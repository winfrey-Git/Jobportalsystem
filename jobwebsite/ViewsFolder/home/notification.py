from django.shortcuts import render


def notification_view(request):
    return render(request, 'notification.html')