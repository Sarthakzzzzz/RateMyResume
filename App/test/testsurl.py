from django.test import SimpleTestCase


class testUrls(SimpleTestCase):
    def test_home_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_score_url(self):
        response = self.client.get('/score/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'score.html')

    def test_admin_url(self):
        response = self.client.get('/admin/')
        # Redirect to login page if not logged in
        self.assertEqual(response.status_code, 302)

    def test_upload_resume_url(self):
        response = self.client.get('/score/upload/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'score.html')
