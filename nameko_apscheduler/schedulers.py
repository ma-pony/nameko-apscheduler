from apscheduler.schedulers.background import BackgroundScheduler

from schema import SchedulerSchema
from kombu.common import maybe_declare
from nameko import config
from nameko.amqp.publish import get_connection
from nameko.constants import AMQP_SSL_CONFIG_KEY
from nameko.extensions import DependencyProvider
from nameko.messaging import encode_to_headers, Publisher
from nameko.standalone.events import get_event_exchange

from utils import get, delete


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


scheduler_publisher = SchedulerPublisher(exchange=get_event_exchange("scheduler"))


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
        id: str,
        trigger: str,
        name: str,
        event_data: dict,
        event_type: str,
        **kwargs
    ):
        """
        """
        return self.background_scheduler.add_job(
            id=str(id),
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
