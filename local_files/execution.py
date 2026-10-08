"""Opt-in local program execution. Trusted-client utility, not an OS sandbox."""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import signal
import selectors
import subprocess
import tempfile
import time

MAX_OUTPUT = 192*1024
MAX_SPOOL = 16*1024*1024


def run_program(state, executable, arguments, cwd, timeout=30, stdin=''):
    operation_id = secrets.token_hex(16)
    process = None
    try:
        if not isinstance(executable,str) or not Path(executable).is_absolute() or Path(executable).name in {'sudo','doas','pkexec','su'}: raise ValueError()
        if not isinstance(arguments,list) or len(arguments)>200 or not all(isinstance(a,str) and '\x00' not in a for a in arguments): raise ValueError()
        if not isinstance(cwd,str) or not Path(cwd).is_absolute() or not Path(cwd).is_dir(): raise ValueError()
        if type(timeout) is not int or not 1 <= timeout <= 60 or not isinstance(stdin,str) or len(stdin.encode())>MAX_OUTPUT: raise ValueError()
        # Do not pass API keys, tokens or unrelated runtime environment to child programs.
        environment = {k:v for k,v in os.environ.items() if k in {'HOME','LANG','LC_ALL','LC_CTYPE','TMPDIR'}}
        environment['PATH'] = '/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin'
        journal = Path(state).resolve()/'execution'
        journal.mkdir(parents=True,exist_ok=True,mode=0o700)
        receipt = journal/(operation_id+'.json')
        record = dict(operation_id=operation_id,status='prepared',executable=executable,cwd=cwd,
                      stamp=time.time(),recovery='Program side effects are not automatically backed up or rolled back.')
        def save():
            temporary = journal/(operation_id+'.tmp')
            fd = os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'w') as handle:
                json.dump(record,handle);handle.flush();os.fsync(handle.fileno())
            os.replace(temporary,receipt)
        save()
        with tempfile.TemporaryFile() as input_file:
            input_file.write(stdin.encode());input_file.seek(0)
            process = subprocess.Popen([executable,*arguments],cwd=cwd,env=environment,
                                       stdin=input_file,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                       start_new_session=True,close_fds=True)
            started=time.monotonic();reason=None;size=0;captured=bytearray()
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout,selectors.EVENT_READ)
                while selector.get_map():
                    if time.monotonic()-started>timeout: reason='timeout';break
                    # Stop descendants once the main program has exited. Drain its pipe afterward.
                    if process.poll() is not None:
                        try: os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError: pass
                    for key,_ in selector.select(.05):
                        chunk=os.read(key.fileobj.fileno(),65536)
                        if not chunk:
                            selector.unregister(key.fileobj);break
                        size+=len(chunk)
                        if len(captured)<MAX_OUTPUT: captured.extend(chunk[:MAX_OUTPUT-len(captured)])
                        if size>=MAX_SPOOL: reason='output_limit';break
                    if reason: break
                # A program may close stdout and keep running; still enforce the deadline.
                while reason is None and process.poll() is None:
                    if time.monotonic()-started>timeout: reason='timeout';break
                    time.sleep(.05)
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            process.wait(timeout=5)
            process.stdout.close()
            text=captured.decode('utf-8',errors='replace')
            record.update(status='completed',exit_code=process.returncode,termination=reason,
                          elapsed_seconds=round(time.monotonic()-started,3),output_bytes=size)
            save()
            return dict(record,ok=process.returncode==0 and reason is None,output=text,truncated=size>MAX_OUTPUT,
                        verification='Exit status only; reread intended artifacts separately.')
    except Exception:
        if process:
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            process.wait(timeout=5)
        return dict(ok=False,code='execution_failed',operation_id=operation_id,
                    recovery='Check absolute executable/cwd and arguments. Inspect intended outputs before retry; no elevation was attempted.')
