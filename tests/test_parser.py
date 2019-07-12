import datetime

import pytest
import pytz
from voluptuous import Invalid as SchemaInvalid

from dateutil.relativedelta import relativedelta
from toolz.dicttoolz import dissoc

from krolib.utils import (
    just_now,
    normalize_datetime,
    normalize_isoformat,
)
from krolib.parser import (
    schedule_parser,
    schedule_delta,
)
from krolib.structs import (
    PeriodicalUnits,
    TimeUnits,
    RelativeUnits,
    RelativeIndexUnits,
    WeekdayUnits,
    MonthUnits,
)


@pytest.mark.unit
class TestStartTimeshiftDelay:

    def test_seconds_delay(self):
        now = just_now()
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.SECONDS,
                }
            },
            'stop': {
                'never': True,
            }
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 1

    def test_minutes_delay(self):
        now = just_now()
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.MINUTES,
                }
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 60

    def test_hours_delay(self):
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
        assert (result - now).total_seconds() == 3600

    def test_days_delay(self):
        now = just_now()
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.DAYS,
                }
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 86400

    def test_weeks_delay(self):
        now = just_now()
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.WEEKS,
                }
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 604800

    def test_months_delay(self):
        now = just_now()
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.MONTHS,
                }
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 2419200

    def test_invalid_delay(self):
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': 'invalid'
                }
            },
        }
        with pytest.raises(SchemaInvalid):
            schedule_gen = schedule_parser(schedule)
            next(schedule_gen)


@pytest.mark.unit
class TestStartDateDelay:

    def test_absolute_day_delay(self):
        now = just_now()
        start_on = now + datetime.timedelta(days=1)
        schedule = {
            'start': {
                'on': start_on,
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 86400

    def test_absolute_day_with_shift_delay(self):
        now = just_now()
        start_on = now + datetime.timedelta(days=1)
        schedule = {
            'start': {
                'on': start_on,
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.SECONDS,
                }
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 86401

    def test_absolute_past_day_delay(self):
        now = just_now()
        start_on = now + datetime.timedelta(days=-1)
        schedule = {
            'start': {
                'on': start_on,
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert result == start_on


@pytest.mark.unit
class TestPeriodicalSchedule:

    def test_secondly_periodical(self):
        now = just_now()
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.SECONDLY,
                'every': 1,
            },
        }
        schedule_gen = schedule_parser(schedule)
        results = [next(schedule_gen) for _ in range(3)]
        deltas = [(x - now).total_seconds() for x in results]
        assert deltas == [1, 2, 3]

    def test_minutely_periodical(self):
        now = just_now()
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MINUTELY,
                'every': 1,
            },
        }
        schedule_gen = schedule_parser(schedule)
        results = [next(schedule_gen) for _ in range(3)]
        deltas = [(x - now).total_seconds() for x in results]
        assert deltas == [60, 120, 180]

    def test_hourly_periodical(self):
        now = just_now()
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.HOURLY,
                'every': 1,
            },
        }
        schedule_gen = schedule_parser(schedule)
        results = [next(schedule_gen) for _ in range(3)]
        deltas = [(x - now).total_seconds() for x in results]
        assert deltas == [3600, 7200, 10800]

    def test_daily_periodical(self):
        now = just_now()
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.DAILY,
                'every': 1,
            },
        }
        schedule_gen = schedule_parser(schedule)
        results = [next(schedule_gen) for _ in range(3)]
        deltas = [(x - now).total_seconds() / 24 for x in results]
        assert deltas == [3600, 7200, 10800]

    def test_weekly_periodical(self):
        now = just_now()
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.WEEKLY,
                'every': 1,
            },
        }
        schedule_gen = schedule_parser(schedule)
        results = [next(schedule_gen) for _ in range(3)]
        deltas = [(x - now).total_seconds() / 7 / 24 for x in results]
        assert deltas == [3600, 7200, 10800]

    def test_monthly_periodical(self):
        now = datetime.datetime(2018, 5, 20, 12, 30, 0, tzinfo=pytz.UTC)
        next_month = now + relativedelta(months=+1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MONTHLY,
                'every': 1,
                'day': 20,
                'hour': 12,
                'minute': 30
            },
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        result = next(schedule_gen)
        assert next_month == result.replace(second=0)

    def test_yearly_periodical(self):
        now = just_now()
        next_year = now + relativedelta(years=+1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.YEARLY,
                'every': 1,
            },
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert next_year == result

    def test_yearly_concrete_periodical(self):
        now = datetime.datetime(2018, 5, 28, tzinfo=pytz.UTC)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.YEARLY,
                'every': 1,
                'month': MonthUnits.JANUARY,
                'day': 1,
                'hour': 12,
                'minute': 30,
            },
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2019, 1, 1, 12, 30, tzinfo=pytz.UTC),
            datetime.datetime(2020, 1, 1, 12, 30, tzinfo=pytz.UTC),
            datetime.datetime(2021, 1, 1, 12, 30, tzinfo=pytz.UTC),
        ]

    def test_monthly_concrete_periodical(self):
        now = datetime.datetime(2018, 1, 1, tzinfo=pytz.UTC)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MONTHLY,
                'every': 1,
                'weekday': [WeekdayUnits.FRIDAY],
                'day': 13,
            },
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2018, 4, 13, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 7, 13, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2019, 9, 13, 0, 0, tzinfo=pytz.UTC),
        ]

    def test_weekly_concrete_periodical(self):
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

    def test_daily_concrete_periodical(self):
        now = datetime.datetime(2018, 5, 1, 1, 20, 45, tzinfo=pytz.UTC)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.DAILY,
                'every': 2,
                'hour': 1,
                'minute': 30,
                'second': 45,
            }
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(4)]
        assert results == [
            datetime.datetime(2018, 5, 1, 1, 30, 45, tzinfo=pytz.UTC),
            datetime.datetime(2018, 5, 3, 1, 30, 45, tzinfo=pytz.UTC),
            datetime.datetime(2018, 5, 5, 1, 30, 45, tzinfo=pytz.UTC),
            datetime.datetime(2018, 5, 7, 1, 30, 45, tzinfo=pytz.UTC),
        ]


@pytest.mark.unit
class TestRelativeSchedule:

    def test_relative_first_monday_monthly(self):
        now = datetime.datetime(year=2018, month=5, day=1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MONTHLY,
                'relative_day': RelativeUnits.MONDAY,
                'relative_day_index': RelativeIndexUnits.FIRST,
            },
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2018, 5, 7, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 6, 4, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 7, 2, 0, 0, tzinfo=pytz.UTC),
        ]

    def test_relative_first_monday_yearly(self):
        now = datetime.datetime(year=2018, month=5, day=1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.YEARLY,
                'relative_day': RelativeUnits.MONDAY,
                'relative_day_index': RelativeIndexUnits.FIRST,
            }
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2019, 1, 7, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2020, 1, 6, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2021, 1, 4, 0, 0, tzinfo=pytz.UTC),
        ]

    def test_relative_last_monday_monthly(self):
        now = datetime.datetime(year=2018, month=5, day=1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MONTHLY,
                'relative_day': RelativeUnits.MONDAY,
                'relative_day_index': RelativeIndexUnits.LAST,
            },
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2018, 5, 28, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 6, 25, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 7, 30, 0, 0, tzinfo=pytz.UTC),
        ]

    def test_relative_first_weekday_monthly(self):
        now = datetime.datetime(year=2018, month=5, day=1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MONTHLY,
                'hour': 1,
                'relative_day': RelativeUnits.WEEKDAY,
                'relative_day_index': RelativeIndexUnits.FIRST,
            }
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2018, 5, 1, 1, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 6, 1, 1, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 7, 2, 1, 0, tzinfo=pytz.UTC),
        ]

    def test_relative_first_weekend_monthly(self):
        now = datetime.datetime(year=2018, month=1, day=1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.MONTHLY,
                'relative_day': RelativeUnits.WEEKEND,
                'relative_day_index': RelativeIndexUnits.FIRST,
            }
        }
        schedule_gen = schedule_parser(schedule, now_dt=now)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            datetime.datetime(2018, 1, 6, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 2, 3, 0, 0, tzinfo=pytz.UTC),
            datetime.datetime(2018, 3, 3, 0, 0, tzinfo=pytz.UTC),
        ]

    def test_relative_last_day_monthly(self):
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

    def test_yearly_with_stop_periodical(self):
        now = just_now()
        next_year = now + relativedelta(years=+1)
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.YEARLY,
                'every': 1,
            },
            'stop': {
                'on': now + datetime.timedelta(days=400),
                'never': False
            }
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert next_year == result

        with pytest.raises(StopIteration):
            next(schedule_gen)

    def test_weekly_with_repeats_periodical(self):
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


@pytest.mark.unit
class TestTimeUtils:

    def test_timezone_eq(self):
        aware_local = just_now(tz='Europe/Kiev')
        unaware_utc = datetime.datetime.utcnow()
        aware_utc = just_now()

        n_aware_local = normalize_datetime(aware_local)
        n_unaware_utc = normalize_datetime(unaware_utc)
        n_aware_utc = normalize_datetime(aware_utc)

        assert n_aware_local == n_unaware_utc == n_aware_utc

    def test_normalizers_eq(self):
        dt_obj = datetime.datetime(2018, 5, 26, 11, 45)
        dt_str = '2018-05-26T11:45'
        assert normalize_datetime(dt_obj) == normalize_isoformat(dt_str)


@pytest.mark.unit
class TestMixedSchedule:

    def test_kiev_timezone_apply(self):
        now = just_now()
        start_on = now + datetime.timedelta(days=1)
        schedule = {
            'start': {
                'on': start_on,
            },
            'timezone': 'Europe/Kiev',
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)
        assert (result - now).total_seconds() == 86400

    def test_jakarta_timezone_apply(self):
        now_in_kiev = normalize_isoformat(
            '2019-03-05T17:00:00',
            tz='Europe/Kiev',
        )
        start_on_jakarta = normalize_isoformat(
            '2019-03-05T22:00:00',
            tz='Asia/Jakarta',
        )

        assert not bool(start_on_jakarta - now_in_kiev)  # same time

        start_on_jakarta = normalize_isoformat(
            '2019-03-05T15:05:00',
        )

        schedule = {
            'start': {
                'on': start_on_jakarta,
                'relative_timeshift': {
                    'delay': None,
                    'time_units': None,
                }
            },
            'stop': {
                'on': None,
                'never': None,
                'after_num_repeats': None,
            },
            'timezone': "Asia/Jakarta"
        }
        schedule_gen = schedule_parser(schedule)
        result = next(schedule_gen)

        assert (result - now_in_kiev).seconds == 300

    def test_different_timezones(self):
        now = just_now(tz=None)
        start_on = now + datetime.timedelta(days=1)
        kyiv_schedule = {
            'start': {
                'on': start_on,
            },
            'timezone': 'Europe/Kiev',
        }
        kyiv_schedule_gen = schedule_parser(kyiv_schedule)
        kyiv_result = next(kyiv_schedule_gen)

        warsaw_schedule = {
            'start': {
                'on': start_on,
            },
            'timezone': 'Europe/Warsaw',
        }
        warsaw_schedule_gen = schedule_parser(warsaw_schedule)
        warsaw_result = next(warsaw_schedule_gen)

        assert (warsaw_result - kyiv_result).total_seconds() == 3600

    def test_start_periodical_same_time(self):
        now = just_now(tz='Europe/Kiev')
        start_on = now + datetime.timedelta(days=1)
        start_on = start_on.replace(hour=11, minute=45)

        schedule = {
            'timezone': 'Europe/Kiev',
            'start': {
                'on': start_on,
            },
            'periodical': {
                'repeats': 'daily',
                'every': 1,
                'hour': 11,
                'minute': 45,
            },
            'stop': {
                'never': True,
            }
        }
        schedule_gen = schedule_parser(schedule)
        results = [next(schedule_gen) for _ in range(3)]
        assert results == [
            start_on,
            start_on + datetime.timedelta(days=1),
            start_on + datetime.timedelta(days=2),
        ]

    def test_periodical_time_for_custom_tz(self):
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
                'repeats': PeriodicalUnits.DAILY,
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
        schedule_gen = schedule_parser(schedule, now_dt=start_on_jakarta)
        results = list(schedule_gen)
        assert [s.tzname() for s in results] == ['WIB', 'WIB', 'WIB']

        one, two, three = results
        assert (one - start_on_jakarta).total_seconds() == 4500  # 75 minutes, start
        assert (two - one).total_seconds() == 86400  # 1 day
        assert (three - two).total_seconds() == 86400  # 1 day
        assert three == normalize_isoformat('2019-03-22T23:15:00', tz='Asia/Jakarta')


@pytest.mark.unit
class TestScheduleDelta:

    def test_hours_delay_delta(self):
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': 1,
                    'time_units': TimeUnits.HOURS,
                }
            },
        }
        delta, _ = schedule_delta(schedule)
        assert delta == 3600

    def test_delta_with_delay(self):
        schedule = {
            'start': {
                'relative_timeshift': {
                    'delay': '1',
                    'time_units': TimeUnits.DAYS,
                }
            },
            'periodical': {
                'repeats': PeriodicalUnits.HOURLY,
                'every': 1,
            },
            'timezone': 'Europe/Kiev',
        }
        delta, _ = schedule_delta(schedule)
        abs_delta, _ = schedule_delta(dissoc(schedule, 'start'))
        assert delta == 86400
        assert abs_delta == 3600

    def test_delta_with_stop(self):
        now = just_now()
        schedule = {
            'periodical': {
                'repeats': PeriodicalUnits.YEARLY,
                'every': 1,
            },
            'stop': {
                'on': now + datetime.timedelta(days=1),
                'never': False
            }
        }
        delta, _ = schedule_delta(schedule)
        assert delta == 0
