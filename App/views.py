# we are making a python based resume analyzer using NLP and Django
# This file is part of the Django application that serves as the entry point for the web application.
# it defines the main view for the application.
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models.resume import Resume
from .models.recieve import extract_text_from_pdf, extract_text_from_docx
import os
from App.utils.rating import calculate_resume_score


def Home(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render(request=request))


def score(request):
    template = loader.get_template("score.html")
    return HttpResponse(template.render(request=request))


def save_uploaded_resume(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        if resume_file:
            ext = os.path.splitext(resume_file.name)[1].lower()
            if ext == ".pdf":
                text = extract_text_from_pdf(resume_file)
            elif ext == ".docx":
                text = extract_text_from_docx(resume_file)
            else:
                text = """Unsupported file format. Please upload a PDF or DOCX file."""
            resume = Resume.objects.create(
                filename=resume_file.name,
                text=text,
                uploaded_file=resume_file
            )
            return render(request, "score.html", {"resume": resume})
        else:
            return render(request, "score.html", {"error": "No file uploaded."})
    return render(request, 'index.html')


def rating_result(request):
    resume = Resume.objects.order_by('-uploaded_at').first()
    rating_res = {}
    score = None
    found_keywords = []

    if resume:
        # Run scoring
        rating_res = calculate_resume_score(resume.text)
        score = rating_res.get("final_score", 0)

        # Collect only keyword-like items (avoid full sentences)
        for section in ["projects", "achievements", "certifications", "leadership_roles"]:
            items = rating_res.get(section, [])
            found_keywords.extend(
                [kw for kw in items if isinstance(
                    kw, str) and len(kw.split()) <= 4]
            )
        found_keywords = list(set(found_keywords))

    return render(request, "analyze.html", {
        "resume": resume,
        "score": score,
        "found_keywords": found_keywords,
        "details": rating_res
    })
