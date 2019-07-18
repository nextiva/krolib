⏰ Krolib: Schedules for Humans
===============================

[![image](https://img.shields.io/pypi/v/krolib.svg)](https://pypi.org/project/krolib/)
[![image](https://api.travis-ci.com/nextiva/krolib.svg)](https://travis-ci.com/nextiva/krolib/)
[![image](https://img.shields.io/pypi/l/krolib.svg)](https://pypi.org/project/krolib/)
[![image](https://img.shields.io/pypi/pyversions/krolib.svg)](https://pypi.org/project/krolib/)

Magic library and DSL to handle complex schedules.


🚀 Installation
---------------

As easy as usual.

```bash
$ pip install krolib
```

Why?
----

**Cron is not enough**

Yes, you can create almost any kind of schedule rotation or delay for you app
but there are some very special cases when Cron can't help you, like "do
something monthly, every second weekend at 6am until 2020". Also, you can
create only app-level job, what if you need periodical function execution
inside your application?

**Declarative schedule format**

Create your schedules programmatically, serialize them, store in DB, modify,
update in runtime and always have a whole picture of what is the final result.

Readable and flexible structure like:

```python
{
    'timezone': 'Europe/Kiev',
    'start': {
        'relative_timeshift': {
            'delay': 2,
            'time_units': TimeUnits.MONTHS,
        }
    }
}
```

**Supports asyncio out of the box**

Works like magic and very helpful to create periodical coroutines:

```python
from krolib.asyncio import scheduler
from krolib.structs import TimeUnits, PeriodicalUnits


@scheduler({
    'start': {
        'relative_timeshift': {
            'delay': 1,
            'time_units': TimeUnits.SECONDS,
        }
    },
    'periodical': {
        'repeats': PeriodicalUnits.SECONDLY,
        'every': 1,
    },
    'stop': {
        'never': False,
        'after_num_repeats': 2
    }
})
async def some_coroutine():
    print('PING')

await some_coroutine()  # will be delayed and called twice!
```

Delay several coroutines concurrently:

```python
from krolib.asyncio import scheduler
from krolib.structs import TimeUnits, PeriodicalUnits


@scheduler({
    'start': {
        'relative_timeshift': {
            'delay': 1,
            'time_units': TimeUnits.SECONDS,
        }
    },
    'periodical': {
        'repeats': PeriodicalUnits.SECONDLY,
        'every': 1,
    },
    'stop': {
        'never': False,
        'after_num_repeats': 2
    }
})
async def some_coroutine():
    print('PING')

@scheduler({
    'start': {
        'relative_timeshift': {
            'delay': 1,
            'time_units': TimeUnits.SECONDS,
        }
    },
    'periodical': {
        'repeats': PeriodicalUnits.SECONDLY,
        'every': 1,
    },
    'stop': {
        'never': False,
        'after_num_repeats': 2
    }
})
async def another_coroutine():
    print('PONG')

# concurrent execution, get your PING PONG twice!
await asyncio.gather(some_coroutine(), another_coroutine())
```

More examples
-------------

Delay for 1 hour:

```python
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
```

Every last day of the month, infinite:

```python
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
```

Since tomorrow, every week with stop after the second one:

```python
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
```

Schedule Format
---------------
The general schema structure which is currently supported by Krolib is
presented here as a pseudo-Python code.

```python
{
   'start': {
       'on': datetime.datetime,
       'relative_timeshift': {
           'delay': int,
           'time_units': 'seconds/minutes/hours/days/weeks/months',
       }
   },
   'periodical': {
       'repeats': 'yearly/monthly/weekly/daily/hourly/minutely/secondly',
       'every': int,
       'month': 1..12 or None,
       'day': 1..31 or None,
       'weekday': [0..6] or None,
       'hour': 0..23 or None,
       'minute': 0..59 or None,
       'second': 0..59 or None,
   },
   'stop': {
       'never': True or False,
       'on': datetime.datetime,
       'after_num_repeats': int
   },
   'timezone': str or None,
}
```

Also, there is special form for relative periodical rotations:

```python
{
   'start': {
       'on': datetime.datetime,
       'relative_timeshift': {
           'delay': int,
           'time_units': 'seconds/minutes/hours/days/weeks/months',
       }
   },
   'periodical': {
       'repeats': 'yearly/monthly',
       'relative_day': 'day/weekday/weekend/sunday/monday/tuesday/wednesday/thursday/friday/saturday',
       'relative_day_index': 'first/second/third/fourth/last',
       'every': int,
       'hour': 0..23 or None,
       'minute': 0..59 or None,
       'second': 0..59 or None,
   },
   'stop': {
       'never': True or False,
       'on': datetime.datetime,
       'after_num_repeats': int
   },
   'timezone': str or None,
}
```

Schedule structure
------------------

The schedule data structure has three main sections:

- start
- periodical
- stop

The schedule structure also holds a `timezone` attribute, which sets the
timezone for all the sections of the schedule. It should hold a string with the
timezone identifier, for example `Europe/Kiev`. Supported list of the timezones
could be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

Please take into account, that timezone validation and processing utilizes
`pytz` library, so finally you might want to dig into the sources of this
library in case if you face any troubles.

### Start section

Start section is used to specify the exact time or delay before the rule or
block starts/continues it's execution (processing).

**`on` key**

This key holds the exact time (datetime object) when to start the
execution/processing. When this key is set, values in the `relative_timeshift`
section should not be filled with any values.


```python
{
    'start': {
        'on': datetime.datetime.utcnow(),
    }
}
```

**`relative_timeshift` key**

This key holds an object with two keys — `delay` and `time_units`.

`delay` holds a string with an integer in it for the amount of time units.

`time_units` holds a string with one of the values:

- seconds
- minutes
- hours
- days
- weeks
- months

When the relative timeshift is set, both delay and time_units should hold the
proper values.

Example of this kind of start section with the delay for 3 days:

```python
{
    'start': {
        'relative_timeshift': {
            'delay': '3',
            'time_units': 'days',
        }
    }
}
```

### Periodical section

The periodical section is used to describe a schedule with the recurring
events. If you use this section, you should also set the values in the stop
section of the schedule data structure.

**`repeats` key**

This key holds the type of repeats:

- yearly
- monthly
- weekly
- daily
- hourly
- minulety
- secondly

Example of yearly repeats on September, 3-rd at 20:30:

```python
{
    'periodical': {
        'repeats': 'yearly',
        'every': 1,
        'month': 9,
        'day': 3,
        'hour': 20,
        'minute': 30,
    }
}
```

**`every` key**

This key gives additional flexibility for repeats. It holds a non-negative
integer greater than zero (a natural number) and is used to calculate skips.

For example, for daily repeats the every key could be set to 1 — this would
mean every day repeats, to 3 — this would mean skip two days, then execute
every third day, skip two days again, etc.

```python
{
    'periodical': {
        'repeats': 'daily',
        'every': 5,
        'hour': 20,
        'minute': 30,
    }
}
```

**`month`, `day`, `hour`, `minute` and `second` keys**

These keys hold integers which correspond to appropriate key. For example, 1-12
(inclusive) for month, 1-31 (inclusive) for day and so on.

**`weekday` key**

This key holds the information about the weekdays for the recurring event.
Valid weekday range is from 0 to 6 where 0 is Monday and 6 is Sunday.

Example of weekly repeats (every week without skipping) on Mondays and Fridays
at 15.00:

```python
{
    'periodical': {
        'repeats': 'weekly',
        'every': 1,
        'weekday': [0, 4],
        'hour': 15,
        'minute': 0,
    }
}
```

### Relative days case

For `monthly` and `yearly` values of the `repeats` key, altenative relative
days schedule could be set.

In this case the `day` and `weekday` keys should not be set and `relative_day`
and `relative_day_index` should be. These keys indicate some relative day of
the month.

**`relative_day` key**

This field should hold the string with one of the following values:

- day
- weekday
- weekend
- sunday
- monday
- tuesday
- wednesday
- thursday
- friday
- saturday

**`relative_day_index` key**

This field should hold a string with one of the following values:

- first
- second
- third
- fourth
- last

Example of monthly repeats on the third Friday of the month at 15.00:

```python
{
    'periodical': {
        'repeats': 'monthly',
        'every': 1,
        'hour': 15,
        'minute': 0,
        'relative_day': 'friday',
        'relative_day_index': 'third'
    }
}
```

### Stop section

This section is obligatory. It holds information about when to stop the
recurring event execution. Has `never`, `on` and `after_num_repeats` keys.

**`never` key**

This key holds a boolean value. If set to `True` — other keys of this section
should not hold any values, because this means that recurring event will never
stop it's execution. If set to `False` — other keys should be also set.

Stop section with never ending repeats:

```python
{
    'stop': {
        'never': True,
    }
}
```

**`on` key**

This key holds exact time (datetime object) when to stop the recurring:

```python
{
    'stop': {
        'never': False,
        'on': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
}
```

**`after_num_repeats` key**

This key holds an integer indicating amount of times to repeat the recurring
schedule.

Stop section with stop after 25 times executing/processing smth:

```python
{
    'stop': {
        'never': False,
        'after_num_repeats': 25
    }
}
```

🤝 Special Thanks
-----------------

- Alexander Omyshev [@akalex](https://github.com/akalex)
- Dmitry Nikonenko [@ndmytro](https://github.com/ndmytro)
- Phil Steitz [@psteitz](https://github.com/psteitz)
- Ralph Goers [@rgoers](https://github.com/rgoers)
- Vitalii Iaskal [@vavilon17](https://github.com/vavilon17)

📝 License
----------

Published under Apache Software License 2.0, see [LICENSE](LICENSE) file.
