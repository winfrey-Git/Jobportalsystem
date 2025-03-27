import random
import time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    """
    Handles user login with a math verification question, limits incorrect attempts,
    and enforces a 1-minute lockout on too many failures.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if "math_attempts" not in request.session:
        request.session["math_attempts"] = 0
        request.session["math_lockout_time"] = 0 

    if request.session["math_attempts"] >= 3:
        lockout_time = request.session.get("math_lockout_time", 0)
        current_time = time.time()

        if current_time - lockout_time < 60:
            remaining_time = int(60 - (current_time - lockout_time))
            messages.error(request, f"Too many incorrect answers. Try again in {remaining_time} seconds.")
            return render(request, "login.html")

        request.session["math_attempts"] = 0
        request.session["math_lockout_time"] = 0

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        num1 = int(request.POST.get("num1"))
        num2 = int(request.POST.get("num2"))
        correct_answer = num1 + num2
        user_answer = request.POST.get("math_answer")

        if not user_answer.isdigit() or int(user_answer) != correct_answer:
            request.session["math_attempts"] += 1  


            if request.session["math_attempts"] >= 3:
                request.session["math_lockout_time"] = time.time()
                messages.error(request, "Too many incorrect math answers. Try again in 60 seconds.")
                return render(request, "login.html")

            messages.error(request, f"Incorrect answer. Attempts left: {3 - request.session['math_attempts']}")
            return render(request, "login.html")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            request.session["math_attempts"] = 0 
            request.session["math_lockout_time"] = 0
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")

    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    return render(request, "login.html", {"num1": num1, "num2": num2})
