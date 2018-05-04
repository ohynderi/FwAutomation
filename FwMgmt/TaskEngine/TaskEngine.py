from abc import ABCMeta, abstractmethod
import concurrent.futures
import time
import logging
logger1 = logging.getLogger("TaskEngine")

class Task(metaclass=ABCMeta):
    task_id = 0

    def __init__(self, path, description=''):
        Task.task_id += 1
        self._task_id = Task.task_id
        self._task_name = 'Task-{0}'.format(self._task_id)
        self._description = description
        self._log_fd = open(path + self._task_name, 'w')
        self._log_fd.write('{0} {1}: Starting task\n'.format(time.asctime(), self._task_name))


    @abstractmethod
    def run(self):
        pass

    @property
    def task_name(self):
        return self._task_name

    def _log(self, msg):
        self._log_fd.write('{0} {1}: {2}\n'.format(time.asctime(), self._task_name, msg))

    def __str__(self):
        return '{0} {1}'.format(self._task_name, ': ' + self._description)


def task_engine(task_gen, conc_thread = 6):
    logger1.warning('Start Running tasks...')

    with concurrent.futures.ThreadPoolExecutor(max_workers = conc_thread) as executor:
        ongoing_task = {executor.submit(task.run): task.task_name for task in task_gen}
        for future in concurrent.futures.as_completed(ongoing_task):
            task_name = ongoing_task[future]
            try:
                result = future.result()
            except Exception as e:
                logger1.warning('{0} : {1}'.format(task_name, e))
            else:
                logger1.warning('Task for {0} {1}'.format(task_name, result))
