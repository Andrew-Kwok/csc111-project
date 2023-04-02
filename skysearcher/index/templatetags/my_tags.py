from django import template
from typing import TypeAlias
from collections import namedtuple
from datetime import datetime, timedelta


DayHourMinute: TypeAlias = namedtuple('DayHourMinute', ['day', 'hour', 'minute'])
register = template.Library()


@register.filter
def modulo(num: int, val: int) -> int:
    return num % val


@register.filter
def no_of_layovers(flights: list) -> str:
    layover = len(flights) - 1
    if layover == 0:
        return 'direct'
    if layover == 1:
        return '1 stop'
    return f'{layover} stops'


@register.filter
def round2(price: float) -> float:
    return round(price, 2)


@register.filter
def digit2(num: int) -> int:
    return '0' * (2 - len(str(num))) + str(num)

@register.simple_tag
def get_minute_diff(before: DayHourMinute, after: DayHourMinute) -> int:
    if before.day > after.day:
        after = DayHourMinute(after.day + 7, after.hour, after.minute)
    elif before.day == after.day and before.hour > after.hour:
        after = DayHourMinute(after.day + 7, after.hour, after.minute)
    elif before.day == after.day and before.hour == after.hour and before.minute > after.minute:
        after = DayHourMinute(after.day + 7, after.hour, after.minute)

    return (after.day * 1440 + after.hour * 60 + after.minute) - \
        (before.day * 1440 + before.hour * 60 + before.minute)


@register.simple_tag
def get_hour_minute_diff(before: DayHourMinute, after: DayHourMinute) -> str:
    min_diff = get_minute_diff(before, after)
    print(before, after, min_diff)
    return f'{min_diff // 60}h {min_diff % 60}m'


def _get_day_diff_int(before: DayHourMinute, after: DayHourMinute) -> int:
    day_diff = after.day - before.day
    if day_diff < 0:
        day_diff += 7
    return day_diff

@register.simple_tag
def get_day_diff(before: DayHourMinute, after: DayHourMinute) -> str:
    day_diff = _get_day_diff_int(before, after)
    if day_diff == 0:
        return ''
    return f'(+{day_diff}d)'


@register.simple_tag
def get_layover_time(flights: list, i: int) -> str:
    return get_hour_minute_diff(flights[i].arrival_time, flights[i+1].departure_time)


@register.filter
def get_airlines(flights: list) -> str:
    airlines = []
    for flight in flights:
        if flight.airline not in airlines:
            airlines.append(flight.airline)
    return ", ".join(airlines)


@register.simple_tag
def get_date(pivot_datetime: str, pivot_weektime: DayHourMinute, query_weektime: DayHourMinute) -> str:    
    day_diff = _get_day_diff_int(pivot_weektime, query_weektime)
    date = pivot_datetime.split('-')
    departure_time = datetime(year=int(date[0]), 
                              month=int(date[1]), 
                              day=int(date[2]))
    departure_time += timedelta(days=int(day_diff))
    return f'{departure_time.day} {departure_time.strftime("%b")}'
