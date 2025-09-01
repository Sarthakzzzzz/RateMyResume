# filepath: [urls.py](http://_vscodecontentref_/0)
from django.contrib import admin
from django.urls import path, include
from . import views
from . import views_enhanced
from . import views_dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views_dashboard.dashboard_home, name="Home"),
    path("score/", views.score, name="score"),
    path("score/upload/", views.save_uploaded_resume, name="upload_resume"),
    path("score/upload/analyze/", views.rating_result, name="rating_result"),
    
    # Enhanced analyzer URLs
    path("enhanced/", views_enhanced.enhanced_analysis, name="enhanced_analysis"),
    path("api/analysis/", views_enhanced.get_analysis_data, name="analysis_api"),
    path("compare/", views_enhanced.compare_positions, name="compare_positions"),
    
    # Comprehensive Dashboard URLs
    path("dashboard/", views_dashboard.comprehensive_analysis, name="comprehensive_analysis"),
    path("api/dashboard/", views_dashboard.get_dashboard_api, name="dashboard_api"),
    
    # Legacy home
    path("old-home/", views.Home, name="old_home"),
    
    path("__reload__/", include("django_browser_reload.urls")),
]
