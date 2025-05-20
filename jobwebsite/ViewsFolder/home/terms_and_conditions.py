from django.shortcuts import render,  get_object_or_404

def terms_and_conditions_view(request):
    return render(request, 'terms_and_conditions.html')