# we are making a python based resume analyzer using NLP and Django
# This file is part of the Django application that serves as the entry point for the web application.
# it defines the main view for the application.
from django.http import HttpResponse
from django.template import loader
def Home(request):
        template = loader.get_template("index.html")
        return HttpResponse(template.render(request=request))
def score(request):
        template = loader.get_template("score.html")
        return HttpResponse(template.render(request=request))
