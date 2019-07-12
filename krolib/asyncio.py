import asyncio
import math
import functools

from krolib.parser import schedule_delta, schedule_parser
from krolib.utils import just_now


def scheduler(schedule=None):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if schedule:
                for dt in schedule_parser(schedule):
                    now = just_now()
                    delay_seconds = math.ceil((dt - now).total_seconds())
                    await asyncio.sleep(delay_seconds)
                    asyncio.create_task(func(*args, **kwargs))
            else:
                asyncio.create_task(func(*args, **kwargs))
        return wrapped
    return wrapper
