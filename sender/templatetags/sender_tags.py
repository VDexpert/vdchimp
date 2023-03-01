from django import template

register = template.Library()

@register.simple_tag()
def first_id(object_list):
    """
    Возвращает ссылку на объект класса User их первого объекта класса ConfigMailing.
    Неообходимо для скрытой передачи ForeignKey при создании нового объекта ConfigMailing
    """
    return object_list.first().username.id

@register.simple_tag()
def count_obj(object_list):
    return len(object_list)

@register.simple_tag()
def get_position(letters):
    if not len(letters):
        return 10
    else:
        return len(letters) * 10 + 10