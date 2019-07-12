Schedule Format
===============

.. toctree::
   :maxdepth: 3


Here is the structure that currently supported by the Krolib::

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


Also, there is special form for relative periodical rotations::

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


Schedule structure
------------------

The schedule data structure has three main sections:

    * start
    * periodical
    * stop

The schedule structure also holds a ``timezone`` attribute, which sets the timezone for
all the sections of the schedule. It should hold a string with the timezone identifier, for
example 'Europe/Kiev', the list of the timezones could be found 
`here <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_.

Please take into account, that timezone validation and processing utilizes ``pytz`` library, so
finally you might want to dig into the sources of this library in case if you face any troubles:
https://pypi.org/project/pytz, https://github.com/newvem/pytz.


The start section
-----------------

Start section is used to specify the exact time or delay before the rule or block
starts/continues it's execution (processing).

**The on key**

This key holds the exact time (datetime object) when to start the execution/processing.
When this key is set, values in the ``relative_timeshift`` section should not be filled with
any values. The example of this kind of ``start`` section::

    {
        'start': {
            'on': datetime.datetime.utcnow(),
        }
    }

**The relative_timeshift key**

This key holds an object with two keys - ``delay`` and ``time_units``.
``delay`` holds a string with an integer in it for the amount of time units.
``time_units`` holds a string with one of the values:

    * seconds
    * minutes
    * hours
    * days
    * weeks
    * months

When the relative timeshift is set, both ``delay`` and ``time_units`` should hold the proper values.
The example of this kind of ``start`` section with the delay for 3 days::

    {
        'start': {
            'relative_timeshift': {
                'delay': '3',
                'time_units': 'days',
            }
        }
    }


The periodical section
----------------------

The periodical section is used to describe a schedule with the recurring events. If you use this
section, you should also set the values in the stop section of the schedule data structure.

**The repeats key**

This key holds the type of repeats:

    * yearly
    * monthly
    * weekly
    * daily
    * hourly
    * minulety
    * secondly

The example of the yearly repeats on September, 3-rd at 20:30::

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

**The every key**

This key gives additional flexibility for the repeats. It holds a non-negative integer greater
than zero (a natural number) and is used to calculate skips.

For example, for the daily repeats the *every* key could be set to 1 - this would mean
**every day** repeats, to 3 - this would mean skip two days, then execute **every third day** then
skip two days again, etc.

The example of the daily repeats at 20:30 with 4 days skip::

    {
        'periodical': {
            'repeats': 'daily',
            'every': 5,
            'hour': 20,
            'minute': 30,
        }
    }

**The month, day, hour, minute and second keys**

These keys hold integers which correspond to appropriate key.
For example, 1-12 (inclusive) for month, 1-31 (inclusive) for day and so on.

**The weekday key**

This key holds the information about the weekdays for the recurring event.

Valid weekday range is from 0 to 6 where 0 is Monday and 6 is Sunday.

The example of the weekly repeats (every week without skipping) on Mondays and Fridays
at 15.00::

    {
        'periodical': {
            'repeats': 'weekly',
            'every': 1,
            'weekday': [0, 4],
            'hour': 15,
            'minute': 0,
        }
    }


**Relative days case**

For *monthly* and *yearly* values of the ``repeats``, the altenative relative days schedule could
be set. In this case the **day** and **weekday** key is not set, instead the **relative_day**
and **relative_day_index** should be set. These keys indicate the relative day of the month.
For example, the **first Wednesday**, the **second weekend**, the **last Monday** of the month.

**The relative_day key**

This field should hold the string with one of the following values:

    * day
    * weekday
    * weekend
    * sunday
    * monday
    * tuesday
    * wednesday
    * thursday
    * friday
    * saturday

**The relative_day_index key**

This field should hold a string with one of the following values:

    * first
    * second
    * third
    * fourth
    * last

The example of monthly repeats on the third Friday of the month at 15.00::

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


The stop section
----------------

This section is obligatory the periodical section is provided within the schedule.
It holds the information on when to stop the recurring event execution.
It has the **never**, **on** and **after_num_repeats** keys.

**The never key**

This key holds a boolean value. If set to ``True`` - the other keys of this section
should not hold any values, because this means, that recurring event will never stop
it's execution. If set to ``False`` - the other keys should be also set.

The example of the stop section with never ending repeats::

    {
        'stop': {
            'never': True,
        }
    }

**The on key**

This key holds the exact time (datetime object) when to stop the recurring::

    {
        'stop': {
            'never': False,
            'on': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
    }

**The after_num_repeats key**

This key holds an integer indicating the amount of times to repeat the recurring schedule.

The example of the stop section with the stop after 25 times executing/processing smth::

    {
        'stop': {
            'never': False,
            'after_num_repeats': 25
        }
    }


More schedule structure examples
--------------------------------

The schedule with the following information:

    * start on '2019-01-01T00:00:00'
    * repeat monthly on 20-th day at 14:50
    * stop after 6 executions

should look like::

    {
        'timezone': 'Europe/Kiev',
        'start': {
            'on': datetime.datetime(year=2019, month=1, day=1),
        }
        'periodical': {
            'repeats': 'monthly',
            'every': 1,
            'day': 20,
            'hour': 14,
            'minute': 50,
        }
        'stop': {
            'never': False,
            'after_num_repeats': 6
        }
    }

As you can see, the sections are configured independently,
though stop section should always be set if the periodical section is set.

The schedule with the following information:

    * start with 2 month delay

should look like::

    {
        'timezone': 'Europe/Kiev',
        'start': {
            'relative_timeshift': {
                'delay': '2',
                'time_units': 'months',
            }
        }
    }

The schedule with the following information:

    * start on '2019-01-01T00:00:00'
    * repeat every 2-nd Monday of the month at 14:50
    * stop on '2020-01-01T00:00:00'

should look like::

    {
        'timezone': 'Europe/Kiev',
        'start': {
            'on': datetime.datetime(year=2019, month=1, day=1),
        }
        'periodical': {
            'repeats': 'monthly',
            'every': 1,
            'hour': 14,
            'minute': 50,
            'relative_day': 'monday',
            'relative_day_index': 'second'
        }
        'stop': {
            'never': False,
            'on': datetime.datetime(year=2020, month=1, day=1),
        }
    }

The schedule with the following information:

    * start on '2019-01-01T00:00:00'
    * repeat on Wednesday and Friday of every third week at 14:50
    * stop on '2020-01-01T00:00:00'

should look like::

    {
        'timezone': 'Europe/Kiev',
        'start': {
            'on': datetime.datetime(year=2019, month=1, day=1),
        }
        'periodical': {
            'repeats': 'weekly',
            'every': 3,
            'weekday': [2, 4],
            'hour': 14,
            'minute': 50,
        }
        'stop': {
            'never': False,
            'on': datetime.datetime(year=2020, month=1, day=1),
        }
    }
