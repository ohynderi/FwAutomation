import FwMgmt
import time
from os import getcwd


class HelloTask(FwMgmt.Task):
    def __init__(self, path=''):
        super().__init__(path)

    def run(self):
        print('{0} start running task at {1}'.format(self._task_name, time.asctime()))
        self._log_fd.write('{0} {1}: Running task\n'.format(time.asctime(), self._task_name))

        time.sleep(5)

        self._log_fd.write('{0} {1}: Finishing task\n'.format(time.asctime(), self._task_name))
        self._log_fd.close()

        return 'completed'

def test1():
    task_gen = (HelloTask(getcwd() + '/Log/') for i in range(10))
    FwMgmt.task_engine(task_gen, conc_thread = 6, debug=True)


def test2():

    list1 = list()
    list1.append('set routing-options static route 3.3.3.0/24 next-hop 1.1.1.1')

    gen = (FwMgmt.NetconfTask(getcwd() + '/Log/', '', '10.32.72.51', 'root', 'ADVISE4ever!', list1)  for i in range(1))
    FwMgmt.task_engine(gen)


def main():
    test1()








if __name__ == '__main__':
    main()