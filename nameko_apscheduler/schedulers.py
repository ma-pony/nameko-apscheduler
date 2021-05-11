import os

from apscheduler.schedulers.background import BackgroundScheduler
from kombu.common import maybe_declare
from nameko import config
from nameko.amqp.publish import get_connection
from nameko.constants import AMQP_SSL_CONFIG_KEY
from nameko.extensions import DependencyProvider
from nameko.messaging import encode_to_headers, Publisher
from nameko.standalone.events import get_event_exchange

from nameko_apscheduler.schema import SchedulerSchema
from nameko_apscheduler.utils import get, delete

EXCHANGE_NAME = config.get("APSCHDULER", {}).get("exchange_name", "nameko-apscheduler")


class SchedulerPublisher(Publisher):
    def __init__(self, exchange=None, declare=None, **publisher_options):
        super(SchedulerPublisher, self).__init__(
            exchange=exchange, declare=declare, **publisher_options
        )
        default_ssl = config.get(AMQP_SSL_CONFIG_KEY)
        ssl = self.publisher_options.pop("ssl", default_ssl)

        with get_connection(self.amqp_uri, ssl) as conn:
            for entity in self.declare:
                maybe_declare(entity, conn.channel())

        serializer = self.publisher_options.pop("serializer", "json")
        self.publisher = self.publisher_cls(
            self.amqp_uri,
            ssl=ssl,
            serializer=serializer,
            exchange=self.exchange,
            declare=self.declare,
            **self.publisher_options
        )

    def publish(
        self,
        event_type: str = None,
        event_data: dict = None,
        extra_headers: dict = None,
    ):
        self.publisher.publish(
            event_data,
            exchange=self.exchange,
            routing_key=event_type,
            extra_headers=extra_headers,
        )


scheduler_publisher = SchedulerPublisher(exchange=get_event_exchange(EXCHANGE_NAME))


class Scheduler(DependencyProvider):
    background_scheduler = BackgroundScheduler()

    def __init__(self):
        self.extra_headers = None

    def start(self):
        self.background_scheduler.start()

    def setup(self):
        scheduler_config = config["APSCHDULER"]
        self.background_scheduler.configure(gconfig=scheduler_config, prefix="")

    def stop(self):
        self.background_scheduler.shutdown()

    def kill(self):
        self.background_scheduler.shutdown()

    @get(SchedulerSchema)
    def create_job(
            self,
            job_id: str,
            trigger: str,
            name: str,
            event_data: dict,
            event_type: str,
            **kwargs
    ):
        """
            add_job(func, trigger=None, args=None, kwargs=None, id=None, \
            name=None, misfire_grace_time=undefined, coalesce=undefined, \
            max_instances=undefined, next_run_time=undefined, \
            jobstore='default', executor='default', \
            replace_existing=False, **trigger_args)

        Adds the given job to the job list and wakes up the scheduler
        if it's already running.

        Any option that defaults to ``undefined`` will be replaced with t
        he corresponding default
        value when the job is scheduled (which happens when the scheduler is started, or
        immediately if the scheduler is already running).

        The ``func`` argument can be given either as a callable object
        or a textual reference in the ``package.module:some.object`` format,
        where the first half (separated by ``:``) is an
        importable module and the second half is a reference to the callable object,
        relative to the module.

        The ``trigger`` argument can either be:
          the alias name of the trigger (e.g. ``date``, ``interval`` or ``cron``),
          in which case any extra keyword arguments to this method are passed on to
           the trigger's constructor  an instance of a trigger class

        :param func: callable (or a textual reference to one) to run at the given time
        :param str|apscheduler.triggers.base.BaseTrigger trigger:
        trigger that determines when ``func`` is called
        :param list|tuple args: list of positional arguments to call func with
        :param dict kwargs: dict of keyword arguments to call func with
        :param str|unicode id: explicit identifier for the job (for modifying it later)
        :param str|unicode name: textual description of the job
        :param int misfire_grace_time: seconds after the designated
        runtime that the job is still allowed to be run
        :param bool coalesce: run once instead of many times  if the scheduler
        determines that the job should be run more than once in succession
        :param int max_instances: maximum number of concurrently running
        instances allowed for this job
        :param datetime next_run_time: when to first run the job,
         regardless of the trigger (pass ``None`` to add the job as paused)
        :param str|unicode jobstore: alias of the job store to store the job in
        :param str|unicode executor: alias of the executor to run the job with
        :param bool replace_existing: ``True`` to replace an existing job with
        the same ``id`` (but retain the number of runs from the existing one)
        :rtype: Job

        ================================================================================
        cron trigger params: year, month, day, week, day_of_week, hours, minute,
        second, start_date, end_date, timezone, jitter
        Examples:
            Schedules job_function to be run on the third Friday of June,
            July, August, November and December at 00:00, 01:00, 02:00 and 03:00
            create_job(
                job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3'
            )

            Runs from Monday to Friday at 5:30 (am) until 2014-05-30 00:00:00
            create_job(
                job_function, 'cron', day_of_week='mon-fri',
                 hour=5, minute=30, end_date='2014-05-30'
             )

            Run the `job_function` every sharp hour with an extra-delay picked randomly
             in a [-120,+120] seconds window.
            create_job(job_function, 'cron', hour='*', jitter=120)


        date trigger params: run_date, timezone
        Examples:
            The job will be executed on November 6th, 2009
            create_job(job_function, 'date', run_date=date(2009, 11, 6), args=['text'])

            The job will be executed on November 6th, 2009 at 16:30:05
            create_job(
                job_function, 'date', run_date=datetime(2009, 11, 6, 16, 30, 5),
                args=['text']
            )
            create_job(
                job_function, 'date', run_date='2009-11-06 16:30:05', args=['text']
            )

            The 'date' trigger and datetime.now() as run_date are implicit
            create_job(job_function, args=['text'])


        interval trigger params: weeks, days, hours, minutes, seconds, start_date,
         end_date, timezone, jitter
        Examples:
            Schedule job_function to be called every two hours
            create_job(job_function, 'interval', hours=2)

            The same as before, but starts on 2010-10-10 at 9:30 and
            stops on 2014-06-15 at 11:00
            create_job(
                job_function, 'interval', hours=2, start_date='2010-10-10 09:30:00',
                end_date='2014-06-15 11:00:00'
            )

            Run the `job_function` every hour with an extra-delay picked randomly
             in a [-120,+120] seconds window.
            create_job(job_function, 'interval', hours=1, jitter=120)

        """
        return self.background_scheduler.add_job(
            id=str(job_id),
            func=scheduler_publisher.publish,
            trigger=trigger,
            name=name,
            kwargs={
                "event_type": event_type,
                "event_data": event_data,
                "extra_headers": self.extra_headers,
            },
            **kwargs
        )

    @delete(SchedulerSchema)
    def delete_job(self, job_id: str):
        return self.background_scheduler.remove_job(job_id)

    @get(SchedulerSchema)
    def get_job(self, job_id: str):
        return self.background_scheduler.get_job(job_id)

    @get(SchedulerSchema)
    def update_job(self, job_id: str, **changes):
        return self.background_scheduler.modify_job(job_id, **changes)

    @get(SchedulerSchema)
    def reschedule_job(self, job_id: str, jobstore=None, trigger=None, **trigger_args):
        return self.background_scheduler.reschedule_job(
            job_id, jobstore=jobstore, trigger=trigger, **trigger_args
        )

    def get_dependency(self, worker_ctx):
        self.extra_headers = encode_to_headers(worker_ctx.context_data)
        return self
