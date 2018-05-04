import re
from .ConfParser import ConfigParser
import logging
logger1 = logging.getLogger("ConfigParser")

class TopoParser(ConfigParser):

    def load_instruction(self, cmd, grp):
        if re.match('show .*', cmd):

            if grp in self._topology.keys():
                logger1.debug('Adding instruction "{0}" to group {1}'.format(cmd, grp))

                self._instruction[grp] = list()
                self._instruction[grp].append(cmd)

            else:
                raise Exception('The Group {0} is not in the topology'.format(grp))

        else:
            raise Exception('Invalide command')