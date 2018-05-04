import csv
import re
import time
from .ConfParser import ConfigParser

class TopoParser(ConfigParser):

    def load_instruction(self, cmd, grp):
        if re.match('show .*', cmd):

            if grp in self._topology.keys():
                if self._debug:
                    print('Adding instruction {0} to group {1}'.format(cmd, grp))

                self._instruction[grp] = list()
                self._instruction[grp].append(cmd)

            else:
                raise Exception('The Group {0} is not in the topology'.format(grp))

        else:
            raise Exception('Invalide command')