# ChatGPT Local Files

**ChatGPT 채팅으로 내 Mac의 파일을 읽고, 만들고, 고치세요.**

Obsidian 노트, 프로젝트 파일, 로컬 폴더, 연결된 외장 SSD를 사용자의 OS 권한 범위에서 관리하는 독립 MCP(도구 연결 규약) 서버입니다. 업무 폴더 화이트리스트를 따로 만들지 않습니다. Codex처럼 실행 사용자에게 OS가 허용한 모든 경로의 일반 파일·폴더를 다루며 텍스트와 바이너리를 지원합니다.

```text
“이 폴더에서 회의록을 찾아 읽어줘.”
“내용을 수정해서 저장하고 다시 읽어 확인해줘.”
“변경 전후를 비교해줘. 이전 버전으로 복구해줘.”
```

파일 관리만 제공합니다. AI Workspace의 기억 원장·과거 채팅 검색·GitHub 기억 동기화에 의존하지 않습니다. 코드 출처는 [AI Workspace Kit](https://github.com/alice840126-ship-it/ai-workspace-kit)입니다. MIT 라이선스입니다.

## 시작하기

1. [설치·ChatGPT 연결 안내](docs/SETUP.md)에 따라 Mac에 서버를 설치합니다.
2. 본인 계정의 인증된 터널을 연결하고 ChatGPT에서 파일 도구 14개가 보이는지 확인합니다.
3. 임시 파일의 생성 → 수정 → 읽기를 실제 ChatGPT 채팅에서 시험합니다.

받는 사람은 자신의 계정·키·터널·OS 권한을 설정합니다. 이 저장소에는 개인 파일, 인증정보, 상태 DB, 다른 사람의 연결 설정이 없습니다. Python 3.11 이상, macOS에서 검증했습니다. Windows 네이티브는 지원하지 않으며 Linux 실기 검증은 하지 않았습니다.

## 도구와 보호 장치

쓰기 8개: 생성, 전체 수정, 구간 수정, 폴더 생성, 복사, 이동·이름 변경, 복구 가능한 삭제, 복구.
읽기 6개: 접근 범위·제한 상태, 파일 상태·해시, 원문, 파일 검색, 작업 이력, 변경 비교.
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
