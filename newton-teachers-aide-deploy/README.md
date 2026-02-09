# Newton Teacher's Aide

The Ultimate Teaching Assistant for HISD NES. Fully offline — all computation runs client-side with zero server dependency.

## Features

- **Lesson Planner** — NES-compliant lesson plans with TEKS alignment
- **Slide Deck Generator** — Auto-generate presentation slides from lesson plans
- **Grade & Analyze** — Assessment analysis with statistical grouping
- **PLC Reports** — Professional Learning Community data reports
- **TEKS Browser** — Full K-8 standards database (all subjects)
- **Ask Newton** — AI teaching assistant chat
- **Wild Garden** — Student progress monitoring

## Deploy to Cloudflare Pages (Auto)

1. Push this repo to GitHub
2. Go to [Cloudflare Pages Dashboard](https://dash.cloudflare.com/?to=/:account/pages)
3. Click **Create a project** → **Connect to Git**
4. Select this repository
5. Configure build settings:
   - **Build command:** _(leave blank — static site, no build needed)_
   - **Build output directory:** `.` or `/`
6. Click **Save and Deploy**

Every push to `main` will auto-deploy.

## Deploy Manually (CLI)

```bash
npm install
npm run deploy
```

## Local Development

```bash
# With Cloudflare Workers dev server
npm run dev

# Or just open index.html directly — it works offline!
open index.html
```

## Architecture

This is a pure static site (HTML + CSS + JS). No build step, no bundler, no framework.

| File | Purpose |
|------|---------|
| `index.html` | Main application shell and all view templates |
| `app.js` | Application logic, navigation, UI interactions |
| `newton-offline-engine.js` | Complete offline computation engine (TEKS DB, lesson generator, assessment analyzer) |
| `styles.css` | All styles |
| `_headers` | Cloudflare Pages HTTP headers (security, caching) |
| `_redirects` | SPA fallback routing |
| `wrangler.toml` | Cloudflare Pages project config |

## License

(c) 2026 Jared Lewis — Ada Computing Company — Houston, Texas
