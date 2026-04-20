# mateo627

## Security

This repository includes automated GitHub Actions security checks on every push and pull request:

- **Dependency vulnerability scan:** Trivy scans dependencies and fails the build when **HIGH** or **CRITICAL** vulnerabilities are present.
- **Static analysis/security lints:** Semgrep runs the `p/security-audit` ruleset and fails the build on **ERROR** severity findings.
- **Secret scanning:** Gitleaks scans commits/PR changes and fails the build if any leaked secrets are detected.

Machine-readable reports are uploaded as workflow artifacts (`trivy-dependencies.json`, `semgrep.json`, and `gitleaks.sarif`).

### Run the same checks locally

From the repository root:

```bash
# Dependency vulnerability scan (HIGH/CRITICAL in JSON)
docker run --rm -v "$(pwd):/src" aquasec/trivy:latest fs --vuln-type library --format json -o /src/trivy-dependencies.json /src
jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH" or .Severity == "CRITICAL")] | length' trivy-dependencies.json

# Static analysis / security lint
python3 -m pip install --upgrade pip
pip install semgrep
semgrep scan --config p/security-audit --json --output semgrep.json .
jq '[.results[]? | select(.extra.severity == "ERROR")] | length' semgrep.json

# Secret scanning
docker run --rm -v "$(pwd):/repo" zricethezav/gitleaks:latest detect --source /repo --report-format sarif --report-path /repo/gitleaks.sarif --exit-code 1
```

### Reporting vulnerabilities

Please **do not** open public issues for security vulnerabilities.

Instead, report vulnerabilities privately to the maintainers (for example, via your organization’s private security contact channel), and include:

- A clear description of the issue and impact.
- Steps to reproduce.
- Any proof-of-concept or logs needed to validate the finding.
- Suggested remediation (if available).
