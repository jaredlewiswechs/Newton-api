# Simplest Flask entrypoint for Vercel to detect
# Vercel searches for an `app` variable in one of several locations;
# by placing this file at the project root we satisfy that requirement.

from api.index import app  # this file already constructs/exports the Flask app

# `app` is now visible at module level and Vercel can automatically
# serve the application.

# Optional handler alias used by some runtimes
handler = app
