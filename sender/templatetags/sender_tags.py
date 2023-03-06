from django import template
from sender.models import Contacts

register = template.Library()


@register.simple_tag()
def count_obj(object_list):
    return len(object_list)


@register.simple_tag()
def get_position(letters):
    if not len(letters):
        return 10
    else:
        return len(letters) * 10 + 10


@register.simple_tag()
def getemail():
    if Contacts.objects.all():
        return Contacts.objects.all().first().email

    return 'False email'


@register.simple_tag()
def getphone():
    if Contacts.objects.all():
        return Contacts.objects.all().first().phone

    return 'False phone'
