# RateMyResume

AI-powered resume analyzer with visual charts and position-based scoring.

## Features
- Position-specific analysis (Software Engineer, Data Scientist, Product Manager, Marketing Manager)
- Visual dashboard with 8 chart types
- ATS compatibility checking
- Skills gap analysis
- Automated improvement suggestions

## Quick Start

```bash
git clone <repo-url>
cd RateMyResume
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python manage.py migrate
python manage.py runserver
```

Access at `http://localhost:8000/`

## What You Get
- Overall score with letter grade (A+ to D)
- Skills matching analysis
- ATS compatibility score
- Visual charts and graphs
- Detailed improvement recommendations

## Tech Stack
- Django, spaCy, scikit-learn
- matplotlib, seaborn, pandas
- TF-IDF vectorization, cosine similarity

## Sample Output
```
Overall Score: 78.5% (Grade: B+)
Skills Match: 85% | ATS Score: 72% | Job Relevance: 80%

Critical: Missing Python, SQL skills
Important: Add quantified achievements
Suggestion: Include technical projects
```

## Deployment (Render)

This repo now includes `render.yaml` and `Procfile` for one-click Render deployment.

1. Push this repository to GitHub.
2. In Render, create a new Blueprint and connect this repo.
3. Render will provision:
   - A Python web service (`ratemyresume-web`)
   - A PostgreSQL database (`ratemyresume-db`)
   - A persistent disk mounted at `/var/data` for uploaded resumes
4. After first deploy, open your Render service URL.

Important environment variables are managed in `render.yaml`:
- `DEBUG=False`
- generated `SECRET_KEY`
- `DATABASE_URL` from Render Postgres
- `MEDIA_ROOT=/var/data/media`
