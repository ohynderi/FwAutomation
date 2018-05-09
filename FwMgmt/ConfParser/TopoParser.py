import re
from .ConfParser import ConfigParser
import logging
logger1 = logging.getLogger("ConfigParser")

class InvalidCmd(Exception):
    pass

class InvalidGrp(Exception):
    pass

class TopoParser(ConfigParser):

    def load_instruction(self, cmd, grp):
        """ Loads an instruction

        This function is intended to run one "show command" against one topology group.

        Args:
            cmd: a string including the instruction to be loaded.

        Returns:

        Raises:
        """

        if re.match('show .*', cmd):

            if grp in self._topology.keys():
                logger1.debug('Adding instruction "{0}" to group {1}'.format(cmd, grp))

                self._instruction[grp] = list()
                self._instruction[grp].append(cmd)

            else:
                raise InvalidGrp('The Group {0} is not in the topology'.format(grp))

        else:
            raise InvalidCmd('This is not a show command')