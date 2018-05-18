import re
from .ConfParser import ConfigParser
from .ConfigParserLib import *
import logging
logger1 = logging.getLogger("ConfigParser")

class InvalidCmd(Exception):
    pass

class InvalidGrp(Exception):
    pass

class TopoParser(ConfigParser):

    def load_instruction(self, cmd, devices_str):
        """ Loads an instruction

        This function is intended to run one "show command" against one topology group.

        Args:
            cmd: a string including the instruction to be loaded.

        Returns:

        Raises:
        """

        if re.match('show .*', cmd):

            if re.search('all_devices', devices_str):
                devices_list = self._topology.keys()
            else:
                devices_list = str_to_device_list(devices_str)

            for device in devices_list:

                if device in self._topology.keys():
                    logger1.debug('Adding instruction "{0}" to group {1}'.format(cmd, device))

                    self._instruction[device] = list()
                    self._instruction[device].append(cmd)

                else:
                    raise InvalidGrp('Device {0} is not in the topology'.format(device))

        else:
            raise InvalidCmd('This is not a show command')