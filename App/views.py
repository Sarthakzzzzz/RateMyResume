from django.shortcuts import render
from django.http import JsonResponse
from .utils.rating import calculate_resume_score

def Home(request):
    """Legacy home view"""
    return render(request, 'dashboard_home.html')

def score(request):
    """Score view"""
    return render(request, 'dashboard_home.html')

def save_uploaded_resume(request):
    """Handle resume upload"""
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def rating_result(request):
    """Return rating results"""
    if request.method == 'POST':
        resume_text = request.POST.get('resume_text', '')
        if resume_text:
            analysis = calculate_resume_score(resume_text)
            return JsonResponse(analysis)
    return JsonResponse({'error': 'No resume text provided'})