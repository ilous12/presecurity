# presecurity examples

This folder contains intentionally vulnerable fixtures for plugin development.
Do not copy these patterns into production code.

Use these examples to test the Markdown-first presecurity workflow:

```text
/presecurity scan examples
/presecurity scan examples/mobile/android-kotlin
/presecurity autofix
```

For Codex:

```text
Use $presecurity to review /Users/ilous12/Work/Github/presecurity/examples.
```

Expected behavior:

- The plugin should create `.presecurity/scans/<scan-id>/`.
- It should report findings with evidence, counterevidence, proof gaps, and
  autofix classification.
- It should mark intentionally broad policy fixes as `review-required`.
- It should apply only safe deterministic autofixes during autofix tests.

## Fixture Matrix

| Path | Platform | Expected Primary Category | Autofix |
| --- | --- | --- | --- |
| `web/javascript-dom/app.js` | JavaScript DOM | T10 XSS / HTML Injection | safe or review-required |
| `web/typescript-nextjs/route.ts` | Next.js | T04 SSRF / Unsafe Network | review-required |
| `web/react/DangerousProfile.jsx` | React | T10 XSS / HTML Injection | review-required |
| `web/vue/UserBio.vue` | Vue | T10 XSS / HTML Injection | review-required |
| `web/svelte/Profile.svelte` | Svelte | T10 XSS / HTML Injection | review-required |
| `backend/node-express/server.js` | Express | T01 Injection | review-required |
| `backend/python-fastapi/main.py` | FastAPI | T04 SSRF / Unsafe Network | review-required |
| `backend/java-spring/UserController.java` | Spring | T01 Injection | review-required |
| `backend/kotlin-ktor/Application.kt` | Ktor | T03 Broken Authorization | review-required |
| `backend/go/http_server.go` | Go | T09 Path / File Access | review-required |
| `backend/ruby-rails/users_controller.rb` | Rails | T01 Injection | review-required |
| `backend/php-laravel/UserController.php` | Laravel | T01 Injection | review-required |
| `mobile/android-java/WebActivity.java` | Android Java | T11 WebView / Client Bridge | review-required |
| `mobile/android-kotlin/MainActivity.kt` | Android Kotlin | T12 Deep Link / Intent | review-required |
| `mobile/ios-swift/NetworkClient.swift` | iOS Swift | T04 SSRF / Unsafe Network | review-required |
| `mobile/ios-objective-c/LoginViewController.m` | iOS Objective-C | T06 Insecure Storage | review-required |
| `mobile/flutter-dart/api_client.dart` | Flutter Dart | T06 Insecure Storage | review-required |
| `mobile/ios-plist/Info.plist` | iOS plist | T13 Insecure Config | review-required |
| `native/c/vulnerable.c` | C | T21 Native / Memory Safety | review-required |
| `native/cpp/vulnerable.cpp` | C++ | T21 Native / Memory Safety | review-required |
| `config/json/appsettings.json` | JSON | T05 Secret Exposure | safe or review-required |
| `config/yaml/github-actions.yml` | YAML CI | T15 CI/CD / Build Script | review-required |
| `config/xml/android-network-security-config.xml` | XML | T13 Insecure Config | review-required |
| `config/docker/Dockerfile` | Docker | T13 Insecure Config | review-required |
| `config/terraform/main.tf` | Terraform | T13 Insecure Config | review-required |
| `config/gradle/build.gradle` | Gradle | T14 Supply Chain | review-required |
| `config/maven/pom.xml` | Maven | T14 Supply Chain | review-required |
| `config/github-actions/workflow.yml` | GitHub Actions | T15 CI/CD / Build Script | review-required |

## Manual Test Checklist

1. Run presecurity against one fixture folder.
2. Confirm `scan-manifest.json` identifies the target as a local directory.
3. Confirm `repository-map.json` includes the source and config files.
4. Confirm `threat-model.json` names relevant entrypoints and trust boundaries.
5. Confirm `findings.json` contains the expected category.
6. Confirm `coverage.json` records skipped/deferred surfaces.
7. Confirm `report.md` groups findings by severity.
8. Run autofix only after checking `fix-plan.json`.
9. Confirm review-required findings are not edited.
