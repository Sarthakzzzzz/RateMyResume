import logging
import os

from django.http import JsonResponse
from django.shortcuts import render

from .models.recieve import extract_text_from_docx, extract_text_from_pdf
from .models.resume import Resume
from .utils.enhana import EnhancedResumeAnalyzer
from .utils.enchanced_paid import AdvancedResumeAnalyzer

logger = logging.getLogger(__name__)


def Home(request):
    return render(request, "dashboard_home.html")


def enhanced_analysis(request):
    """Enhanced resume analysis with position-based scoring"""
    if request.method == "POST":
        try:
            resume_file = request.FILES.get("resume")
            position = request.POST.get("position", "software_engineer")

            if resume_file:
                # Extract text
                ext = os.path.splitext(resume_file.name)[1].lower()
                if ext == ".pdf":
                    text = extract_text_from_pdf(resume_file)
                elif ext == ".docx":
                    text = extract_text_from_docx(resume_file)
                else:
                    return render(request, "enhanced.html", {
                        "error": "Unsupported file format. Please upload a PDF or DOCX file."
                    })

                # Save resume
                resume = Resume.objects.create(
                    filename=resume_file.name,
                    text=text,
                    uploaded_file=resume_file
                )

                # Analyze with advanced analyzer for precision
                advanced_analyzer = AdvancedResumeAnalyzer()
                advanced_analysis = advanced_analyzer.comprehensive_analysis(text, position)

                # Also get enhanced analysis for charts
                analyzer = EnhancedResumeAnalyzer()
                analysis = analyzer.analyze_for_position(text, position)

                # Merge analyses
                analysis["advanced"] = advanced_analysis

                # Generate charts
                charts = analyzer.generate_charts(analysis["charts_data"])

                context = {
                    "resume": resume,
                    "analysis": analysis,
                    "charts": charts,
                    "position": position.replace("_", " ").title(),
                }

                return render(request, "analysis.html", context)

            return render(request, "enhanced.html", {
                "error": "No file uploaded."
            })
        except Exception:
            logger.exception("Failed to generate enhanced analysis")
            return render(request, "enhanced.html", {
                "error": "We couldn't analyze that resume right now. Please try again with a valid PDF or DOCX file."
            })

    return render(request, "enhanced.html")


def get_analysis_data(request):
    """API endpoint for getting analysis data as JSON"""
    resume = Resume.objects.order_by("-uploaded_at").first()
    position = request.GET.get("position", "software_engineer")

    if resume:
        analyzer = EnhancedResumeAnalyzer()
        analysis = analyzer.analyze_for_position(resume.text, position)

        # Convert to JSON-serializable format
        json_data = {
            "overall_score": analysis["position_score"]["weighted_score"],
            "grade": analysis["position_score"]["grade"],
            "skills_match": analysis["skills_analysis"],
            "suggestions": analysis["suggestions"],
            "charts_data": analysis["charts_data"],
        }

        return JsonResponse(json_data)

    return JsonResponse({"error": "No resume found"})


def compare_positions(request):
    """Compare resume against multiple positions"""
    resume = Resume.objects.order_by("-uploaded_at").first()

    if resume:
        try:
            advanced_analyzer = AdvancedResumeAnalyzer()
            positions = [
                "software_engineer",
                "data_scientist",
                "product_manager",
                "marketing_manager",
            ]

            comparisons = {}
            for position in positions:
                analysis = advanced_analyzer.comprehensive_analysis(resume.text, position)
                skill_analysis = analysis["skill_analysis"]
                position_skills = advanced_analyzer.skill_databases.get(
                    position, advanced_analyzer.skill_databases["software_engineer"]
                )

                required_skills = position_skills.get("core_skills", [])
                preferred_skills = []
                for category, skills in position_skills.items():
                    if category != "core_skills":
                        preferred_skills.extend(skills)

                found_required = skill_analysis.get("found_skills", {}).get("core_skills", [])
                found_preferred = []
                for category, skills in skill_analysis.get("found_skills", {}).items():
                    if category != "core_skills":
                        found_preferred.extend(skills)

                comparisons[position] = {
                    "score": analysis["final_score"]["final_score"],
                    "grade": analysis["final_score"]["grade"],
                    "required_skills_match": round((len(found_required) / len(required_skills)) * 100, 1) if required_skills else 0,
                    "preferred_skills_match": round((len(found_preferred) / len(preferred_skills)) * 100, 1) if preferred_skills else 0,
                    "ats_score": analysis["ats_analysis"]["total_score"],
                    "job_match": analysis["semantic_analysis"]["similarity_score"],
                    "skill_count": skill_analysis["total_skills"],
                }

            return render(request, "poscom.html", {
                "comparisons": comparisons,
                "resume": resume,
            })
        except Exception:
            logger.exception("Failed to generate position comparison")
            return render(request, "enhanced.html", {
                "error": "We could not compare positions right now. Please try again."
            })

    return render(request, "enhanced.html", {
        "error": "No resume found for comparison"
    })
