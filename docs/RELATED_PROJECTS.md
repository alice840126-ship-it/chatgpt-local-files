# 유사 도구 조사와 반영 — 2026-10-09

GitHub 원문 README와 Reddit 개발자 게시글을 검토했습니다. 비교 도구를 설치하거나 실제 동작을 검증한 결과는 아닙니다. 인기·성능·시장 수요를 입증하는 조사는 아닙니다.

| 프로젝트 | 원문에서 확인한 방향 | 이번 배포에 참고한 점 |
|---|---|---|
| [공식 Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | 파일 읽기·쓰기·편집, 허용 디렉터리 기반 | 파일 접근 범위와 도구를 명시적으로 설명 |
| [Desktop Commander](https://github.com/wonderwhy-er/DesktopCommanderMCP) | 파일·문서·검색·터미널 작업, 페이지/분할 처리 | 작은 구간 수정과 제한값 안내. 전체 경로 접근 자체는 이미 제공되는 기능이므로 독점적 차별점으로 주장하지 않음 |
| [FileMCP](https://github.com/anhnv02/file-mcp) | 선택한 작업 폴더, Secure MCP Tunnel, OS 자격증명 저장소, 네이티브 앱 | 개인 키를 코드에서 분리하고 실제 연결·권한 검증을 설치 단계로 구분 |
| [Local Files MCP](https://github.com/Meteoryte/local-files-mcp) | GUI 설치, 접근 프로필, 로컬 쓰기 승인, 선택적 직접 쓰기 | 설치→연결→실제 쓰기 검증 순서. 본 제품에는 사용자 요청대로 업무 폴더 화이트리스트를 추가하지 않음 |
| [Chat2Local](https://github.com/doguozyigit/Chat2Local) | ChatGPT 채팅에 로컬 파일·스킬·복구 이력 연결 | 복구 이력을 실제 사용 흐름에 포함하고 겹치는 수정은 버전 검사로 감지 |

## Reddit에서 확인한 문제

- [Chat2Local 논의](https://www.reddit.com/r/mcp/comments/1wwaero/i_built_chat2local_an_opensource_mac_app_that/): 여러 채팅이 같은 파일을 다룰 때 이력 분리와 겹치는 변경 문제가 제기됨. 개발자는 자동 충돌 해결이 없다고 설명함.
- [TunnelGPT 논의](https://www.reddit.com/r/mcp/comments/1wxkf9b/tunnelgpt_connecting_a_local_project_folder_to/): 확인 토큰과 실제 사람의 동의는 다르며, 변경 대상과 기록을 명확히 보여줘야 한다는 논의가 있음.
- [RepoRelay 논의](https://www.reddit.com/r/LLMDevs/comments/1w315vi/i_built_a_bridge_that_lets_chatgpt_web_inspect/): 현재 파일 열람과 변경 전 스냅샷·차이 비교의 차이가 논의됨.

## 반영된 내용

- `local_files_status`로 현재 활성 도구, OS 접근 범위, 읽기·쓰기 제한, 복구 정책을 조회할 수 있음. 상태 조회는 실제 권한/터널 성공 증명이 아니라고 반환함.
- 최신 버전 검사, 변경 비교, 보존본 복구는 기존 검증된 엔진을 유지함.
- 스킬은 작은 구간 수정 우선, 실제 사람의 대량 삭제 확인, 오류 뒤 현재 대상·복구본 확인을 안내함.
- 폴더 접근 범위를 제한하지 않되 OS 권한을 우회하지 않는다는 계약을 명확히 함.

외부 코드를 복사·통합하지 않았습니다. 문서에 공개 출처를 연결하고 제품의 사용 흐름을 참고했습니다. 네이티브 GUI 설치, 자동 로그인 실행, PDF/Excel 구조 편집, 대용량 분할 쓰기는 이번 소스 배포에서 제공하지 않습니다. 현재 8 MiB 생성·수정 제한이 있으므로 Codex의 모든 기능/파일 크기와 동등하다고 주장하지 않습니다.
