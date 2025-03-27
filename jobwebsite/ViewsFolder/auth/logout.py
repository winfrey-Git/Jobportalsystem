from django.shortcuts import  redirect
from django.contrib.auth import logout 
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfuly")
    return redirect('home')