# Supported platforms

presecurity is designed for general-purpose codebases. The implementation
surface is Markdown guidance for the host coding agent, not a language-specific
runtime.

## Web

Supported:

- JavaScript
- TypeScript
- React
- Next.js
- Vue
- Svelte

Review focus:

- XSS and unsafe HTML rendering
- server-side request flows and SSRF
- route handlers and server actions
- auth/session checks
- secrets in client bundles
- unsafe redirects
- prototype pollution and dependency risk

## Backend

Supported:

- Node.js
- Python
- Java
- Kotlin
- Go
- Ruby
- PHP

Review focus:

- injection
- broken auth
- broken authorization
- tenant isolation
- file upload and path traversal
- deserialization
- unsafe outbound network requests
- logging and error leaks
- rate limit and resource abuse gaps

## Mobile

Supported:

- Java
- Kotlin
- Swift
- Objective-C
- Dart
- plist

Review focus:

- Android manifest exported components
- Android cleartext traffic and network security config
- WebView JavaScript bridge risk
- intent extras and deep links
- iOS ATS exceptions
- Keychain and local storage
- Flutter platform channels
- Firebase and mobile config exposure

## Native

Supported:

- C
- C++

Review focus:

- bounds checks
- unsafe string and memory functions
- integer overflow
- use-after-free
- format string risk
- unsafe file and IPC handling

## Config, Build, and Supply Chain

Supported:

- JSON
- YAML
- XML
- plist
- Dockerfile
- Terraform
- Gradle
- Maven
- GitHub Actions
- generic CI configuration

Review focus:

- secrets in configuration
- debug and permissive flags
- overbroad permissions
- untrusted CI execution
- dependency confusion
- unsafe install hooks
- unsigned release paths
- public storage and network exposure
