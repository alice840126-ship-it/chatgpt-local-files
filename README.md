# ChatGPT Local Files

**ChatGPT 채팅으로 내 Mac의 파일을 읽고, 만들고, 고치세요.**

Obsidian 노트, 프로젝트 파일, 로컬 폴더, 연결된 외장 SSD를 사용자의 OS 권한 범위에서 관리하는 독립 MCP(도구 연결 규약) 서버입니다. 업무 폴더 화이트리스트를 따로 만들지 않습니다. Codex처럼 실행 사용자에게 OS가 허용한 모든 경로의 일반 파일·폴더를 다루며 텍스트와 바이너리를 지원합니다.

```text
“이 폴더에서 회의록을 찾아 읽어줘.”
“내용을 수정해서 저장하고 다시 읽어 확인해줘.”
“변경 전후를 비교해줘. 이전 버전으로 복구해줘.”
```

파일·문서 작업과 선택적 프로그램 실행을 제공합니다. AI Workspace의 기억 원장·과거 채팅 검색·GitHub 기억 동기화에 의존하지 않습니다. 코드 출처는 [AI Workspace Kit](https://github.com/alice840126-ship-it/ai-workspace-kit)입니다. MIT 라이선스입니다.

## 시작하기

1. [설치·ChatGPT 연결 안내](docs/SETUP.md)에 따라 Mac에 서버를 설치합니다.
2. 본인 계정의 인증된 터널을 연결하고 ChatGPT에서 파일 도구 26개(프로그램 실행을 켜면 27개)가 보이는지 확인합니다.
3. 임시 파일의 생성 → 수정 → 읽기를 실제 ChatGPT 채팅에서 시험합니다.

받는 사람은 자신의 계정·키·터널·OS 권한을 설정합니다. 이 저장소에는 개인 파일, 인증정보, 상태 DB, 다른 사람의 연결 설정이 없습니다. Python 3.11 이상, macOS에서 검증했습니다. Windows 네이티브는 지원하지 않으며 Linux 실기 검증은 하지 않았습니다.

## 도구와 보호 장치

기존 파일 관리에 재개 가능한 분할 쓰기, 빠른 폴더 목록, PDF 텍스트·페이지 선택, DOCX 문단·표 읽기와 서식 구간 수정, XLSX/XLSM 셀 읽기·수정, 실제 이미지 미리보기를 추가했습니다.
`--execution`을 명시하면 제한 시간·출력 한도·프로세스 그룹 정리를 적용한 프로그램 실행도 제공합니다. 실행 도구는 샌드박스가 아니며 프로그램 변경은 파일 복구 이력으로 자동 되돌릴 수 없습니다.
[도구명·크기 제한·복구 한계](docs/TOOLS.md).

수정 전 버전을 검사하고 이전 파일을 같은 볼륨에 보존하며 저장 결과를 재검사합니다. 대량 삭제는 사람의 확인을 요구합니다. 다른 프로그램의 동시 변경을 완전히 잠그는 시스템은 아니며, 경쟁 변경과 중간 실패는 확인이 필요한 결과로 반환합니다.

## 사용 스킬

[`skills/chatgpt-local-files/SKILL.md`](skills/chatgpt-local-files/SKILL.md)는 도구 선택·버전 검사·복구를 안내합니다. Codex에서는 폴더를 자신의 `~/.codex/skills/`에 설치해 사용할 수 있습니다. ChatGPT에서는 먼저 MCP를 연결하고 [채팅용 지침](docs/SETUP.md#채팅용-지침)을 프로젝트 지침에 넣을 수 있습니다. 스킬 파일 자체를 붙여넣는 것만으로 컴퓨터 연결이 생기지는 않습니다.

현재 공개 소스 배포이며 ChatGPT 공식 스토어 등록·모든 계정의 사용 가능 여부를 보장하지 않습니다. 설치 후 실제 쓰기 호출을 확인하세요.

## 개발 검증

```bash
./.venv/bin/python -m unittest discover -s tests
./.venv/bin/chatgpt-local-files-check
```

자체 검사는 임시 폴더에서 실제 MCP subprocess를 실행합니다. 자신의 ChatGPT 계정 연결과 macOS 권한은 별도로 확인합니다. [검증 기록](docs/VALIDATION.md), [보안 범위](SECURITY.md).

[GitHub·Reddit 유사 도구 비교와 참고한 내용](docs/RELATED_PROJECTS.md)을 공개합니다. 단순 파일 연결을 새로운 발명으로 주장하지 않으며 복구·충돌 검증과 실제 사용 편의성을 개선합니다.

## 공통 엔진 구조 (v0.2.0)

이 저장소의 `local_files` 패키지가 파일·문서·실행 기능의 정본입니다. AI Workspace는 같은 패키지의 검증된 커밋을 의존성으로 사용하고 기억·색인 기능만 덧붙입니다. 사용자는 파일 전용 배포와 Workspace 통합 중 필요한 방식을 선택합니다. 코드를 두 벌로 개발하지 않습니다.

대용량 쓰기는 `local_write_begin` → `local_write_chunk` → `local_write_status` → `local_write_commit`이며 최종 교체 전까지 대상 파일은 유지됩니다. 중단은 `local_write_abort`를 사용합니다. 문서 전용 쓰기 결과는 8 MiB, 입력 문서는 32 MiB·30초 제한이 있습니다. 스캔 PDF OCR, Excel 수식 계산, 브라우저 자동 조작과 서명된 Mac 설치 앱은 포함하지 않습니다.
