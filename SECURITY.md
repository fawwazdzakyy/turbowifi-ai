# Security Policy

## Supported Versions
Only the latest major version (1.x) receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability in TurboWiFi AI, please DO NOT open a public issue.
Instead, send an email to fawwaz@example.com. All security vulnerabilities will be promptly addressed.

### Threat Model
TurboWiFi interacts with system-level network configurations via `sudo`. We explicitly defend against:
- Shell injection (using `subprocess` safely with lists, never `shell=True`).
- Path traversal (validating all paths before read/write).
- Privilege escalation via the daemon.
