from jnpr.junos import Device
import traceback
from .TaskEngine import Task


class NetconfCliTask(Task):
    """ Function creating a NetconfCLITask object.

    Should typically used for applyging a "show command" on a group of device

    Args:
        path (string): location of the task log file
        description (string): description of the task
        ip (string): ip address of the device
        username (string): username to login on the device
        password (string): password to login on the device
        cmd_set (list of string): list of instruction to be run on a device

    Returns:

    Raises:
    """

    def __init__(self, path, description, ip, username, password, show_cmd):
        super().__init__(path, description)
        self._ip = ip
        self._username = username
        self._password = password
        self._cmd = show_cmd[0]

    '''
    @property
    def task_name(self):
        return self._ip
    '''

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
