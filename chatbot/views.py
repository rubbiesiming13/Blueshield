from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def police_ai(request):
    return render(
        request,
        "chatbot/police_ai.html"
    )