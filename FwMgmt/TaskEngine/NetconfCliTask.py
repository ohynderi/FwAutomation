from jnpr.junos import Device
import traceback
from .TaskEngine import Task


class NetconfCliTask(Task):

    def __init__(self, path, description, ip, username, password, show_cmd):
        super().__init__(path, description)
        self._ip = ip
        self._username = username
        self._password = password
        self._cmd = show_cmd[0]

    @property
    def task_name(self):
        return self._ip

    def run(self):
        try:
            # Opening the connection
            self._log("Running task")

            device1 = Device(host=self._ip, user=self._username, password=self._password)
            device1.open()
            self._log("Connected to {0}".format(self._ip))

            self._log_fd.writelines(device1.cli(self._cmd, warning=False))

            device1.close()
            self._log_fd.close()

        except Exception as e:
            self._log_fd.write('\n'+str(e))
            self._log_fd.write(traceback.format_exc())
            self._log_fd.close()

            raise

        return 'Successfully completed'
