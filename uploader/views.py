from django.shortcuts import render
from django.http import HttpResponse
from .platforms.dailymotion import exchange_code_for_token

def dailymotion_callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse("No code parameter received.")

    try:
        tokens = exchange_code_for_token(code)
        # Save tokens in DB or session for later use
        # Example: request.session['dm_access_token'] = tokens['access_token']
        return HttpResponse(f"Access token received: {tokens['access_token']}")
    except Exception as e:
        return HttpResponse(f"Error exchanging code for token: {e}")
