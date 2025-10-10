# Deployment Architecture

## Development Environment

**Prerequisites:**
- Python >=3.13
- uv (fast Python package manager)
- Terminal emulator (iTerm2, Windows Terminal, GNOME Terminal, etc.)
- Mealie instance with API access

**Setup Steps:**

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd mealie-testing
   ```

2. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your Mealie URL and API key
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Run application**
   ```bash
   python main.py
   # or
   uv run main.py
   ```

## Production Deployment

**Deployment Model:** Local user installation (not server-deployed)

**User Installation:**
```bash
# User on their local machine
git clone <repo-url>
cd mealie-testing
uv sync
cp .env.example .env
# User edits .env with their Mealie credentials
python main.py
```

**No Infrastructure Required:**
- No database (uses Mealie API)
- No web server (terminal app)
- No containerization needed (Python process)
- No CI/CD pipeline (manual git pull for updates)

## Upgrade Path (for Batch Mode)

**Current Version → Batch-Enabled Version:**

1. **User pulls latest code**
   ```bash
   git pull origin main
   ```

2. **Update dependencies** (if changed)
   ```bash
   uv sync
   ```

3. **Run application** (batch mode available)
   ```bash
   python main.py
   ```

**State Migration:** No database migrations needed (stateless app)

**Configuration Changes:** Optional new .env variables for batch mode:
```bash
BATCH_MODE_ENABLED=true         # Feature flag
SIMILARITY_THRESHOLD=0.85       # Fuzzy matching threshold
```

## Rollback Procedure

**If Batch Mode Causes Issues:**

1. **Disable batch mode** (via feature flag)
   ```bash
   # Edit .env
   BATCH_MODE_ENABLED=false
   ```

2. **Revert to previous version**
   ```bash
   git checkout <previous-tag>
   uv sync
   ```

3. **Or use sequential mode** (batch mode is additive - sequential mode unchanged)

---
