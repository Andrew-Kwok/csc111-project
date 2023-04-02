from django import template

register = template.Library()

@register.filter
def modulo(num: int, val: int) -> int:
    return num % val


@register.filter
def no_of_layovers(flights) -> str:
    layover = len(flights) - 1
    if layover == 0:
        return 'direct'
    if layover == 1:
        return '1 stop'
    return f'{layover} stops'