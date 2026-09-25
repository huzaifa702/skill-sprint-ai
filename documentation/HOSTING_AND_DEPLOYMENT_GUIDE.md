# SkillSprint AI — Production & Free Cloud Hosting Guide

**Theme:** OnboardVerse | **Category:** Generative AI PowerPlay  
**Target Enterprise:** AeroPulse Avionics & Autonomous Systems Inc.  
**Stack:** Python 3.11, Flask 3.1, SQLite 3 (WAL Mode), Gunicorn, Vanilla CSS/JS

---

## 1. Overview of Free Hosting Options

For hosting **SkillSprint AI** (a Python Flask + SQLite application) for free, there are four proven, zero-cost cloud options. We have pre-configured the codebase with **ready-to-deploy configuration files** for each.

| Platform | Free Tier Highlights | Best For | Included Config |
|---|---|---|---|
| **Render.com (Top Recommendation)** | • 100% Free Web Service<br>• Free Automatic SSL / HTTPS<br>• Auto-deploy from GitHub<br>• Custom domains supported | General public hosting, hackathon demos, production links | [`render.yaml`](file:///render.yaml)<br>[`Procfile`](file:///Procfile) |
| **Koyeb** | • Free Eco Tier<br>• Docker deployment<br>• Global edge routing | High-speed global edge hosting | [`deployment/Dockerfile`](file:///deployment/Dockerfile) |
| **PythonAnywhere** | • Free Python + SQLite hosting<br>• No container overhead<br>• Persistent storage | Classical Python environment | [`deployment/pythonanywhere_wsgi.py`](file:///deployment/pythonanywhere_wsgi.py) |
| **Instant Live Tunnel (Cloudflare / Localtunnel)** | • Instant live public URL in 10 seconds<br>• Zero cloud signups required | Immediate live sharing directly from your running machine | `npx localtunnel --port 5000` |

---

## 2. Option 1: Deploy to Render.com (Recommended — Step-by-Step)

**Render** is the industry standard for hosting Python Flask applications with automated continuous deployment from GitHub.

### Step 1: Push Your Code to a GitHub Repository
If you haven't pushed the project to GitHub yet, run these commands:
```bash
# 1. On GitHub (github.com), click "New Repository" -> name it "skill-sprint-ai" -> Public
# 2. In your terminal:
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/skill-sprint-ai.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to **[https://render.com](https://render.com)** and sign up / sign in (free).
2. Click **New +** in the top right and select **Blueprint** (or **Web Service**).
3. Connect your GitHub account and select your `skill-sprint-ai` repository.
4. Render will automatically detect [`render.yaml`](file:///render.yaml) and configure:
   - **Environment:** `Python 3`
   - **Plan:** `Free`
   - **Build Command:** `pip install -r requirements.txt && python -m src.database.seed_data && python scripts/generate_all_role_plans.py`
   - **Start Command:** `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
   - `FLASK_ENV`: `production`
6. Click **Apply / Deploy**.

Within 2 to 3 minutes, your application will be live at:
```text
https://skillsprint-ai.onrender.com
```

---

## 3. Option 2: Deploy to Koyeb (Free Docker Hosting)

Koyeb offers high-performance free Docker container hosting:

1. Sign up at **[https://koyeb.com](https://koyeb.com)**.
2. Click **Create Service** $\rightarrow$ **GitHub**.
3. Select your `skill-sprint-ai` repository.
4. Under **Builder**, select **Dockerfile** (pointing to `deployment/Dockerfile`).
5. Under **Environment Variables**, set:
   - `PORT`: `5000`
   - `SECRET_KEY`: `your-random-production-secret-key-32-chars`
   - `GEMINI_API_KEY`: `your-gemini-api-key`
6. Click **Deploy**. Your app will be live with free TLS at `https://<app-name>.koyeb.app`.

---

## 4. Option 3: Deploy to PythonAnywhere (Free SQLite Hosting)

PythonAnywhere is uniquely suited for Python + SQLite workloads:

1. Create a free account at **[https://www.pythonanywhere.com](https://www.pythonanywhere.com)**.
2. Open a **Bash Console** in your PythonAnywhere dashboard and clone your repo:
   ```bash
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/skill-sprint-ai.git
   cd skill-sprint-ai
   mkvirtualenv --python=/usr/bin/python3.11 skillsprint-env
   pip install -r requirements.txt
   python -m src.database.seed_data
   python scripts/generate_all_role_plans.py
   ```
3. Navigate to the **Web** tab in PythonAnywhere:
   - Add a new web app (select Manual Configuration $\rightarrow$ Python 3.11).
   - Set **Source code** to: `/home/<username>/skill-sprint-ai`
   - Set **Working directory** to: `/home/<username>/skill-sprint-ai`
   - Set **Virtualenv** to: `/home/<username>/.virtualenvs/skillsprint-env`
4. Click on the **WSGI configuration file** link, replace its contents with [`deployment/pythonanywhere_wsgi.py`](file:///deployment/pythonanywhere_wsgi.py), and save.
5. Click **Reload <username>.pythonanywhere.com**. Your app is live!

---

## 5. Option 4: Instant Public URL (Zero-Account Live Sharing)

If you need an immediate public link right now from your local running server (e.g. for a presentation or instant testing on your mobile phone):

### Method A: Cloudflare Tunnel (Free & Secure)
```bash
# If you have cloudflared installed:
cloudflared tunnel --url http://127.0.0.1:5000
```
This gives you an instant `https://<random-id>.trycloudflare.com` public URL.

### Method B: Localtunnel via npx (Pre-Installed)
```bash
npx localtunnel --port 5000
```
This prints a public `https://<subdomain>.loca.lt` URL that immediately forwards to your running local server.

---

## 6. Verification Checklist for Production

Before submitting your live URL:
- [x] Gunicorn WSGI configured in `Procfile` and `requirements.txt`
- [x] Seed data script generates all 22 documents and 10 roles
- [x] Batch generation populates all 207 requirement comparison records
- [x] Secret key loaded from environment variable
- [x] All 23 Pytest tests pass cleanly
- [x] Database file (`skillsprint.db`) is included or auto-seeded during build
