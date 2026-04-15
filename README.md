# mateo627

Security-focused FastAPI project scaffold with explicit entry points, trust boundaries, and static review notes.

## Project structure

```text
/workspace/mateo627
├── app/
│   ├── config.py           # Environment/config loading
│   ├── db.py               # SQLAlchemy engine/session wiring
│   ├── main.py             # API bootstrap + health endpoint
│   ├── models.py           # ORM models
│   ├── schemas.py          # Request/response validation schemas
│   ├── security.py         # Password/JWT primitives
│   └── routers/
│       └── auth.py         # Registration/login routes
├── data/                   # Local sqlite files (gitignored)
├── .env.example            # Runtime config template
├── pyproject.toml          # Build + dependency manifest
├── requirements.txt        # Runtime pinned dependency list
└── requirements-dev.txt    # Dev/static-analysis dependencies
```

## Runtime

1. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements-dev.txt`
2. Create `.env` from `.env.example` and set a high-entropy `JWT_SECRET_KEY`.
3. Run:
   - `uvicorn app.main:app --reload`

## Entry points and trust boundaries

### HTTP entry points

- `GET /health` in `app/main.py`.
- `POST /auth/register` in `app/routers/auth.py`.
- `POST /auth/login` in `app/routers/auth.py`.

### Configuration entry points

- Environment variables and optional `.env` values are loaded through `app/config.py`.
- `DATABASE_URL` and `JWT_SECRET_KEY` are the highest-impact config values.

### Persistence / data sinks

- SQLite (or configured SQLAlchemy backend) through `app/db.py` and `app/models.py`.
- JWT creation/signing via `app/security.py`.

## Threat model (baseline)

### Assets

- User credentials (plaintext in transit, hashed at rest).
- JWT signing secret and issued tokens.
- User table and authentication state.

### Primary attackers

- Internet-originated unauthenticated clients trying credential stuffing, brute force, and malformed JSON payloads.
- Insider or CI/CD misconfiguration leaking `.env` and secret values.
- Dependency-chain attackers exploiting known CVEs in auth/crypto/web dependencies.

### Trust boundaries

- Boundary A: external client input -> FastAPI request models.
- Boundary B: app process -> environment/runtime config.
- Boundary C: app -> database engine.
- Boundary D: app -> token consumers (downstream services if JWT is reused).

### Assumptions

- TLS termination exists upstream (reverse proxy or platform edge).
- Secret injection is handled by environment, not committed files.
- Default sqlite is for local/dev only.

## Static security review (file-by-file patching map)

The items below are intentionally written so fixes can be applied surgically by file.

### 1) Input handling and deserialization points

- **`app/schemas.py`**: Uses typed Pydantic models and strict length/pattern constraints for `username` and `password`; this is good baseline validation.
  - **Patch next if needed**: add custom password complexity validator and deny common-password list.
- **`app/routers/auth.py`**: Request bodies are deserialized via `UserRegister`/`UserLogin`; no direct `dict` parsing.
  - **Residual risk**: no request rate limiting or captcha on auth endpoints.

### 2) Authentication/session logic

- **`app/security.py`**: Bcrypt password hashing and constant-time verify via Passlib; JWT `exp` enforced by JOSE decode.
- **`app/routers/auth.py`**: Issues bearer token on registration/login.
  - **Findings**:
    - No account lockout or failed-attempt throttling.
    - No refresh token / revocation strategy.
    - Registration auto-logins user; acceptable for many apps but should be explicit policy.

### 3) Secrets management and credential loading

- **`app/config.py` + `.env.example`**:
  - `.env` loading is explicit and local-friendly.
  - `jwt_secret_key` has an insecure default (`insecure-change-me`) for bootstrapping.
  - **Required hardening before production**:
    - Fail startup if `JWT_SECRET_KEY` is default or weak.
    - Add secret rotation strategy and KMS/secret manager integration.

### 4) Database query construction and command execution

- **`app/routers/auth.py`**: Uses SQLAlchemy `select(User).where(...)`; no string-concatenated SQL.
- **`app/db.py`**: Uses SQLAlchemy engine/session without raw shell command execution.
  - **Residual risk**: missing DB transaction retry/backoff and migration tooling.

### 5) Dependency versions and lockfiles

- **`pyproject.toml` / `requirements.txt` / `requirements-dev.txt`**:
  - Direct dependencies are pinned to exact versions to reduce drift.
  - **Finding**: no generated lockfile with transitive pins/hashes yet.
  - **Patch recommendation**:
    - Add `pip-tools` (`requirements.lock` with hashes) or `uv.lock` and enforce in CI.
    - Run `pip-audit` and `bandit` in CI on each merge.

## Security hardening backlog (priority order)

1. Enforce non-default `JWT_SECRET_KEY` at startup in `app/config.py`.
2. Add rate limiting/brute-force protections in `app/routers/auth.py`.
3. Add refresh token + revocation list in `app/security.py` and auth router.
4. Introduce migration system (Alembic) for schema control.
5. Add lockfile + CI security scanning gates.
