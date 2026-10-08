# v0.2.0 ChatGPT 실호출 확인 — 2026-10-09

운영 중인 기존 AI Workspace Local Search 연결에 공통 엔진을 적용하고 ChatGPT의 도구 목록을 새로고침했습니다. 실제 채팅에서 `local_files_status`가 version=0.2.0, execution_enabled=true를 반환했고, 텍스트 생성 → 버전 확인 수정 → 독립 재읽기, Word 생성 → 문서 재읽기, `local_program_run`의 printf 실행이 성공했습니다. 테스트 파일 내용·SHA256과 실행 작업 기록을 Mac에서 별도로 대조했습니다. 일반 로컬 파일 호출이 외장 SSD로 연결된 테스트 출력 위치에서도 동작했습니다.

이 검증은 기존 소유 계정과 기존 연결의 성공입니다. 다른 사용자의 새 연결, 모든 macOS 보호 폴더의 권한, 음성 모드 성공을 뜻하지 않습니다. Workspace의 기존 기억·검색 4개를 포함한 활성 도구는 31개이며 공통 엔진 상태의 27개는 파일·문서·실행 도구만 센 값입니다.

공통 엔진 회귀 31개, 원래 Workspace 132개, 배포 Workspace Kit 136개가 통과했습니다. 설치된 패키지를 별도 프로세스로 호출해 공통 엔진 27개와 Kit 30개 도구 및 생성·수정·재읽기·충돌 거부·삭제·복구를 검증했고 의존성 검사도 통과했습니다. 독립 검토에서 문서 저장 관련 3개 문제를 수정하고 회귀 검사했습니다.

# v0.2.0 확장 검증 — 2026-10-09

기존 파일 검증에 대용량 재개·원본 복구·충돌·업로드 변조·기록 실패 재시도, 실제 PDF/Word/Excel 처리, MCP 이미지 전달, 실행 비밀 환경 차단·시간 제한·출력 제한을 추가했습니다. 문서 저장 후 버전 불일치, Excel 문자열 잘림, Word 서식 경계의 모호한 치환도 회귀 검증합니다.

공통 엔진은 local_files 패키지 하나이며 Workspace 어댑터는 같은 검증 커밋을 사용합니다. 기존 도구 노출과 기억·검색은 별도로 회귀 확인합니다. 이 기록의 과거 버전 수치는 아래 이전 배포에 해당합니다. 새 계정의 ChatGPT 연결·OS 권한은 별도 실호출이 필요합니다.

# Validation — 2026-10-09

This standalone package inherits the tested filesystem engine from AI Workspace Kit. It excludes memory, artifact indexing, checkpoints, publication, native chat history and live deployment configuration.

- macOS / Python 3.14.5 / MCP SDK 2.2.0.
- The 17 filesystem regression tests cover version conflicts, same-size/mtime edits, no-clobber, binary/UTF-8 reads, directory operations, bulk-delete confirmation binding, concurrent calls, macOS metadata, retained race bytes and failed journal completion.
- A fresh non-editable installation runs outside the checkout. The installed self-check starts a real stdio MCP subprocess and verifies 27 tools with explicit execution enabled (26 without it), create → edit → actual reread → stale-version rejection → recoverable delete → restore.
- The skill frontmatter is validated separately; independent review examines tool routing, stale conflict and human confirmation boundaries.
- Source and committed history are scanned for secrets before publication.

No new standalone-package ChatGPT registration, recipient OS permission grant, physical SSD test, login service or voice call is claimed. The original engine had live ChatGPT file operations; this establishes lineage, not a new user's connection success. Follow SETUP.md and test an actual chat on your own account.

The root plugin manifest packages the reusable skill. It does not bundle a working per-user tunnel connection: each recipient must register their own MCP. GitHub source publication is separate from public ChatGPT directory approval.
