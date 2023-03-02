from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(needs_autoescape=False)
@stringfilter
def format_err(error, autoescape=False):

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    result = error.replace('рассылки', '').replace('Название', 'названием')
    return mark_safe(esc(result))


@register.filter(needs_autoescape=True)
@stringfilter
def cutlastchar(text, autoescape=True):

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    result = text[:-1]
    return mark_safe(esc(result))


@register.filter
def create_range(value, start_index=0):
    return range(start_index, value+start_index)


@register.filter
def translatefield(field):
    weekdays_dict = {
        'sunday': 'воскресенье', 'monday': 'понедельник',
        'tuesday': 'вторник', 'wednesday': 'среда', 'thursday': 'четверг',
        'friday': 'пятница', 'saturday': 'суббота'
    }
    return weekdays_dict[str(field)]


@register.filter
def checkweekday(field, mailing):
    weekdays_dict = {
        'sunday': 'воскресенье', 'monday': 'понедельник',
        'tuesday': 'вторник', 'wednesday': 'среда', 'thursday': 'четверг',
        'friday': 'пятница', 'saturday': 'суббота'
    }

    if weekdays_dict[str(field)] in str(mailing.weekdays_text).replace(' ', '').split(','):
        return True

    return False


@register.filter
def checkmonthdate(field, mailing):
   return True if len([x for x in str(mailing.monthdates).replace(' ', '').split(',') if str(field).split('_')[1] == str(x)]) else False


@register.filter
def cutfieldfornum(field):
    return str(field).split('_')[1]


@register.filter(needs_autoescape=True)
def checkuseragenttablet(user_agent, autoescape=True):
    target_agent = ['ipad', 'tablet', 'tab', 'pad']

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    return True if len([x for x in target_agent if re.findall(x, esc(user_agent.lower()))]) else False


@register.filter(needs_autoescape=True)
def checkuseragentphone(user_agent, autoescape=True):
    target_agent = ['iphone', 'mobile', 'phone']

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    return True if len([x for x in target_agent if re.findall(x, esc(user_agent.lower()))]) else False


@register.filter
def calcposition(loop_count, sent_letters_count):
    return loop_count - sent_letters_count
