from django.test import TestCase
from App.models.resume import Resume


class ResumeModelTest(TestCase):
    def setUp(self):
        self.resume = Resume.objects.create(
            filename='test_resume.pdf',
            text='This is a test resume.',
            uploaded_file='resumes/test_resume.pdf'
        )

    def test_resume_creation(self):
        self.assertEqual(self.resume.filename, 'test_resume.pdf')
        self.assertEqual(self.resume.text, 'This is a test resume.')
        self.assertTrue(self.resume.uploaded_at is not None)
        self.assertEqual(self.resume.uploaded_file, 'resumes/test_resume.pdf')

    def test_resume_str(self):
        self.assertEqual(str(self.resume), 'test_resume.pdf')
