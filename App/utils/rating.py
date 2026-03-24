"""
Resume rating module - Facade for backward compatibility.

This module maintains backward compatibility by re-exporting functions
from the new modular structure.

New code should prefer importing directly from submodules:
- From extractors: get_personal_info, extract_education_section, etc.
- From scorers: tech_skills_score, calculate_quality_score
- From validators: detect_red_flags
- From calculator: calculate_resume_score
"""

# Import common components first
from . import common

# Import all public functions for backward compatibility
from .common import normalize_text, get_nlp, get_tool

from .extractors import (
    get_personal_info,
    extract_education_section,
    extract_experience,
    extract_projects,
    extract_achievements,
    extract_certifications,
    extract_leadership_roles,
)

from .scorers import (
    tech_skills_score,
    calculate_quality_score,
)

from .validators import detect_red_flags

from .calculator import calculate_resume_score

# Expose module-level instances for patching in tests
nlp = common.nlp
tool = common.tool

__all__ = [
    'normalize_text',
    'get_nlp',
    'get_tool',
    'get_personal_info',
    'extract_education_section',
    'extract_experience',
    'extract_projects',
    'extract_achievements',
    'extract_certifications',
    'extract_leadership_roles',
    'tech_skills_score',
    'calculate_quality_score',
    'detect_red_flags',
    'calculate_resume_score',
    'nlp',
    'tool',
]
