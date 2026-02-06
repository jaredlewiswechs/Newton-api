# realTinyTalk Web IDE - Server-Side Script Persistence

This directory contains the web UI for realTinyTalk and the server endpoints that support server-side script persistence and versioning.

New features added (Feb 2026):

- Server-side script storage with versioning at `storage/scripts/`.
- Endpoints:
  - `GET /api/scripts` - list scripts and metadata
  - `GET /api/scripts/<name>` - get latest script and versions
  - `GET /api/scripts/<name>/version/<vid>` - get a specific version
  - `POST /api/scripts` - save a script (creates a new version). JSON body: `{name, code, message}`
  - `POST /api/scripts/<name>/restore` - restore a version by `version_id` (creates new version)
  - `DELETE /api/scripts/<name>` - delete a script

- UI improvements in `static/index.html`:
  - Local `localStorage` multi-file support and tabs
  - Save / Save As / Export / Import
  - Autosave (toggle)
  - Save to server & Server Sync (load from server)
  - Version History and restore
  - Tab rename, close, and drag-to-reorder
  - Autosave indicator and status messages

Testing
-------
Run unit tests for the Flask endpoints with pytest:

```bash
# from workspace root
pytest realTinyTalk/web/tests/test_server_scripts.py -q
```

Notes
-----
- Server storage is a simple filesystem-backed store under `realTinyTalk/web/storage/scripts/`.
- This is intentionally simple; for production you should add authentication, per-user isolation, and access control.
