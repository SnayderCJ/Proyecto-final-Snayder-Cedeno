# PLANIFICADOR_IA/planner/templatetags/planner_tags.py
from django import template
from django.utils import timezone
import datetime

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def confidence_class(confidence):
    if confidence >= 0.8:
        return 'ai-confidence-high'
    elif confidence >= 0.6:
        return 'ai-confidence-medium'
    else:
        return 'ai-confidence-low'

@register.filter
def confidence_text(confidence):
    if confidence >= 0.8:
        return '🎯 Alta confianza'
    elif confidence >= 0.6:
        return '📊 Confianza media'
    else:
        return '💭 Baja confianza'

@register.filter
def format_time(iso_string):
    try:
        dt_obj = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt_obj.strftime('%H:%M') 
    except ValueError:
        return iso_string

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value