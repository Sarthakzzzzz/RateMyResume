from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render
from .models.resume import Resume
from .models.recieve import extract_text_from_pdf, extract_text_from_docx
from .utils.enhana import EnhancedResumeAnalyzer
from .utils.enhanced_ana import AdvancedResumeAnalyzer
from .utils.enhanced_ana import AdvancedResumeAnalyzer
import os

def Home(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render(request=request))

def enhanced_analysis(request):
    """Enhanced resume analysis with position-based scoring"""
    if request.method == "POST":
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
                return render(request, "enhanced_analysis.html", {
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
            analysis['advanced'] = advanced_analysis
            
            # Generate charts
            charts = analyzer.generate_charts(analysis['charts_data'])
            
            context = {
                "resume": resume,
                "analysis": analysis,
                "charts": charts,
                "position": position.replace('_', ' ').title()
            }
            
            return render(request, "advanced_analysis.html", context)
        else:
            return render(request, "enhanced_analysis.html", {
                "error": "No file uploaded."
            })
    
    return render(request, 'enhanced_upload.html')

def get_analysis_data(request):
    """API endpoint for getting analysis data as JSON"""
    resume = Resume.objects.order_by('-uploaded_at').first()
    position = request.GET.get('position', 'software_engineer')
    
    if resume:
        analyzer = EnhancedResumeAnalyzer()
        analysis = analyzer.analyze_for_position(resume.text, position)
        
        # Convert to JSON-serializable format
        json_data = {
            'overall_score': analysis['position_score']['weighted_score'],
            'grade': analysis['position_score']['grade'],
            'skills_match': analysis['skills_analysis'],
            'suggestions': analysis['suggestions'],
            'charts_data': analysis['charts_data']
        }
        
        return JsonResponse(json_data)
    
    return JsonResponse({'error': 'No resume found'})

def compare_positions(request):
    """Compare resume against multiple positions"""
    resume = Resume.objects.order_by('-uploaded_at').first()
    
    if resume:
        advanced_analyzer = AdvancedResumeAnalyzer()
        positions = ['software_engineer', 'data_scientist', 'product_manager', 'marketing_manager']
        
        comparisons = {}
        for position in positions:
            analysis = advanced_analyzer.comprehensive_analysis(resume.text, position)
            comparisons[position] = {
                'score': analysis['final_score']['final_score'],
                'grade': analysis['final_score']['grade'],
                'ats_score': analysis['ats_analysis']['total_score'],
                'job_match': analysis['semantic_analysis']['similarity_score'],
                'skill_count': analysis['skill_analysis']['total_skills']
            }
        
        return render(request, 'position_comparison.html', {
            'comparisons': comparisons,
            'resume': resume
        })
    
    return render(request, 'enhanced_upload.html', {
        'error': 'No resume found for comparison'
    })