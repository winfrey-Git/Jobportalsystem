from django.shortcuts import render, redirect
from django.core.mail import EmailMessage

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")  # User's email
        message = request.POST.get("message")

        subject = f"New Contact Message from {name}"

        body = f"""
You received a new message via the contact form.

From: {name}
Email: {email}

Message:
{message}
"""

        email_msg = EmailMessage(
            subject=subject,
            body=body,
            from_email='winniekive@gmail.com',  # Must be your actual authenticated sender
            to=['winfrey965@gmail.com'],
            reply_to=[email],  # This is the trick that makes "Reply" go to the user
        )
        email_msg.send()

        return redirect('thank_you')  # or render a thank-you template

    return render(request, 'contact.html')



def thank_you(request):
    return render(request, 'thank_you.html')