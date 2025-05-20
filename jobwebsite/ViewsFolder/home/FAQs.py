from django.shortcuts import render

def faqs_view(request):
    return render(request, 'faqs.html')

def user_guide_view(request):
    return render(request, 'user_guide.html')
