# we are making a python based resume analyzer using NLP and Django
# This file is part of the Django application that serves as the entry point for the web application.
# it defines the main view for the application.
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render


def Home(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render(request=request))


def score(request):
    template = loader.get_template("score.html")
    return HttpResponse(template.render(request=request))


def upload_resume(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        if resume_file:
            return render(request, "score.html", {"message": "Resume uploaded successfully!", "filename": resume_file.name})
        else:
            return render(request, "score.html", {"message": "No file uploaded."})
    else:
        return render(request, "score.html")
