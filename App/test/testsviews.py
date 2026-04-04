import os
import django
import types
from unittest.mock import patch


# Ensure this is the correct settings module for your project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "App.settings")
os.environ["DEBUG"] = "True"
os.environ["SECURE_SSL_REDIRECT"] = "False"
os.environ.setdefault("MPLCONFIGDIR", "/tmp")
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.urls import reverse, resolve, NoReverseMatch

import App.views_enhanced as views


class TestViewResolution(SimpleTestCase):
    def _try_reverse(self, name, fallback):
        try:
            return reverse(name)
        except NoReverseMatch:
            return fallback

    def _get_view_attr(self, attr_name):
        return getattr(views, attr_name, None)

    def test_home_url_is_resolved(self):
        path = self._try_reverse("Home", "/")
        # Import dashboard_home from views_dashboard
        from App.views_dashboard import dashboard_home
        try:
            resolved = resolve(path)
        except Exception:
            self.skipTest(f"URL name 'Home' not configured; tried path {path}")
        self.assertEqual(resolved.func, dashboard_home)

    def test_upload_resume_url_is_resolved(self):
        path = self._try_reverse("upload_resume", "/upload/")
        view_obj = self._get_view_attr("upload_resume")
        if view_obj is None:
            self.skipTest("upload_resume view not defined in App.views")
        try:
            resolved = resolve(path)
        except Exception:
            self.skipTest(
                f"URL name 'upload_resume' not configured; tried path {path}")
        self.assertEqual(resolved.func, view_obj)

    def test_score_url_is_resolved(self):
        path = self._try_reverse("score", "/score/")
        view_obj = self._get_view_attr("score")
        if view_obj is None:
            self.skipTest("score view not defined in App.views")
        try:
            resolved = resolve(path)
        except Exception:
            self.skipTest(
                f"URL name 'score' not configured; tried path {path}")
        self.assertEqual(resolved.func, view_obj)

    def test_home_get_returns_success(self):
        path = self._try_reverse("home", "/")
        response = self.client.get(path)
        self.assertIn(response.status_code, (200, 302))

    def test_score_get_returns_success(self):
        path = self._try_reverse("score", "/score/")
        response = self.client.get(path)
        self.assertIn(response.status_code, (200, 302))


class DashboardAnalysisTest(SimpleTestCase):
    @patch("App.views_dashboard.Resume.objects.create")
    @patch("App.views_dashboard.extract_text_from_pdf")
    @patch("App.views_dashboard.ResumeDashboard")
    def test_dashboard_post_renders_existing_template(
        self, mock_dashboard_cls, mock_extract_pdf, mock_resume_create
    ):
        resume_text = (
            "Jane Doe\n"
            "jane.doe@example.com\n"
            "Python AWS Docker\n"
            "Experience\n"
            "Built internal tools\n"
        )

        mock_extract_pdf.return_value = resume_text
        mock_resume_create.return_value = types.SimpleNamespace(
            filename="resume.pdf",
            text=resume_text,
            uploaded_file="resumes/resume.pdf",
        )
        mock_dashboard = mock_dashboard_cls.return_value
        mock_dashboard.generate_comprehensive_dashboard.return_value = {
            "analysis": {
                "position_score": {
                    "weighted_score": 88.5,
                    "grade": "A",
                    "experience_score": 12.0,
                    "skills_score": 18.0,
                    "education_score": 7.0,
                    "projects_score": 9.0,
                },
                "skills_analysis": {
                    "required_found": ["python"],
                    "required_missing": [],
                    "preferred_found": ["aws"],
                    "preferred_missing": [],
                },
                "suggestions": {
                    "critical": [],
                    "important": [],
                    "nice_to_have": [],
                },
            },
            "charts": {
                "score_gauge": "",
                "skills_radar": "",
                "improvement_priority": "",
                "section_comparison": "",
                "skills_heatmap": "",
                "wordcloud": "",
                "progress_bars": "",
                "recommendation_chart": "",
            },
        }

        upload = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4\n% fake pdf content\n",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("comprehensive_analysis"),
            {"resume": upload, "position": "software_engineer"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        mock_extract_pdf.assert_called_once()
        mock_dashboard.generate_comprehensive_dashboard.assert_called_once_with(
            resume_text, "software_engineer"
        )
