# filepath: [urls.py](http://_vscodecontentref_/0)
from django.contrib import admin
from django.urls import path
from . import page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", page.Home, name="home"),
    path("score/", page.score, name="score"),
    # Add your analyze view here when ready, e.g.:
    path("score/analyze/", page.analyze, name="analyze"),
]
