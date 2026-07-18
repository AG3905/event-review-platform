Deployment notes and platform rules
=================================

Port rule
---------
- Always use the `PORT` environment variable when binding the server. Example in `run.py`:

  - `port = int(os.environ.get('PORT', 5000))`

- In containers, use a command that expands `$PORT` (see `Dockerfile` using `sh -c`).

Build vs Start command (Render / Heroku)
--------------------------------------
- Build Command: runs once during deploy (e.g., install deps, compile assets). Example for this repo:

  - `pip install -r requirements.txt`

- Start Command: must keep a process running. Example (Procfile / Heroku):

  - `web: gunicorn "app:create_app()" -w 4 -b 0.0.0.0:$PORT`

- On Render, use the repository's `bash build.sh` build command. It installs dependencies and runs `flask db upgrade`; the Gunicorn start command remains long-lived.

Case sensitivity (Linux hosts)
------------------------------
- Your local machine (Windows/macOS) may be case-insensitive. On Linux (Render, Docker containers), imports and filenames are case-sensitive.
- Ensure module/file import casing matches filenames exactly. Example: `from app import create_app` expects a folder named `app`.

Quick checks before deploy
--------------------------
- Ensure `SECRET_KEY` is configured in your platform's environment (do not commit `.env`).
- Set `DATABASE_URL` to the existing Supabase PostgreSQL connection string. `render.yaml` intentionally does not provision a replacement database.
- Set `PLATFORM_ADMIN_EMAIL` to the existing organizer account that should be promoted to Platform Admin on its next successful sign-in.
- Add `RATELIMIT_STORAGE_URL` (Redis) in production for consistent rate-limiting across workers.
- Use persistent/object storage for generated files (set `FILE_STORAGE_PATH` or implement S3 uploads).
- If migrations are not run through `build.sh`, run `flask db upgrade` once using the production `DATABASE_URL` before starting the service.
