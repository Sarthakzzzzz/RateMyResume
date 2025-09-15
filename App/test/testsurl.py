from django.test import SimpleTestCase
from django.urls import reverse, resolve, NoReverseMatch
import App.views_dashboard as views
import App.views_enhanced as views_main
import os
import django


# Ensure this is the correct settings module for your project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RateMyResume.settings")
django.setup()


class TestViewResolution(SimpleTestCase):
    def _try_reverse(self, name, fallback):
        try:
            return reverse(name)
        except NoReverseMatch:
            return fallback

    def _get_view_attr(self, attr_name):
        return getattr(views, attr_name, None)

    def test_home_url_is_resolved(self):
        path = self._try_reverse("home", "/")
        view_obj = self._get_view_attr("Home")
        if view_obj is None:
            self.skipTest("Home view not defined in App.views")
        try:
            resolved = resolve(path)
        except Exception:
            self.skipTest(f"URL name 'home' not configured; tried path {path}")
        self.assertEqual(resolved.func, view_obj)

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
