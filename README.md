# presecurity

presecurity는 Claude Code와 Codex Desktop에서 사용하는 **코딩 에이전트용 보안 점검 플러그인**입니다.

개발자가 에이전트에게 코드를 만들거나 수정하게 한 뒤, 바로 `/presecurity scan`을 실행하면 위험한 코드 패턴을 찾아주고, `/presecurity autofix`로 안전하게 바꿀 수 있는 항목만 자동 수정합니다.

> English: presecurity is a lightweight security plugin for coding agents. It scans agent-written code, creates a remediation plan, and applies only safe deterministic fixes.

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

## 지원 커맨드

presecurity는 네 개의 커맨드만 지원합니다.

```text
/presecurity init
/presecurity scan
/presecurity autofix
/presecurity cleanup
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
- 최근 변경 diff에서 보안상 민감한 영역이 있는지

결과는 여기에 저장됩니다.

```text
.presecurity/scan-plan.json
```

### 3. `/presecurity autofix`

마지막 scan 결과를 기준으로, 안전하게 자동 수정할 수 있는 항목만 순서대로 수정합니다.

예:

- `yaml.load(` → `yaml.safe_load(`
- `debug=True` → `debug=False`
- `.innerHTML =` → `.textContent =`
- `verify=False` → `verify=True`
- `privileged: true` → `privileged: false`

자동 수정 후 다시 스캔해서 남은 이슈를 확인합니다.

### 4. `/presecurity cleanup`

프로젝트에서 presecurity 관리 파일을 삭제합니다.

```text
.presecurity/
```

플러그인을 더 이상 쓰지 않거나, 스캔 이력을 지우고 싶을 때 사용합니다.

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

## 직접 실행

플러그인 없이 저장소에서 직접 실행할 수도 있습니다.

```bash
python3 -m presecurity init
python3 -m presecurity scan
python3 -m presecurity autofix
python3 -m presecurity cleanup
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
```

Command meanings:

- `init`: create `.presecurity/` state files.
- `scan`: scan the project and write `.presecurity/scan-plan.json`.
- `autofix`: apply safe deterministic fixes, then rescan.
- `cleanup`: remove `.presecurity/`.

## License

MIT License. See [LICENSE](LICENSE).
