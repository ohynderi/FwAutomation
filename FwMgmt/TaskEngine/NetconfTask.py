import pprint
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import traceback
from lxml import etree
from .TaskEngine import Task

class NetconfTask(Task):

    def __init__(self, path, description, ip, username, password, cmd_set):
        super().__init__(path, description)
        self._ip = ip
        self._username = username
        self._password = password
        self._cmd_set = cmd_set

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


            # Getting device facts
            self._log("Getting facts")

            pp = pprint.PrettyPrinter(indent=4, stream=self._log_fd)
            pp.pprint(device1.facts)

            config1 = Config(device1)

            for line in self._cmd_set:
                self._log("Applying {0}".format(line))

                config1.load(line, format='set')


            self._log("Committing changes")

            config1.commit()

            self._log("Retrieving config")
            self._log_fd.writelines(etree.tostring(device1.rpc.get_config(), encoding='unicode'))

            device1.close()
            self._log_fd.close()

        except Exception as e:
            self._log_fd.write('\n'+str(e))
            self._log_fd.write(traceback.format_exc())
            self._log_fd.close()

            raise

        return 'Successfully completed'
