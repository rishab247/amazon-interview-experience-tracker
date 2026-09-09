# Amazon LeetCode Interview Explorer 🚀

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)
![Platform: Vercel](https://img.shields.io/badge/Platform-Vercel-black?logo=vercel)
![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-emerald)
![Database: 1300+ Experiences](https://img.shields.io/badge/Dataset-1%2C300%2B%20Experiences-FF9900)

An interactive intelligence hub and comprehensive interview preparation platform curated from 1,300+ real Amazon interview experiences shared on LeetCode Discuss.

---

## 🌟 Key Features

- **1,300+ Verified Experiences**: Real interview stories categorized by role (SDE I, SDE II, SDE III, EM, TPM, Intern), level, outcome (Offer, Rejected, Pending), and geographic location.
- **16 Amazon Leadership Principles Guide**: Complete breakdown of all 16 LPs with core philosophies, interviewer evaluation rubrics (positive signals & red flags), and actual interview behavioral questions.
- **Searchable Question Bank**: High-frequency algorithmic and system design questions tagged by difficulty, category, and recency.
- **Visual Analytics Dashboard**: Interactive offer acceptance statistics, LP distribution charts, and hiring funnel breakdowns.
- **Export Capabilities**: Download filtered candidate datasets into JSON or CSV directly from the interface.
- **Instant Search & Deep Filtering**: Search by keyword, timeline (2026, 2025, last 30/90 days), and bookmarks saved locally.

---

## 📁 Project Architecture

```text
├── vercel.json                  # Vercel zero-config routing, output directory, and cache headers
├── index.html                   # Clean root entrypoint with instant redirect & launch splash
├── README.md                    # Setup documentation and deployment guide
├── server.py                    # Local development server (HTTP + CORS + threaded handler)
├── start.bat                    # Quick-start script for Windows local testing
├── ui/                          # Production static web application (output directory)
│   ├── index.html               # Main application interface (Tailwind CSS, Lucide icons)
│   ├── app.js                   # Application state engine, filters, analytics & rendering
│   ├── style.css                # Custom glassmorphism styles and animations
│   └── experiences.json         # Primary curated dataset (1,300+ interview records)
├── data/
│   └── experiences.json         # Master source dataset
└── scripts/                     # Crawler and data enrichment pipeline
    ├── build_ui.py              # UI asset generator
    ├── crawler.js               # LeetCode discussion post scraper
    ├── enrich_interview_dates.py
    ├── enrich_questions_catalog.py
    ├── fetch_amazon_experiences.py
    ├── fetch_playwright_experiences.py
    ├── import_new_posts.py
    ├── ingest_all_catalog.py
    └── verify_dataset.py
```

---

## ⚡ Vercel Deployment Guide

This project is pre-configured for seamless, zero-config deployment on Vercel using `vercel.json`.

### Option 1: Automatic Continuous Deployment via GitHub (Recommended)

Link your GitHub repository (`rishab247/<repo>`) to Vercel for automatic zero-downtime builds whenever you push code or update data:

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure project for Vercel deployment"
   git remote add origin https://github.com/rishab247/<your-repo-name>.git
   git push -u origin master
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com/) and log in (or sign up with GitHub).
   - Click **"Add New..."** in the top-right corner and select **"Project"**.
   - Under **"Import Git Repository"**, find and select `rishab247/<your-repo-name>`.

3. **Deploy (Zero-Config)**:
   - **Project Name**: Choose any project name (e.g. `amazon-interview-explorer`).
   - **Framework Preset**: Leave as **Other** (or auto-detected).
   - **Root Directory**: Leave as `./` (the root `vercel.json` automatically sets `outputDirectory: "ui"`).
   - **Build Command**: Leave blank (pure static assets, no compilation step needed).
   - **Output Directory**: Leave blank (configured in `vercel.json`).
   - Click **Deploy**.

4. **Continuous Deployment Active**:
   - Every `git push` to `master` automatically triggers an updated deployment within seconds.
   - Pull requests automatically generate preview environments with shareable URLs.

---

### Option 2: Deploying via Vercel CLI

You can also deploy directly from your local terminal using the Vercel CLI:

```bash
# 1. Install or run Vercel CLI
npx vercel

# 2. Deploy directly to production
npx vercel --prod
```

Follow the brief CLI prompts on first run to link your Vercel account.

---

## ⚙️ How `vercel.json` Works

The root `vercel.json` provides edge routing, asset optimization, and CDN caching rules:

- **Root Output Directory (`outputDirectory: "ui"`)**:
  Instructs Vercel to serve the optimized frontend files in `ui/` as the site root (`/`), ensuring `ui/index.html` is the primary entrypoint without directory nesting.
- **Clean URLs (`cleanUrls: true`)**:
  Enables clean, extensionless URLs (`/` instead of `/index.html`).
- **Rewrites**:
  - Directs `/api/experiences` and `/api/status` to `/experiences.json` so frontend and external scripts fetch data reliably.
  - Rewrites `/ui` and `/ui/*` to root assets so bookmarks and legacy URLs continue to resolve.
- **Smart Cache-Control Headers**:
  - `experiences.json`: Short edge cache (`s-maxage=300`, `max-age=60`, `stale-while-revalidate=600`) ensuring users immediately receive newly scraped or enriched interview records.
  - Static Assets (`style.css`, `app.js`): Long-term edge caching (`max-age=86400`, `stale-while-revalidate=604800`) for near-instant repeat page loads.
  - HTML Files: Dynamic revalidation (`max-age=0, must-revalidate`) so UI changes deploy instantly.
- **Security & CORS Headers**:
  - Built-in protection headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`).
  - CORS header (`Access-Control-Allow-Origin: *`) enabled for API and JSON endpoints.

---

## 💻 Local Development

### Option A: Built-in Python Server
Run the custom threaded Python server:
```bash
python server.py
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### Option B: Any Static Web Server
```bash
# Using Node's serve
npx serve ui

# Using Python's http.server from repo root
python -m http.server 8000
```
Open [http://localhost:8000](http://localhost:8000) (the root `index.html` will automatically route to the UI).

### Option C: Vercel Local Emulation
```bash
npx vercel dev
```
Simulates the exact Vercel Edge routing and header environment locally on port 3000.

---

## 📄 License
Curated for educational and interview preparation purposes. Content sourced from public LeetCode Discuss community submissions.
