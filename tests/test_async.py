import asyncio
import pytest
from voluptuous import Invalid as SchemaInvalid

from krolib.asyncio import scheduler
from krolib.structs import TimeUnits, PeriodicalUnits


pytestmark = pytest.mark.asyncio


async def test_scheduler(event_loop):

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

    await some_coroutine()  # will be printed twice


async def test_scheduler_wrong_struct():

    @scheduler({
        'stop': []
    })
    async def some_coroutine():
        return 'PING'

    with pytest.raises(SchemaInvalid):
        await some_coroutine()


async def test_concurrent_scheduler(event_loop):

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

    # concurrent execution
    await asyncio.gather(some_coroutine(), another_coroutine())
