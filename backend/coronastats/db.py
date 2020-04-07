import datetime
import typing

from flask import current_app
from peewee import (
    SqliteDatabase,
    Model,
    DateField,
    AutoField,
    IntegerField,
    JOIN,
    fn,
    Value,
    CharField,
    ForeignKeyField,
)

database = SqliteDatabase(current_app.config["DATABASE_PATH"])


class BaseModel(Model):
    class Meta:
        database = database


class CoronaLog(BaseModel):
    id = AutoField()
    datetime = DateField(default=datetime.date.today(), unique=True, index=True)
    infected = IntegerField(default=0)
    cured = IntegerField(default=0)
    tests = IntegerField(default=0)
    deaths = IntegerField(default=0)


class CoronaLocation(BaseModel):
    id = AutoField()
    location = CharField(index=True)
    last_updated = DateField(default=datetime.date.today())


class CoronaLocationLog(BaseModel):
    id = AutoField()
    date = DateField(default=datetime.date.today(), index=True)
    infected = IntegerField(default=0)
    infected_females = IntegerField(default=0)
    cured = IntegerField(default=0)
    tests = IntegerField(default=0)
    deaths = IntegerField(default=0)
    location = ForeignKeyField(CoronaLocation, backref="data")


def add_corona_log(
    infected: int,
    cured: int,
    tests: int,
    deaths: int = 0,
    date_: typing.Optional[datetime.date] = None,
) -> CoronaLog:
    if not date_:
        date_ = datetime.date.today()
    created = (
        CoronaLog.insert(
            infected=infected, cured=cured, tests=tests, deaths=deaths, datetime=date_
        )
        .on_conflict_replace()
        .execute()
    )
    return created


def get_log_by_date(log_date):
    return CoronaLog.get_or_create(datetime=log_date)


def get_last_log_date() -> datetime.date:
    return (
        CoronaLog.select(CoronaLog.datetime)
        .order_by(CoronaLog.datetime.desc())
        .get()
        .datetime
    )


def get_infected_log() -> typing.Iterable[dict]:
    return CoronaLog.select(
        CoronaLog.datetime,
        CoronaLog.infected,
        CoronaLog.cured,
        CoronaLog.tests,
        CoronaLog.deaths,
    ).dicts()


def get_infected_increase_log() -> typing.Iterable[dict]:
    CoronaLogPrevieous = CoronaLog.alias()
    previous_query = CoronaLogPrevieous.select()
    previous_query = previous_query.alias("clp")

    return (
        CoronaLog.select(
            CoronaLog.datetime,
            Value(CoronaLog.infected - fn.COALESCE(previous_query.c.infected, 0)).alias(
                "infected_increase"
            ),
            Value(CoronaLog.cured - fn.COALESCE(previous_query.c.cured, 0)).alias(
                "cured_increase"
            ),
            Value(CoronaLog.tests - fn.COALESCE(previous_query.c.tests, 0)).alias(
                "tests_increase"
            ),
            Value(CoronaLog.deaths - fn.COALESCE(previous_query.c.deaths, 0)).alias(
                "deaths_increase"
            ),
        )
        .join(
            previous_query,
            JOIN.LEFT_OUTER,
            on=(previous_query.c.id == CoronaLog.id - 1),
        )
        .dicts()
    )


def get_last_location_log() -> typing.Iterable[dict]:
    last_date = (
        CoronaLocationLog.select(CoronaLocationLog.date)
        .order_by(CoronaLocationLog.date.desc())
        .get()
        .date
    )
    return (
        CoronaLocationLog.select(
            CoronaLocationLog.date,
            CoronaLocationLog.infected,
            CoronaLocationLog.infected_females,
            Value(
                CoronaLocationLog.infected - CoronaLocationLog.infected_females
            ).alias("infected_males"),
            CoronaLocationLog.cured,
            CoronaLocationLog.tests,
            CoronaLocationLog.deaths,
            CoronaLocation.location,
            CoronaLocation.last_updated,
        )
        .join(CoronaLocation)
        .where(CoronaLocationLog.date == last_date)
        .dicts()
    )
