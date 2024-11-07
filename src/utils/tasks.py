from json import dumps
from django_celery_beat.models import IntervalSchedule, PeriodicTask


def create_periodic_task(name: str, task: str, args: list, one_off: bool = True):
    """
    Create a periodic task.

    Args:
        name (str): The name of the task.
        task (str): The task to be executed.
        args (list): The arguments for the task.
        one_off (bool, optional): Whether the task is a one-off task. Defaults to True.
    """
    PeriodicTask.objects.create(
        interval=IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)[0],
        name=name,
        task=task,
        args=dumps(args),
        one_off=one_off,
    )
