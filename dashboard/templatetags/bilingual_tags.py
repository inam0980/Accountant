"""
Bilingual template tags for handling Arabic/English content
"""
from django import template
from django.utils.translation import get_language

register = template.Library()


@register.filter
def bilingual_name(obj):
    """
    Return name in current language.
    Checks for name_arabic field and returns it if language is Arabic.
    
    Usage: {{ school|bilingual_name }}
    """
    current_lang = get_language()
    
    if current_lang == 'ar':
        # Check if object has arabic name field
        arabic_field = None
        for field_name in ['name_arabic', 'school_name_arabic', 'title_arabic']:
            if hasattr(obj, field_name):
                arabic_field = getattr(obj, field_name)
                if arabic_field:
                    return arabic_field
    
    # Return default name
    for field_name in ['name', 'school_name', 'title', '__str__']:
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if callable(value):
                return value()
            return value
    
    return str(obj)


@register.simple_tag
def get_field_value(obj, field_name):
    """
    Get field value in current language.
    
    Usage: {% get_field_value school 'name' %}
    """
    current_lang = get_language()
    
    if current_lang == 'ar':
        arabic_field = f"{field_name}_arabic"
        if hasattr(obj, arabic_field):
            value = getattr(obj, arabic_field)
            if value:
                return value
    
    if hasattr(obj, field_name):
        return getattr(obj, field_name)
    
    return ""


@register.filter
def is_rtl(value=None):
    """
    Check if current language is RTL (Right-to-Left).
    
    Usage: {% if request.LANGUAGE_CODE|is_rtl %}
    """
    current_lang = get_language()
    return current_lang in ['ar', 'he', 'fa', 'ur']


@register.simple_tag
def get_text_direction():
    """
    Get text direction for current language.
    
    Usage: <html dir="{% get_text_direction %}">
    """
    current_lang = get_language()
    return 'rtl' if current_lang in ['ar', 'he', 'fa', 'ur'] else 'ltr'
