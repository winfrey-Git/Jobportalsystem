from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("messages")

        send_mail(
            subject=f"Contact Form Submisssion from {name}",
            message=message,
            from_email=email,
            recipient_list=['winfredkive@gmail.com'],
        )
        return HttpResponse("thank you for contacting us!")
    return render(request, 'contact.html')