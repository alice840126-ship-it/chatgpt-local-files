"""Single registration surface shared by standalone and Workspace adapters."""
from __future__ import annotations
import json
import sys
from mcp.types import ToolAnnotations, CallToolResult, ImageContent, TextContent
from .extended import Engine
from .filesystem import register_tools, MAX_INLINE, MAX_READ, MAX_ENTRIES


def register(server, state, *, execution=False):
    engine = Engine(state)
    register_tools(server, state, engine)
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    create = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)
    change = ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=False)

    @server.tool(annotations=read)
    def local_files_status() -> dict:
        """Report actual enabled capabilities and limits, not proof of OS permission or ChatGPT/tunnel success."""
        return dict(ok=True,version='0.2.0',platform=sys.platform,scope='OS-accessible ordinary paths; no folder whitelist; no elevation',
                    python_executable=sys.executable,execution_enabled=execution,tools=27 if execution else 26,
                    limits=dict(inline_write_bytes=MAX_INLINE,read_bytes=MAX_READ,tree_entries=MAX_ENTRIES,
                                document_bytes=32*1024*1024,document_timeout=30,execution_timeout=60),
                    permission_verified=False,tunnel_verified=False,
                    recovery='File tool originals retained locally. Program side effects are NOT automatically recoverable.')

    @server.tool(annotations=read)
    def local_directory_list(path: str, offset: int=0, limit: int=100) -> dict:
        """Page a directory's immediate names without recursively hashing every file. Live pages can shift during external changes."""
        return engine.call('list_directory',path=path,offset=offset,limit=limit)

    @server.tool(annotations=create)
    def local_write_begin(path: str, expected_version: str, total_bytes: int) -> dict:
        """Begin resumable large text/binary file replacement with retained original. Declared byte count and current target version required. Does not change target until commit."""
        return engine.call('write_begin',path=path,expected_version=expected_version,total_bytes=total_bytes)

    @server.tool(annotations=create)
    def local_write_chunk(upload_id: str, offset: int, content: str, encoding: str='base64') -> dict:
        """Send UTF-8/base64 chunk <=8 MiB at exact next_offset. Identical acknowledged chunk retries are idempotent. Stage only; not a committed file."""
        return engine.call('write_chunk',upload_id=upload_id,offset=offset,content=content,encoding=encoding)

    @server.tool(annotations=read)
    def local_write_status(upload_id: str) -> dict:
        """Read resumable upload offset/status; prepared is not committed success."""
        return engine.call('write_status',upload_id=upload_id)

    @server.tool(annotations=change)
    def local_write_commit(upload_id: str) -> dict:
        """Verify staged chunk hashes and original target version, atomically commit, retain original and reread. Conflicts leave the target untouched before commit; inspect_required needs inspection."""
        return engine.call('write_commit',upload_id=upload_id)

    @server.tool(annotations=change)
    def local_write_abort(upload_id: str) -> dict:
        """Discard an uncommitted upload's staging data only. Refuse if commit started. Does not remove target or retained committed originals."""
        return engine.call('write_abort',upload_id=upload_id)

    @server.tool(annotations=read)
    def local_document_read(path: str, options: dict|None=None) -> dict:
        """Extract PDF pages, DOCX paragraphs/tables, or XLSX/XLSM cells. PDF/DOCX offset+limit; Excel sheet+range (e.g. A1:J50). Returns current version. No OCR, formula recalculation or macro execution."""
        return engine.call('document',path=path,options=options)

    @server.tool(annotations=create)
    def local_docx_create(path: str, paragraphs: list[str]) -> dict:
        """Create a DOCX from paragraphs at a missing path; reread actual document. No existing file overwrite."""
        return engine.call('document',path=path,action='docx_create',expected_version='missing',options=dict(paragraphs=paragraphs))

    @server.tool(annotations=change)
    def local_docx_replace(path: str, expected_version: str, old_text: str, new_text: str) -> dict:
        """Replace one unique DOCX text occurrence within one formatting run, including table cells; preserve run formatting. Reject cross-run/ambiguous matches, retain original and reread."""
        return engine.call('document',path=path,action='docx_replace',expected_version=expected_version,options=dict(old_text=old_text,new_text=new_text))

    @server.tool(annotations=change)
    def local_spreadsheet_write(path: str, expected_version: str, cells: dict, sheet: str|None=None) -> dict:
        """Create/update XLSX/XLSM cells by coordinate, preserving original for recovery. expected_version=missing creates XLSX. Up to 10000 cells; scalar values/formula strings. No formula calculation or macro execution; unsupported features may change."""
        options=dict(cells=cells)
        if sheet is not None: options['sheet']=sheet
        return engine.call('document',path=path,action='xlsx_write',expected_version=expected_version,options=options)

    @server.tool(annotations=change)
    def local_pdf_select_pages(path: str, expected_version: str, pages: list[int]) -> dict:
        """Replace a PDF with chosen/reordered 1-based pages. Original retained. Document signatures/forms/metadata may be invalidated; explain this before a requested edit."""
        return engine.call('document',path=path,action='pdf_pages',expected_version=expected_version,options=dict(pages=pages))

    @server.tool(annotations=read)
    def local_image_preview(path: str) -> CallToolResult:
        """Return actual local image pixels as MCP ImageContent, bounded 1600px preview with version metadata. First frame only; not raw base64 masquerading as understanding."""
        result=engine.call('document',path=path)
        data=result.pop('image',None)
        contents=[TextContent(type='text',text=json.dumps(result,ensure_ascii=False))]
        if data: contents.append(ImageContent(type='image',data=data,mimeType='image/png'))
        return CallToolResult(content=contents,isError=not result.get('ok',False))

    if execution:
        @server.tool(annotations=ToolAnnotations(readOnlyHint=False,destructiveHint=True,openWorldHint=True))
        def local_program_run(executable: str, arguments: list[str], cwd: str, timeout: int=30, stdin: str='') -> dict:
            """Run an explicitly user-authorized local program, absolute executable/cwd, no shell=True and no elevation. Optional explicit shell/interpreter can execute code: trusted-client utility, NOT a sandbox. Do not use commands to bypass file deletion confirmations or OS permissions. Request human confirmation before destructive/nonrecoverable actions or unauthorized external effects. Timeout <=60s, output capped; descendants in process group stopped on completion. No credentials injected. Exit 0 is not file/artifact verification; reread intended outputs."""
            from .execution import run_program
            return run_program(state,executable,arguments,cwd,timeout,stdin)

    return engine
