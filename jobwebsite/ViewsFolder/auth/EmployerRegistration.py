from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction  # Import transaction to handle atomic operations
from jobwebsite.forms.EmployerRegistration import EmployerRegistration
from jobwebsite.models import Company

def Employer_Registration_View(request):
    if request.method == "POST":
        form = EmployerRegistration(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():  # Ensure both user and company details are saved together
                    user = form.save()  # Save the user first

                    # Get company details directly from request.POST
                    company_name = request.POST.get('company_name', '').strip()
                    company_address = request.POST.get('company_address', '').strip()
                    industry = request.POST.get('industry', '').strip()
                    company_description = request.POST.get('company_description', '').strip()
                    company_logo = request.FILES.get('company_logo', None)  # Handle optional file upload
                    contact_email = request.POST.get('contact_email', '').strip()
                    contact_phone = request.POST.get('contact_phone', '').strip()
                    website = request.POST.get('website', '').strip()

                    # Create the company and link it to the employer
                    company = Company.objects.create(
                        user=user,  # Link company to the employer
                        company_name=company_name,
                        company_address=company_address,
                        industry=industry,
                        company_description=company_description,
                        company_logo=company_logo,
                        contact_email=contact_email,
                        contact_phone=contact_phone,
                        website=website,
                    )

                    messages.success(request, "Registration successful! You can now log in.")
                    return redirect('login')  # Redirect to login page after successful registration

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")  # Show error message

    else:
        form = EmployerRegistration()

    return render(request, "employer/employer_registration.html", {"form": form})
