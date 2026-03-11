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

- On Render, put build steps in Build Command and use the Start Command above. If Start exits quickly, the platform marks the app as crashed.

Case sensitivity (Linux hosts)
------------------------------
- Your local machine (Windows/macOS) may be case-insensitive. On Linux (Render, Docker containers), imports and filenames are case-sensitive.
- Ensure module/file import casing matches filenames exactly. Example: `from app import create_app` expects a folder named `app`.

Quick checks before deploy
--------------------------
- Ensure `SECRET_KEY` is configured in your platform's environment (do not commit `.env`).
- Add `RATELIMIT_STORAGE_URL` (Redis) in production for consistent rate-limiting across workers.
- Use persistent/object storage for generated files (set `FILE_STORAGE_PATH` or implement S3 uploads).
- Add a release hook to run migrations: `flask db upgrade`.
