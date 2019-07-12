.. Krolib documentation master file, created by
   sphinx-quickstart on Wed Apr 10 16:42:05 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. title:: Krolib


Welcome to Krolib's documentation!
==================================

So, you want schedules in your app? Why do you need Krolib?


**Cron is not enough**

Yes, you can create almost any kind of schedule rotation or delay 
for you app but there are some very special cases when Cron can't help you,
like "do something monthly, every second weekend at 6am until 2020". Also,
you can create only app-level job, what if you need periodical function execution
inside your application?


**Declarative schedule format**

Create your schedules programmatically, serialize them, store in DB,
modify, update in runtime and always have a whole picture of what is the final result.

Readable and flexible structure like::

    {
        'timezone': 'Europe/Kiev',
        'start': {
            'relative_timeshift': {
                'delay': 2,
                'time_units': TimeUnits.MONTHS,
            }
        }
    }


**Supports asyncio out of the box**

Works like magic and very helpful to create periodical coroutines::

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


Want to delay several coroutines concurrently? Not a problem::

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


Dive into schedule format section and look into examples to see 
how powerful it is!

.. toctree::
   :maxdepth: 3
   :titlesonly:

   format
   examples
   api
