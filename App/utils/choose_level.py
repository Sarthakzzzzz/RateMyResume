# look for the job apllied and its level
'''
    diff levels:
    1. Entry level junior 
    2. Mid level
    3. Senior level
    4. Lead / Staff
    5. Manager / Director
    6. Principal / Architect
    7. VP / C Executive level
'''
import re
from typing import List, Dict, Union
import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_sm")
''' Option is already given in analyze.html'''


def rate_resume(job_title: str) -> int:
    """
    Get the job level based on the job title.
    Returns an integer from 1 (Entry) to 7 (VP/C-level), or 0 if unknown.
    """
    job_title = job_title.lower()
    if re.search(r'\b(junior|entry-level|associate)\b', job_title):
        return 1
    elif re.search(r'\b(mid-level|mid)\b', job_title):
        return 2
    elif re.search(r'\b(senior|sr)\b', job_title):
        return 3
    elif re.search(r'\b(lead|staff)\b', job_title):
        return 4
    elif re.search(r'\b(manager|director)\b', job_title):
        return 5
    elif re.search(r'\b(principal|architect)\b', job_title):
        return 6
    elif re.search(r'\b(vp|vice president|c-level|chief)\b', job_title):
        return 7
    else:
        return 0  # Unknown level
