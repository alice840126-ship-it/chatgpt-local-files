"""Shared extension engine: resumable writes, listing, and document commits."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from .filesystem import (Filesystem, MAX_INLINE, MAX_READ, RECOVERY_PREFIX,
                         snapshot, fail, copy_metadata, rename_atomic, digest)


class Engine(Filesystem):
    def list_directory(self, path, offset=0, limit=100):
        if type(offset) is not int or type(limit) is not int or offset < 0 or not 1 <= limit <= 500:
            raise ValueError()
        target = self.path(path, mutation=False)
        if not target.is_dir() or target.is_symlink(): raise ValueError()
        entries = sorted(target.iterdir(), key=lambda item: item.name)
        result = []
        for item in entries[offset:offset+limit]:
            info = item.lstat()
            result.append(dict(path=str(item), name=item.name, bytes=info.st_size,
                               kind='symlink' if item.is_symlink() else 'directory' if stat.S_ISDIR(info.st_mode) else 'file'))
        return dict(ok=True, entries=result, next_offset=offset+len(result), total=len(entries),
                    truncated=offset+len(result)<len(entries), consistency='Live listing; concurrent changes can shift pages.')

    def write_begin(self, path, expected_version, total_bytes):
        if type(total_bytes) is not int or total_bytes < 0: raise ValueError()
        target = self.path(path)
        before = self.expect(target, expected_version)
        if before['kind'] not in ('file', 'missing'): raise ValueError()
        info = os.statvfs(target.parent)
        if total_bytes > info.f_bavail * info.f_frsize:
            fail('disk_full', 'Free enough space for the complete staged file and retained original.')
        record = self.begin('write', path=str(target), before=before, total_bytes=total_bytes,
                            next_offset=0, chunks=[], upload=True)
        stage = target.parent / (RECOVERY_PREFIX + record['operation_id'])
        record['backup'] = str(stage)
        self.save(record)
        fd = os.open(stage, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        try:
            os.fsync(fd)
            info = os.fstat(fd)
            record['stage_identity'] = [info.st_dev, info.st_ino]
        finally: os.close(fd)
        self.save(record)
        return dict(ok=True, upload_id=record['operation_id'], next_offset=0,
                    total_bytes=total_bytes, committed=False)

    def upload(self, upload_id):
        record = self.load(upload_id)
        if not record.get('upload'): raise ValueError()
        if record['status'] != 'prepared' or record.get('commit_started'):
            fail('upload_not_writable', 'Inspect history/current file; commit may already have started.',
                 status=record['status'])
        self.active = record
        return record

    def stage_fd(self, record, flags):
        fd = os.open(record['backup'], flags | os.O_NOFOLLOW | os.O_NONBLOCK)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or [info.st_dev, info.st_ino] != record.get('stage_identity'):
            os.close(fd)
            fail('stage_changed', 'Do not modify upload staging files. Inspect history before restarting.')
        return fd

    def write_chunk(self, upload_id, offset, content, encoding='base64'):
        record = self.upload(upload_id)
        data = self.decode(content, encoding)
        if type(offset) is not int or offset < 0 or not data: raise ValueError()
        if offset < record['next_offset']:
            matching = next((c for c in record['chunks'] if c[0] == offset), None)
            if matching == [offset, len(data), digest(data)]:
                return dict(ok=True, upload_id=upload_id, next_offset=record['next_offset'], duplicate=True)
            fail('chunk_conflict', 'Resume at returned next_offset; never replace acknowledged chunks.')
        if offset != record['next_offset'] or offset+len(data) > record['total_bytes']:
            fail('chunk_offset', 'Use the exact next_offset and stay within declared total_bytes.', next_offset=record['next_offset'])
        fd = self.stage_fd(record, os.O_RDWR)
        try:
            size = os.fstat(fd).st_size
            if size == offset:
                os.lseek(fd, offset, os.SEEK_SET)
                view = memoryview(data)
                while view:
                    written = os.write(fd, view); view = view[written:]
                os.fsync(fd)
            elif size == offset+len(data):
                # Resume a fsynced chunk whose receipt was interrupted.
                os.lseek(fd, offset, os.SEEK_SET)
                if os.read(fd, len(data)) != data: fail('chunk_conflict', 'Inspect the unacknowledged staging chunk.')
            else: fail('stage_size_changed', 'Inspect staging data; no truncation was attempted.')
        finally: os.close(fd)
        record['chunks'].append([offset, len(data), digest(data)])
        record['next_offset'] += len(data)
        self.save(record)
        return dict(ok=True, upload_id=upload_id, next_offset=record['next_offset'], committed=False)

    def write_status(self, upload_id):
        record = self.load(upload_id)
        if not record.get('upload'): raise ValueError()
        return dict(ok=True, upload_id=upload_id, status=record['status'],
                    next_offset=record['next_offset'], total_bytes=record['total_bytes'],
                    commit_started=record.get('commit_started', False))

    def write_commit(self, upload_id):
        record = self.upload(upload_id)
        if record['next_offset'] != record['total_bytes']:
            fail('upload_incomplete', 'Send remaining chunks before commit.', next_offset=record['next_offset'])
        fd = self.stage_fd(record, os.O_RDONLY)
        hashed = hashlib.sha256()
        try:
            if os.fstat(fd).st_size != record['total_bytes']: raise ValueError()
            for offset, size, expected in record['chunks']:
                data = os.read(fd, size)
                if digest(data) != expected: fail('stage_changed', 'A staged chunk changed; inspect before restarting.')
                hashed.update(data)
        finally: os.close(fd)
        target = Path(record['path']); stage = Path(record['backup'])
        self.expect(target, record['before']['version'])
        if record['before']['kind'] == 'file': copy_metadata(target, stage)
        record['intended_sha256'] = hashed.hexdigest()
        record['commit_started'] = True
        self.save(record)
        rename_atomic(stage, target, swap=record['before']['kind']=='file')
        if record['before']['kind'] == 'file' and snapshot(stage)['version'] != record['before']['version']:
            fail('commit_race_preserved', 'Latest displaced data retained; inspect both paths.', recovery_path=str(stage))
        after = snapshot(target)
        if after['sha256'] != record['intended_sha256']:
            fail('post_write_conflict', 'Inspect current target and retained original.')
        return self.finish(record, after)

    def write_abort(self, upload_id):
        record = self.upload(upload_id)
        fd = self.stage_fd(record, os.O_RDONLY)
        os.close(fd)
        Path(record['backup']).unlink()
        record['status'] = 'aborted'
        self.save(record)
        return dict(ok=True, upload_id=upload_id, aborted=True, target_changed=False)

    def document(self, path, action='read', expected_version=None, options=None):
        target = self.path(path, mutation=action!='read')
        before = snapshot(target) if action=='read' else self.expect(target, expected_version)
        if before['kind'] not in (('file',) if action=='read' else ('file','missing')): raise ValueError()
        if before['bytes'] > 32*1024*1024:
            fail('document_size_limit', 'Use program execution for documents larger than 32 MiB.')
        request = json.dumps(dict(path=str(target), action=action, options=options or {})).encode()
        # Parsing is isolated from the long-lived MCP; malformed archives cannot hang it indefinitely.
        try:
            run = subprocess.run([sys.executable, '-m', 'local_files.document_worker'], input=request,
                                 capture_output=True, timeout=30)
        except subprocess.TimeoutExpired:
            fail('document_timeout', 'Document processing exceeded 30 seconds; try fewer pages or rows.')
        if run.returncode:
            fail('document_worker_failed', 'Inspect document format or installed dependencies; no target change attempted.')
        result = json.loads(run.stdout)
        if not result.get('ok'): return result
        if action=='read':
            self.expect(target, before['version'])
            return dict(result, version=before['version'], path=str(target))
        encoded = result.pop('binary')
        saved = self.write(str(target), encoded, before['version'], encoding='base64')
        # Parse the actual committed file rather than claiming that serialization implies correctness.
        reread = self.document(str(target), options=result.get('verify_options', {}))
        if not reread.get('ok'): fail('document_verification_failed', 'Inspect operation receipt and retained original.', operation_id=saved['operation_id'])
        if reread.get('version') != saved['after']['version']:
            fail('post_write_conflict', 'Another program changed the committed document; inspect current and retained originals.', operation_id=saved['operation_id'])
        return dict(saved, document=reread, warnings=result.get('warnings', []))
