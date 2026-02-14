# Foghorn API Vercel Deployment

## 1. API Entrypoint
- The file `api/foghorn.py` is the Vercel entrypoint for the Foghorn API.
- It exposes the FastAPI app using the `mount_foghorn_api` function from `foghorn.api`.

## 2. vercel.json
- The `vercel.json` file is configured to route all `/foghorn/*` requests to `api/foghorn.py`.
- All other requests are routed to the main Newton API (`api/index.py`).

## 3. Requirements
- Foghorn dependencies are listed in `foghorn/requirements.txt`.
- Vercel will install these automatically for the Foghorn build.

## 4. Deploy Steps
1. Push your changes to the repository connected to Vercel.
2. Vercel will detect the new build entry for `api/foghorn.py` and install dependencies.
3. The Foghorn API will be available at `https://<your-vercel-domain>/foghorn/...`

## 5. Troubleshooting
- If you see import errors, ensure all dependencies are in `foghorn/requirements.txt`.
- If you see 404s, check the `rewrites` in `vercel.json`.
- For debugging, visit `/foghorn/health` for error details if startup fails.

---

For custom domains or advanced configuration, see the Vercel documentation.
