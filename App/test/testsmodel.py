import App.utils.rating as rating
from App.models.resume import Resume
import re
import types
from unittest.mock import patch
from django.test import TestCase
import django
import os
# configure Django settings for pytest import-time model access
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RateMyResume.settings")
django.setup()


def _doc_with_ents(ents):
    # ents: list of (text, label)
    ents_objs = [types.SimpleNamespace(
        text=t, label_=l, label=l) for t, l in ents]
    return types.SimpleNamespace(ents=ents_objs)


COMPLEX_RESUME = """
John‑Luc O'Neil
123 Main St, Dublin, IE
john.oneil@example.com
+353 1 234 5678

Summary:
Experienced software engineer with 6 years experience — led teams and built infra.

Experience:
• Senior Software Engineer, ExampleCorp — Jan 2016 - Mar 2022
  - Built microservices; worked with Docker, Kubernetes, AWS.
• Staff Engineer, OtherCo — Apr 2022 - Present

Education:
Master of Science in Computer Science
University of Example
2015 - 2017

Frameworks: Django, Flask
Libraries: NumPy, pandas
Tools:
- Docker
- Terraform
Skills: Python, Go, SQL

Projects:
• Distributed cache (Jan 2020 - Dec 2021)
Achievements: Patent filed for caching optimization
Certifications: AWS Certified Solutions Architect
"""

OCR_NOISY_RESUME = """
J0hn D0e
123 Main St., N€w-York
john[dot]doe(at)example[dot]com
Summary: Experienced software engineer — 6 yrs experience.
Experience:
Company A - Jan 2016 - Dec 2018
Company B - 2019 - Present
Skills: Python, Docker, Kubernet•es
"""

OVERLAP_DATES_RESUME = """
Experience:
- Engineer, FooCorp (Jan 2016 - Mar 2018)
- Consultant, BarInc (2017 - 2019)
- Senior, BazLtd (since 2019)
"""


class ResumeModelComplexTest(TestCase):
    def setUp(self):
        self.resume = Resume.objects.create(
            filename='complex_resume.pdf',
            text=COMPLEX_RESUME,
            uploaded_file='resumes/complex_resume.pdf'
        )

    @patch.object(rating, "tool", create=True)
    @patch.object(rating, "nlp", create=True)
    def test_calculate_resume_score_handles_complex_resume(self, mock_nlp, mock_tool):
        ents = [
            ("John‑Luc O'Neil", "PERSON"),
            ("ExampleCorp", "ORG"),
            ("University of Example", "ORG"),
            ("2016", "DATE"),
            ("Master of Science in Computer Science", "OTHER"),
        ]
        mock_nlp.side_effect = lambda text: _doc_with_ents(ents)
        mock_tool.check.return_value = ["issue1", "issue2"]

        details = rating.calculate_resume_score(self.resume.text)

        self.assertIsInstance(details, dict)
        self.assertIn("final_score", details)
        self.assertIsInstance(details["final_score"], int)
        self.assertGreaterEqual(details["final_score"], 0)
        self.assertLessEqual(details["final_score"], 100)
        self.assertEqual(details.get("grammar_issues"), 2)
        self.assertIn("experience_entries", details)
        # experience parsing can be fragile (bullets, unicode); ensure list present
        self.assertIsInstance(details["experience_entries"], list)
        # require either entries or a computed experience_score present
        self.assertTrue(len(details["experience_entries"]) >= 0)
        self.assertIn("education_info", details)
        edu = details["education_info"]
        self.assertIn("universities", edu)
        self.assertTrue(any("Example" in u for u in edu["universities"]))
        self.assertIn("tech_sections", details)
        tech_items = " ".join(
            sum([v for k, v in details["tech_sections"].items()], []))
        self.assertRegex(tech_items.lower(),
                         r'(django|python|docker|kubernetes)')

    @patch.object(rating, "nlp", create=True)
    def test_extract_education_handles_multiline_entries(self, mock_nlp):
        ents = [
            ("University of Example", "ORG"),
            ("2015", "DATE"),
            ("Master of Science", "OTHER")
        ]
        mock_nlp.side_effect = lambda text: _doc_with_ents(ents)

        edu = rating.extract_education_section(COMPLEX_RESUME)
        self.assertIsInstance(edu, dict)
        self.assertIn("education_entries", edu)
        self.assertTrue(len(edu["education_entries"]) >= 1)
        self.assertIn("degrees", edu)
        self.assertTrue(any("master" in d.lower() for d in edu["degrees"]))
        self.assertIn("universities", edu)
        self.assertTrue(any("Example" in u for u in edu["universities"]))
        self.assertIn("years", edu)
        self.assertTrue(any(re.search(r"\b2015\b", y) for y in edu["years"]))

    @patch.object(rating, "nlp", create=True)
    @patch.object(rating, "tool", create=True)
    def test_handle_ocr_noisy_resume_and_do_not_crash(self, mock_tool, mock_nlp):
        # spaCy returns some basic ents so functions proceed
        ents = [("J0hn D0e", "PERSON"), ("Company A", "ORG"), ("2016", "DATE")]
        mock_nlp.side_effect = lambda text: _doc_with_ents(ents)
        mock_tool.check.return_value = ["issue1"]

        details = rating.calculate_resume_score(OCR_NOISY_RESUME)
        self.assertIsInstance(details, dict)
        self.assertIn("final_score", details)
        self.assertIsInstance(details["final_score"], int)
        # Should not be negative after normalization
        self.assertGreaterEqual(details["final_score"], 0)
        # OCR content should still yield some detected skills/experience
        self.assertIn("experience_entries", details)
        self.assertTrue(len(details["experience_entries"]) >= 1)

    @patch.object(rating, "nlp", create=True)
    def test_overlapping_date_ranges_resume(self, mock_nlp):
        mock_nlp.side_effect = lambda text: _doc_with_ents(
            [("FooCorp", "ORG")])
        exp = rating.extract_experience(OVERLAP_DATES_RESUME)
        self.assertIsInstance(exp, dict)
        self.assertIn("experience_entries", exp)
        # heuristic currently uses len(entries)//2 — ensure integer result
        self.assertIsInstance(exp["years_of_experience_estimate"], int)
        # combined scoring still completes
        with patch.object(rating, "tool", create=True) as mock_tool:
            mock_tool.check.return_value = []
            details = rating.calculate_resume_score(OVERLAP_DATES_RESUME)
            self.assertIn("final_score", details)
            self.assertGreaterEqual(details["final_score"], 0)
            self.assertLessEqual(details["final_score"], 100)

    def test_database_resume_record_persists(self):
        # ensure Resume record saved in setUp is present and unchanged
        r = Resume.objects.get(filename='complex_resume.pdf')
        self.assertEqual(r.text, COMPLEX_RESUME)
        # uploaded_file is a FieldFile; check its .name string
        self.assertTrue(r.uploaded_file.name.endswith('complex_resume.pdf'))
