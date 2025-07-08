# filepath: [urls.py](http://_vscodecontentref_/0)
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.Home, name="home"),
    path("score/", views.score, name="score"),
    path("score/upload/", views.save_uploaded_resume, name="upload_resume"),
    path("score/upload/analyze/", views.rating_result, name="rating_result"),
    path("__reload__/", include("django_browser_reload.urls")),
]
