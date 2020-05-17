
from marshmallow import Schema, fields


class Trigger(Schema):
    timezone = fields.Str()
    start_date = fields.Str()
    end_date = fields.Str()
    jitter = fields.Str()
    type = fields.Function(lambda obj: obj.__module__.split(".")[-1])
    # date trigger
    run_date = fields.Str()

    # intervals trigger
    interval = fields.Str()
    interval_length = fields.Str()

    # cron trigger
    year = fields.Str()
    month = fields.Str()
    day = fields.Str()
    week = fields.Str()
    day_of_week = fields.Str()
    hour = fields.Str()
    minute = fields.Str()
    second = fields.Str()
    fields = fields.List(fields.Str())


class SchedulerSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    func_ref = fields.Str()
    trigger = fields.Nested(Trigger)
    executor = fields.Str()
    args = fields.List(fields.Str())
    kwargs = fields.Dict()
    misfire_grace_time = fields.Int()
    coalesce = fields.Bool()
    max_instances = fields.Int()
    next_run_time = fields.Str()
    pending = fields.Bool()
