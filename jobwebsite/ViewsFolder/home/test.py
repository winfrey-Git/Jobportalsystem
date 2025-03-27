from django.utils.timezone import now
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect, render,get_object_or_404
from jobwebsite.models import Application,JobApplicationTest

def start_test(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    user = request.user

    # Check if the user has already passed
    if application.test_attempts.filter(passed=True).exists():
        messages.success(request, "You have already passed the test.")
        return redirect('jobseeker_dashboard')

    # Get the last attempt count
    attempts = application.test_attempts.count()
    if attempts >= 3:
        messages.error(request, "You have reached the maximum test attempts.")
        return redirect('jobseeker_dashboard')

    # Start test and set timer (e.g., 20 minutes)
    time_limit = 20 * 60  # 20 minutes in seconds
    request.session['test_start_time'] = now().timestamp() + time_limit

    return render(request, 'test.html', {'application': application, 'time_limit': time_limit})

def submit_test(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    test = application.job.test
    user_answers = request.POST
    correct_answers = 0
    total_questions = test.total_questions

    # Calculate score
    for question in test.questions.all():
        if user_answers.get(f'question_{question.id}') == question.correct_answer:
            correct_answers += 1

    score = (correct_answers / total_questions) * 100
    passed = score >= test.passing_score

    # Get time taken
    start_time = request.session.get('test_start_time', None)
    time_taken = 0
    if start_time:
        time_taken = max(0, start_time - now().timestamp())

    # Track attempt
    attempt_number = application.test_attempts.count() + 1
    JobApplicationTest.objects.create(
        application=application, attempt_number=attempt_number, score=score, passed=passed, time_taken=time_taken
    )

    # Check result
    if passed:
        messages.success(request, "You passed! You will be considered for an interview.")
        return redirect('jobseeker_dashboard')
    elif attempt_number >= 3:
        messages.error(request, "You have failed all three attempts.")
        return redirect('jobseeker_dashboard')

    messages.warning(request, f"You scored {score}%. You have {3 - attempt_number} attempts left.")
    return redirect('start_test', application_id=application.id)
