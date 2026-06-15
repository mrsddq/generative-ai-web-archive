# GAI

A generative AI web application archive located in the `AI-Web-App/` folder.

## Structure

```text
AI-Web-App/
```

## Status

Baseline repository structure is complete:

- application folder
- Azure Translator Flask app
- `.env.example` for required credentials
- root README
- root `.gitignore`

## Setup

```bash
cd AI-Web-App
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app app run
```

## Maintenance Note

Keep this archived until it receives tests, screenshots, and a deployment path. Generated virtual environment files and local `.env` values should not be committed.

The concrete upgrade checklist lives in [docs/UPGRADE_PLAN.md](docs/UPGRADE_PLAN.md).
