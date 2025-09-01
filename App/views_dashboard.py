from django.shortcuts import render
from django.http import JsonResponse
from .models.resume import Resume
from .models.recieve import extract_text_from_pdf, extract_text_from_docx
from .utils.dashboard_generator import ResumeDashboard
import os

def dashboard_home(request):
    """Main dashboard view"""
    return render(request, 'dashboard_home.html')

def comprehensive_analysis(request):
    """Comprehensive dashboard analysis"""
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
                return render(request, "dashboard_home.html", {
                    "error": "Unsupported file format. Please upload a PDF or DOCX file."
                })
            
            # Save resume
            resume = Resume.objects.create(
                filename=resume_file.name,
                text=text,
                uploaded_file=resume_file
            )
            
            # Generate comprehensive dashboard
            dashboard = ResumeDashboard()
            dashboard_data = dashboard.generate_comprehensive_dashboard(text, position)
            
            context = {
                "resume": resume,
                "dashboard_data": dashboard_data,
                "position": position.replace('_', ' ').title()
            }
            
            return render(request, "comprehensive_dashboard.html", context)
        else:
            return render(request, "dashboard_home.html", {
                "error": "No file uploaded."
            })
    
    return render(request, 'dashboard_home.html')

def get_dashboard_api(request):
    """API endpoint for dashboard data"""
    resume = Resume.objects.order_by('-uploaded_at').first()
    position = request.GET.get('position', 'software_engineer')
    
    if resume:
        dashboard = ResumeDashboard()
        dashboard_data = dashboard.generate_comprehensive_dashboard(resume.text, position)
        
        # Convert to JSON-serializable format
        api_data = {
            'overall_score': dashboard_data['analysis']['position_score']['weighted_score'],
            'grade': dashboard_data['analysis']['position_score']['grade'],
            'position': position,
            'skills_analysis': dashboard_data['analysis']['skills_analysis'],
            'suggestions_count': {
                'critical': len(dashboard_data['analysis']['suggestions']['critical']),
                'important': len(dashboard_data['analysis']['suggestions']['important']),
                'nice_to_have': len(dashboard_data['analysis']['suggestions']['nice_to_have'])
            },
            'section_scores': dashboard_data['analysis']['base_analysis']
        }
        
        return JsonResponse(api_data)
    
    return JsonResponse({'error': 'No resume found'})