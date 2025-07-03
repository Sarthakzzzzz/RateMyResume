from django.test import SimpleTestCase
from django.urls import reverse, resolve
from App.views import Home, upload_resume, score


class TestUrls(SimpleTestCase):
    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, Home)

    def test_upload_resume_url_is_resolved(self):
        url = reverse('upload_resume')
        self.assertEqual(resolve(url).func, upload_resume)

    def test_score_url_is_resolved(self):
        url = reverse('score')
        self.assertEqual(resolve(url).func, score)
