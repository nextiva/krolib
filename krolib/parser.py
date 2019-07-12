import math
import calendar
import datetime
import typing as t

from toolz.dicttoolz import get_in, assoc_in
from dateutil.relativedelta import (
    relativedelta,
    MO,
    TU,
    WE,
    TH,
    FR,
    SA,
    SU,
)
from dateutil.rrule import (
    rrule,
    YEARLY,
    MONTHLY,
    WEEKLY,
    DAILY,
    HOURLY,
    MINUTELY,
    SECONDLY,
)

from .structs import (
    TimeUnits,
    PeriodicalUnits,
    RelativeUnits,
    RelativeIndexUnits,
    ScheduleSchema,
    RelativeScheduleSchema,
    GettersSchema,
)
from .utils import (
    just_now,
    is_weekday,
    is_weekend,
    normalize_datetime,
)


TIMESHIFT_MAP = {
    TimeUnits.DAYS: lambda val: datetime.timedelta(days=val),
    TimeUnits.SECONDS: lambda val: datetime.timedelta(seconds=val),
    TimeUnits.MINUTES: lambda val: datetime.timedelta(minutes=val),
    TimeUnits.HOURS: lambda val: datetime.timedelta(hours=val),
    TimeUnits.WEEKS: lambda val: datetime.timedelta(weeks=val),
    TimeUnits.MONTHS: lambda val: datetime.timedelta(weeks=val * 4),
}

PERIODICAL_MAP = {
    PeriodicalUnits.YEARLY: YEARLY,
    PeriodicalUnits.MONTHLY: MONTHLY,
    PeriodicalUnits.WEEKLY: WEEKLY,
    PeriodicalUnits.DAILY: DAILY,
    PeriodicalUnits.HOURLY: HOURLY,
    PeriodicalUnits.MINUTELY: MINUTELY,
    PeriodicalUnits.SECONDLY: SECONDLY,
}

PERIODICAL_ATTRS_MAP = {
    'every': 'interval',
    'month': 'bymonth',
    'day': 'bymonthday',
    'weekday': 'byweekday',
    'hour': 'byhour',
    'minute': 'byminute',
    'second': 'bysecond',
}

SENSITIVE_ATTRS_MAP = {
    PeriodicalUnits.YEARLY: {'every', 'weekday', 'month', 'day', 'hour', 'minute', 'second'},
    PeriodicalUnits.MONTHLY: {'every', 'weekday', 'day', 'hour', 'minute', 'second'},
    PeriodicalUnits.WEEKLY: {'every', 'weekday', 'hour', 'minute', 'second'},
    PeriodicalUnits.DAILY: {'every', 'hour', 'minute', 'second'},
    PeriodicalUnits.HOURLY: {'every', 'minute', 'second'},
    PeriodicalUnits.MINUTELY: {'every', 'second'},
    PeriodicalUnits.SECONDLY: {'every'},
}

RELATIVE_DAY_MAP = {
    RelativeUnits.SUNDAY: SU,
    RelativeUnits.MONDAY: MO,
    RelativeUnits.TUESDAY: TU,
    RelativeUnits.WEDNESDAY: WE,
    RelativeUnits.THURSDAY: TH,
    RelativeUnits.FRIDAY: FR,
    RelativeUnits.SATURDAY: SA,
}


def validated_schedule(
        schedule: dict,
        getters: t.Optional[t.List[dict]] = None,
) -> dict:
    """Validates ``schedule`` with schemas and returns modified
    schedule dict if some getters provided.

    Getters are special functions that can be attached to get some
    schedule value from external source by key-path::

        getters = [
            {
                'getter': payload_getter,
                'params': {
                    'path': ['start', 'relative_timeshift', 'delay'],
                    'source': payload_source,
                }
            }
        ]

    In this case, :func:`payload_getter` will receive value by ``path``
    from the ``payload_source``. And ``schedule`` will be modified with
    the result from ``payload_getter`` by the same path.
    """
    if getters:
        getters = GettersSchema(getters)
        for getter in getters:
            modifier = getter['getter']
            params = getter.get('params', {})
            path_to_value = params.get('path')
            if path_to_value:
                path_value = get_in(path_to_value, schedule)
                if path_value is not None:
                    val = modifier(path_value, **params)
                    schedule = assoc_in(schedule, path_to_value, val)

    relative_params = (
        get_in(['periodical', 'relative_day'], schedule) and
        get_in(['periodical', 'relative_day_index'], schedule)
    )
    if relative_params:
        schedule = RelativeScheduleSchema(schedule)
    else:
        schedule = ScheduleSchema(schedule)

    return schedule


def schedule_parser(
    schedule: dict,
    now_dt: t.Optional[datetime.datetime] = None,
    getters: t.Optional[t.List[dict]] = None,
) -> t.Generator[datetime.datetime, None, None]:
    """Generates datetime objects by provided schedule structure.

    Simple periodical example::

        schedule = {
            'start': {
                'on': just_now(),
            },
            'periodical': {
                'repeats': 'weekly',
                'every': 1,
            },
            'stop': {
                'never': False,
                'after_num_repeats': 2
            }
        }
        schedule_gen = schedule_parser(schedule)


    Getters case::

        schedule_gen = schedule_parser(
            schedule,
            getters=[
                {
                    'getter': payload_getter,
                    'params': {
                        'path': ['start', 'relative_timeshift', 'delay'],
                        'source': payload_source,
                    }
                }
            ]
        )

    Pay special attention to the timezone hell. By default, parser uses UTC
    everywhere. You can set some local timezone with special ``timezone``
    field::

        start_on_jakarta = normalize_isoformat(
            '2019-03-20T22:00:00',
            tz='Asia/Jakarta',
        )
        stop_on_jakarta = normalize_isoformat(
            '2019-03-22T23:16:00',
            tz='Asia/Jakarta',
        )
        schedule = {
            'start': {
                'on': start_on_jakarta,
            },
            'periodical': {
                'repeats': 'daily'
                'hour': 23,
                'minute': 15,
                'every': 1,
            },
            'stop': {
                'never': False,
                'on': stop_on_jakarta,
            },
            'timezone': 'Asia/Jakarta',
        }
        schedule_gen = schedule_parser(schedule)

    If start and stop datetime objects signed with some tz (not naive),
    that will be changed according to the timezone from this field.

    If datetime objects are naive, they will be signed with timezone.
    If there is no ``timezone`` — UTC is the default one.
    """
    schedule = validated_schedule(schedule, getters=getters)

    explicit_tz = schedule.get('timezone', 'UTC')
    if now_dt:
        now = normalize_datetime(now_dt, explicit_tz)
    else:
        now = just_now(explicit_tz)

    schedule_date = get_in(['start', 'on'], schedule)
    if schedule_date:
        schedule_date = normalize_datetime(schedule_date, explicit_tz)
    else:
        schedule_date = now

    timeshift_delay = get_in(['start', 'relative_timeshift', 'delay'], schedule)
    timeshift_type = get_in(['start', 'relative_timeshift', 'time_units'], schedule)
    if timeshift_delay and timeshift_type:
        timeshift_modifier = TIMESHIFT_MAP[timeshift_type]
        schedule_date = schedule_date + timeshift_modifier(timeshift_delay)

    periodical_type = get_in(['periodical', 'repeats'], schedule)
    if not periodical_type:
        yield schedule_date

    rrule_params = {'dtstart': schedule_date}

    stop_dt = get_in(['stop', 'on'], schedule)
    if stop_dt:
        stop_dt = normalize_datetime(stop_dt, explicit_tz)
        rrule_params['until'] = stop_dt

    num_repeats = get_in(['stop', 'after_num_repeats'], schedule)
    is_infinite = get_in(['stop', 'never'], schedule)
    if num_repeats and not is_infinite:
        rrule_params['count'] = num_repeats

    if periodical_type:
        rrule_params['freq'] = PERIODICAL_MAP[periodical_type]
        context_params = SENSITIVE_ATTRS_MAP[periodical_type]
        for param in context_params:
            mapped_param = PERIODICAL_ATTRS_MAP[param]
            related_param = get_in(['periodical', param], schedule)
            rrule_params[mapped_param] = related_param

        relative_params = (
            get_in(['periodical', 'relative_day'], schedule) and
            get_in(['periodical', 'relative_day_index'], schedule)
        )

        schedule_gen = rrule(**rrule_params)
        for dt in schedule_gen:
            if dt <= now and not relative_params:
                continue

            if not relative_params:
                yield dt

            if relative_params:
                # basic case for the next planned time shift
                next_dt = relative_datetime_schedule(dt, schedule)
                if next_dt <= schedule_date:
                    continue

                yield next_dt


def relative_datetime_schedule(schedule_date, schedule_struct):
    relative_day = get_in(['periodical', 'relative_day'], schedule_struct)
    relative_day_index = get_in(['periodical', 'relative_day_index'], schedule_struct)
    repeats_type = get_in(['periodical', 'repeats'], schedule_struct)

    if repeats_type == PeriodicalUnits.MONTHLY:
        this_month_range = calendar.monthrange(schedule_date.year, schedule_date.month)
        first_day = schedule_date + relativedelta(day=1)
        _, last_day = this_month_range
        last_day = schedule_date + relativedelta(day=last_day)
    elif repeats_type == PeriodicalUnits.YEARLY:
        last_month_range = calendar.monthrange(schedule_date.year, 12)
        first_day = schedule_date + relativedelta(day=1, month=1)
        _, last_day = last_month_range
        last_day = schedule_date + relativedelta(day=last_day, month=12)

    if relative_day == RelativeUnits.DAY:
        if relative_day_index == RelativeIndexUnits.FIRST:
            schedule_date = first_day
        elif relative_day_index == RelativeIndexUnits.SECOND:
            schedule_date = first_day + relativedelta(day=2)
        elif relative_day_index == RelativeIndexUnits.THIRD:
            schedule_date = first_day + relativedelta(day=3)
        elif relative_day_index == RelativeIndexUnits.FOURTH:
            schedule_date = first_day + relativedelta(day=4)
        elif relative_day_index == RelativeIndexUnits.LAST:
            schedule_date = last_day

    elif relative_day in RELATIVE_DAY_MAP:
        weekday_modifier = RELATIVE_DAY_MAP[relative_day]
        if relative_day_index in {
            RelativeIndexUnits.FIRST,
            RelativeIndexUnits.SECOND,
            RelativeIndexUnits.THIRD,
            RelativeIndexUnits.FOURTH,
        }:
            modifier_shift_map = {
                RelativeIndexUnits.FIRST: +1,
                RelativeIndexUnits.SECOND: +2,
                RelativeIndexUnits.THIRD: +3,
                RelativeIndexUnits.FOURTH: +4,
            }
            base_date = first_day
        elif relative_day_index in {RelativeIndexUnits.LAST}:
            modifier_shift_map = {
                RelativeIndexUnits.LAST: -1,
            }
            base_date = last_day

        schedule_date = base_date + relativedelta(
            weekday=weekday_modifier(modifier_shift_map[relative_day_index])
        )

    elif relative_day in {RelativeUnits.WEEKDAY, RelativeUnits.WEEKEND}:
        if relative_day == RelativeUnits.WEEKDAY:
            is_proper_daytype = is_weekday
        elif relative_day == RelativeUnits.WEEKEND:
            is_proper_daytype = is_weekend

        if relative_day_index in {
            RelativeIndexUnits.FIRST,
            RelativeIndexUnits.SECOND,
            RelativeIndexUnits.THIRD,
            RelativeIndexUnits.FOURTH,
        }:
            days_range = range(1, last_day.day + 1)
            index_unit_slice_map = {
                RelativeIndexUnits.FIRST: 1,
                RelativeIndexUnits.SECOND: 2,
                RelativeIndexUnits.THIRD: 3,
                RelativeIndexUnits.FOURTH: 4,
            }
            base_date = first_day
        elif relative_day_index in {RelativeIndexUnits.LAST}:
            days_range = range(last_day.day, 0, -1)
            index_unit_slice_map = {
                RelativeIndexUnits.LAST: 1,
            }
            base_date = last_day

        weekday_pos = 0
        for day_num in days_range:
            maybe_this_dt = base_date + relativedelta(day=day_num)
            if is_proper_daytype(maybe_this_dt):
                weekday_pos += 1
            if index_unit_slice_map[relative_day_index] == weekday_pos:
                schedule_date = maybe_this_dt
                break

    return schedule_date


def schedule_delta(
    schedule: dict,
    now_dt: t.Optional[datetime.datetime] = None,
    getters: t.Optional[t.List[dict]] = None,
) -> t.Tuple[int, datetime.datetime]:
    schedule_gen = schedule_parser(schedule, now_dt=now_dt, getters=getters)
    explicit_tz = schedule.get('timezone', 'UTC')
    if now_dt:
        now = normalize_datetime(now_dt, explicit_tz)
    else:
        now = just_now(explicit_tz)

    try:
        schedule_dt_base = next(schedule_gen)
    except StopIteration:
        return 0, now

    schedule_seconds = (schedule_dt_base - now).total_seconds()

    if schedule_seconds <= 0:
        try:
            schedule_dt_base = next(schedule_gen)
        except StopIteration:
            return schedule_seconds, now

    schedule_seconds = (schedule_dt_base - now).total_seconds()

    return math.ceil(schedule_seconds), schedule_dt_base
