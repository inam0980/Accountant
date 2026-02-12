"""
Language switching views
"""
from django.shortcuts import redirect
from django.utils import translation
from django.conf import settings
from django.http import HttpResponseRedirect


def set_language(request):
    """
    Set user's preferred language and redirect back to previous page.
    
    Accepts language code via POST or GET parameter 'language'.
    """
    next_url = request.POST.get('next', request.GET.get('next'))
    if not next_url:
        next_url = request.META.get('HTTP_REFERER', '/')
    
    language = request.POST.get('language', request.GET.get('language'))
    
    if language and language in [lang[0] for lang in settings.LANGUAGES]:
        # Activate the language
        translation.activate(language)
        
        # Set language in session
        if hasattr(request, 'session'):
            request.session[translation.LANGUAGE_SESSION_KEY] = language
        
        # Create response
        response = HttpResponseRedirect(next_url)
        
        # Set language cookie
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        
        return response
    
    return HttpResponseRedirect(next_url)
