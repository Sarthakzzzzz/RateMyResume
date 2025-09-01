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
pip install -r requirements_enhanced.txt
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