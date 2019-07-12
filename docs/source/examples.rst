Examples
========

.. toctree::
   :maxdepth: 3


The ``schedule_parser`` is datetime objects generator 
that works with proposed structure. Schedules list can be infinite,
that's why it is a generator.


Schedules generator usage
-------------------------

Delay for 1 hour::

    from krolib.utils import just_now
    from krolib.parser import schedule_parser
    from krolib.structs import TimeUnits

    now = just_now()
    schedule = {
        'start': {
            'relative_timeshift': {
                'delay': 1,
                'time_units': TimeUnits.HOURS,
            }
        },
    }
    schedule_gen = schedule_parser(schedule)
    result = next(schedule_gen)
    assert (result - now).total_seconds() == 3600  # seconds


Every last day of the month, infinite::

    import datetime
    import pytz

    from krolib.structs import (
        PeriodicalUnits,
        RelativeUnits,
        RelativeIndexUnits,
    )
    from krolib.parser import schedule_parser

    # today is this date, for example
    now = datetime.datetime(year=2018, month=1, day=1)

    schedule = {
        'periodical': {
            'repeats': PeriodicalUnits.MONTHLY,
            'relative_day': RelativeUnits.DAY,
            'relative_day_index': RelativeIndexUnits.LAST,
        }
    }
    schedule_gen = schedule_parser(schedule, now_dt=now)
    results = [next(schedule_gen) for _ in range(3)]
    assert results == [
        datetime.datetime(2018, 1, 31, 0, 0, tzinfo=pytz.UTC),
        datetime.datetime(2018, 2, 28, 0, 0, tzinfo=pytz.UTC),
        datetime.datetime(2018, 3, 31, 0, 0, tzinfo=pytz.UTC),
    ]


Every week, on Monday and Tuesday at 23:15:30, infinite::

    import datetime
    import pytz

    from krolib.structs import (
        PeriodicalUnits,
        WeekdayUnits,
    )
    from krolib.parser import schedule_parser

    # today is this date, for example
    now = datetime.datetime(2018, 5, 1, tzinfo=pytz.UTC)

    schedule = {
        'periodical': {
            'repeats': PeriodicalUnits.WEEKLY,
            'every': 1,
            'weekday': [WeekdayUnits.MONDAY, WeekdayUnits.TUESDAY],
            'hour': 23,
            'minute': 15,
            'second': 30,
        }
    }
    schedule_gen = schedule_parser(schedule, now_dt=now)
    results = [next(schedule_gen) for _ in range(3)]
    assert results == [
        datetime.datetime(2018, 5, 1, 23, 15, 30, tzinfo=pytz.UTC),
        datetime.datetime(2018, 5, 7, 23, 15, 30, tzinfo=pytz.UTC),
        datetime.datetime(2018, 5, 8, 23, 15, 30, tzinfo=pytz.UTC),
    ]


Since tomorrow, every week with stop after the second one::

    import datetime

    from krolib.utils import just_now
    from krolib.parser import schedule_parser
    from krolib.structs import PeriodicalUnits

    now = just_now()
    start_on = now + datetime.timedelta(days=1)
    schedule = {
        'start': {
            'on': start_on,
        },
        'periodical': {
            'repeats': PeriodicalUnits.WEEKLY,
            'every': 1,
        },
        'stop': {
            'never': False,
            'after_num_repeats': 2
        }
    }
    schedule_gen = schedule_parser(schedule)
    one_dt, two_dt = list(schedule_gen)
    assert one_dt == start_on
    assert (two_dt - one_dt).days == 7
