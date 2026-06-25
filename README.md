# presecurity

![presecurity logo](assets/presecurity-logo.png)

presecurity는 Claude Code와 Codex Desktop에서 사용하는 **코딩 에이전트용 보안 점검 플러그인**입니다.

에이전트가 만든 코드를 그대로 믿기 전에, 위험한 패턴을 먼저 확인하고 안전한 수정만 자동으로 적용하도록 돕습니다. 개발자는 `/presecurity scan`으로 문제를 확인하고, `/presecurity autofix`로 확실한 항목만 정리할 수 있습니다.

> English: presecurity is a lightweight security plugin for coding agents. It reviews agent-written code, explains risk, creates a remediation plan, and applies only safe deterministic fixes.

## 지원 커맨드

presecurity는 다섯 개의 커맨드를 지원합니다.

```text
/presecurity init
/presecurity scan
/presecurity autofix
/presecurity cleanup
/presecurity doctor
```

### 1. `/presecurity init`

현재 프로젝트에 presecurity 관리 폴더를 만듭니다.

```text
.presecurity/
  config.json
  history.jsonl
  scan-plan.json
```

처음 한 번만 실행하면 됩니다.

### 2. `/presecurity scan`

프로젝트를 스캔하고 보안 이슈를 찾습니다.

스캔 결과에는 다음 정보가 포함됩니다.

- 어떤 파일과 라인에서 문제가 발견됐는지
- OWASP Top 10 중 어떤 유형인지
- 위험도와 신뢰도
- 어떤 영향이 있을 수 있는지
- 어떤 순서로 수정하면 좋은지
- 자동 수정 가능한 항목인지
- 명백한 placeholder/test fixture 등 사전 제외된 오탐 후보가 몇 개인지
- 최근 변경 diff에서 보안상 민감한 영역이 있는지

결과는 여기에 저장됩니다.

```text
.presecurity/scan-plan.json
```

실행 중에는 터미널에 진행바가 표시됩니다.

```text
[############------------] 2/4 오탐 후보 제외 및 규칙 검사
```

### 3. `/presecurity autofix`

마지막 scan 결과를 기준으로, 수정 계획에 있는 항목을 순서대로 자동 수정합니다.
수동 처리 요청은 만들지 않습니다. 명확한 치환이 가능한 항목은 코드로 고치고, 패키지 설치가 필요한 수정은 마지막에 모아서 한 번에 처리합니다.

예:

- `yaml.load(` → `yaml.safe_load(`
- `debug=True` → `debug=False`
- `.innerHTML =` → `.textContent =`
- `verify=False` → `verify=True`
- `privileged: true` → `privileged: false`
- `dangerouslySetInnerHTML` → `DOMPurify.sanitize(...)`
- `document.write(...)` → text node 삽입
- 하드코딩된 credential-like 값 → 빈 값으로 치환
- `NEXT_PUBLIC_*SECRET*` → 서버 전용 변수명으로 치환
- `.html_safe` 제거

자동 수정 후 다시 스캔해서 남은 이슈를 확인합니다. 진행 중에는 각 파일/라인별 적용 상태가 진행바로 표시됩니다.

### 4. `/presecurity cleanup`

프로젝트에서 presecurity 관리 파일을 삭제합니다.

```text
.presecurity/
```

플러그인을 더 이상 쓰지 않거나, 스캔 이력을 지우고 싶을 때 사용합니다.

### 5. `/presecurity doctor`

presecurity가 현재 프로젝트에서 제대로 동작할 수 있는지 점검합니다.

확인하는 항목:

- Python 런타임
- git 설치 여부
- 현재 폴더가 git repository인지
- `.presecurity/` 초기화 여부
- `config.json`, `history.jsonl`, `scan-plan.json` 존재 여부
- 내장 룰과 지원 플랫폼 정보

처음 설치한 뒤 문제가 있는지 확인하고 싶을 때 사용합니다.

## 왜 필요한가요?

코딩 에이전트는 빠르게 코드를 만들어주지만, 가끔 다음과 같은 보안 실수를 만들 수 있습니다.

- 사용자 입력을 그대로 `eval`, shell command, SQL query에 넣는 코드
- `innerHTML`, `dangerouslySetInnerHTML` 같은 XSS 위험 코드
- `yaml.load`, `pickle.load` 같은 위험한 역직렬화
- 하드코딩된 API key, token, password
- TLS 검증 비활성화
- Docker, Kubernetes, Terraform, GitHub Actions 설정 실수

presecurity는 이런 문제를 **OWASP Top 10 기준으로 분류**하고, 파일/라인/영향도/수정 방향을 `.presecurity/scan-plan.json`에 기록합니다.

## 설치

### Claude Code

Claude Code에서 이 GitHub 저장소를 플러그인 마켓플레이스로 추가합니다.

```text
/plugin marketplace add https://github.com/ilous12/presecurity
```

그 다음 `presecurity`를 설치합니다.

```text
/plugin install presecurity@presecurity-marketplace
```

### Codex Desktop / Codex CLI

Codex에서는 이 저장소를 플러그인 마켓플레이스로 추가한 뒤 설치합니다.

```bash
codex plugin marketplace add ilous12/presecurity --ref main --sparse .agents/plugins --sparse plugins/codex/presecurity
codex plugin add presecurity@presecurity
```

자세한 설치 흐름은 [docs/install-from-github.md](docs/install-from-github.md)를 참고하세요.

## 일반 사용 흐름

처음 사용하는 프로젝트에서는 이렇게 시작합니다.

```text
/presecurity init
/presecurity scan
```

스캔 결과를 보고, 안전한 자동 수정을 적용하고 싶으면 다음을 실행합니다.

```text
/presecurity autofix
```

다시 확인합니다.

```text
/presecurity scan
```

정리하고 싶을 때는 다음을 실행합니다.

```text
/presecurity cleanup
```

설치나 초기화 상태를 확인하고 싶으면 다음을 실행합니다.

```text
/presecurity doctor
```

## 현재 지원 범위

- OWASP Top 10 기반 경량 SAST
- JavaScript / TypeScript / React / Next.js
- Node.js / Express / NestJS
- Python / Django / FastAPI / Flask
- Java / Spring
- Go
- Ruby on Rails
- PHP / Laravel
- Docker / Kubernetes / Terraform
- GitHub Actions
- 안전한 일부 autofix
- git diff 기반 변경 의도 요약

## 한계

presecurity는 개발 중 빠르게 위험 신호를 잡기 위한 보조 도구입니다.

다음을 완전히 대체하지 않습니다.

- 전문 SAST
- DAST
- dependency scanning
- secret scanning 전용 도구
- 보안 전문가의 코드 리뷰
- 모의해킹

## English quick start

Install from Claude Code:

```text
/plugin marketplace add https://github.com/ilous12/presecurity
/plugin install presecurity@presecurity-marketplace
```

Install from Codex:

```bash
codex plugin marketplace add ilous12/presecurity --ref main --sparse .agents/plugins --sparse plugins/codex/presecurity
codex plugin add presecurity@presecurity
```

Commands:

```text
/presecurity init
/presecurity scan
/presecurity autofix
/presecurity cleanup
/presecurity doctor
```

Command meanings:

- `init`: create `.presecurity/` state files.
- `scan`: scan the project, exclude common false-positive placeholders/fixtures, and write file, line, evidence, impact, and fix plan data to `.presecurity/scan-plan.json`.
- `autofix`: apply automatic fixes without manual handoff, batch package installs at the end, then rescan.
- `cleanup`: remove `.presecurity/`.
- `doctor`: check runtime, git, state files, rules, and platform support.

## License

MIT License. See [LICENSE](LICENSE).
