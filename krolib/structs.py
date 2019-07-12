import collections
import datetime

import pytz
import voluptuous as v

from dateutil.relativedelta import (
    MO,
    TU,
    WE,
    TH,
    FR,
    SA,
    SU,
)


TimeUnits = collections.namedtuple(
    'TimeUnits', [
        'SECONDS',
        'MINUTES',
        'HOURS',
        'DAYS',
        'WEEKS',
        'MONTHS',
    ]
)(
    SECONDS='seconds',
    MINUTES='minutes',
    HOURS='hours',
    DAYS='days',
    WEEKS='weeks',
    MONTHS='months',
)

PeriodicalUnits = collections.namedtuple(
    'PeriodicalUnits', [
        'YEARLY',
        'MONTHLY',
        'WEEKLY',
        'DAILY',
        'HOURLY',
        'MINUTELY',
        'SECONDLY',
    ]
)(
    YEARLY='yearly',
    MONTHLY='monthly',
    WEEKLY='weekly',
    DAILY='daily',
    HOURLY='hourly',
    MINUTELY='minutely',
    SECONDLY='secondly',
)

RelativeUnits = collections.namedtuple(
    'RelativeUnits', [
        'DAY',
        'WEEKDAY',
        'WEEKEND',
        'SUNDAY',
        'MONDAY',
        'TUESDAY',
        'WEDNESDAY',
        'THURSDAY',
        'FRIDAY',
        'SATURDAY',
    ]
)(
    DAY='day',
    WEEKDAY='weekday',
    WEEKEND='weekend',
    SUNDAY='sunday',
    MONDAY='monday',
    TUESDAY='tuesday',
    WEDNESDAY='wednesday',
    THURSDAY='thursday',
    FRIDAY='friday',
    SATURDAY='saturday',
)

RelativeIndexUnits = collections.namedtuple(
    'RelativeIndexUnits', [
        'FIRST',
        'SECOND',
        'THIRD',
        'FOURTH',
        'LAST',
    ]
)(
    FIRST='first',
    SECOND='second',
    THIRD='third',
    FOURTH='fourth',
    LAST='last',
)

WeekdayUnits = collections.namedtuple(
    'WeekdayUnits', [
        'MONDAY',
        'TUESDAY',
        'WEDNESDAY',
        'THURSDAY',
        'FRIDAY',
        'SATURDAY',
        'SUNDAY',
    ]
)(
    MONDAY=MO.weekday,
    TUESDAY=TU.weekday,
    WEDNESDAY=WE.weekday,
    THURSDAY=TH.weekday,
    FRIDAY=FR.weekday,
    SATURDAY=SA.weekday,
    SUNDAY=SU.weekday,
)

MonthUnits = collections.namedtuple(
    'MonthUnits', [
        'JANUARY',
        'FEBRUARY',
        'MARCH',
        'APRIL',
        'MAY',
        'JUNE',
        'JULY',
        'AUGUST',
        'SEPTEMBER',
        'OCTOBER',
        'NOVEMBER',
        'DECEMBER',
    ]
)(
    JANUARY=1,
    FEBRUARY=2,
    MARCH=3,
    APRIL=4,
    MAY=5,
    JUNE=6,
    JULY=7,
    AUGUST=8,
    SEPTEMBER=9,
    OCTOBER=10,
    NOVEMBER=11,
    DECEMBER=12,
)

GettersSchema = v.Schema([
    {
        v.Required('getter'): object,
        'params': dict
    }
])

StartSection = {
    'on': v.Maybe(datetime.datetime),
    'relative_timeshift': {
        v.Required('delay'): v.Maybe(
            v.All(
                v.Coerce(int, msg='Invalid start timeshift delay value, an integer expected'),
                v.Range(min=1)
            )
        ),
        v.Required('time_units'): v.Maybe(
            v.All(
                str, v.In(set(TimeUnits),
                            msg='Invalid start timeshift unit value, one of %s expected' % (
                    ', '.join(['"%s"' % x for x in tuple(TimeUnits)])
                )),
            ),
        )
    }
}

StopSection = {
    v.Required('never'): v.Maybe(v.Boolean()),
    'on': v.Maybe(datetime.datetime),
    'after_num_repeats': v.Maybe(v.All(int, v.Range(min=1))),
}


RelativeScheduleSchema = v.Schema({
    'start': StartSection,
    'stop': StopSection,
    v.Required('periodical'): {
        v.Required('repeats'): v.Maybe(
            v.All(
                str,
                v.In({
                    PeriodicalUnits.MONTHLY, PeriodicalUnits.YEARLY},
                    msg='Relative datetime can be with %s rotation type only' % (
                        ' or '.join(
                            '"%s"' % x for x in (PeriodicalUnits.MONTHLY, PeriodicalUnits.YEARLY)
                        ))
                )
            ),
        ),
        v.Required('relative_day'): v.All(str, v.In(set(RelativeUnits))),
        v.Required('relative_day_index'): v.All(str, v.In(set(RelativeIndexUnits))),
        v.Optional('every', default=1): v.Maybe(v.All(int, v.Range(min=1))),
        'hour': v.Maybe(v.All(int, v.Range(min=0, max=23))),
        'minute': v.Maybe(v.All(int, v.Range(min=0, max=59))),
        'second': v.Maybe(v.All(int, v.Range(min=0, max=59))),
    },
    'timezone': v.Maybe(v.All(str, v.In(pytz.all_timezones_set)))
})

ScheduleSchema = v.Schema({
    'start': StartSection,
    'stop': StopSection,
    'periodical': {
        v.Required('repeats'): v.Maybe(v.All(str, v.In(set(PeriodicalUnits)))),
        v.Optional('every', default=1): v.Maybe(v.All(int, v.Range(min=1))),
        'month': v.Maybe(v.All(int, v.Range(min=1, max=12))),
        'day': v.Maybe(v.All(int, v.Range(min=1, max=31))),
        'weekday': v.Maybe([v.All(int, v.Range(min=0, max=6))]),
        'hour': v.Maybe(v.All(int, v.Range(min=0, max=23))),
        'minute': v.Maybe(v.All(int, v.Range(min=0, max=59))),
        'second': v.Maybe(v.All(int, v.Range(min=0, max=59))),
        'relative_day': v.Maybe(v.All(str, v.In(set(RelativeUnits)))),
        'relative_day_index': v.Maybe(v.All(str, v.In(set(RelativeIndexUnits)))),
    },
    'timezone': v.Maybe(v.All(str, v.In(pytz.all_timezones_set)))
})
