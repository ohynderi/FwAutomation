import argparse
import logging
import re
from os import listdir, getcwd
from os.path import isfile, join
import csv


class Topology:
    def __init__(self):
        self.topology = dict()

    def _extract_subnet(self, s):
        subnet = re.search('[0-9]+\.[0-9]+\.[0-9]+', s).group() + '.0' + re.search('/[0-9]+',s).group()

        return subnet

    def _extract_name(self, s):
        name = re.search('[0-9]+\.[0-9]+\.[0-9]+', s).group() + '.0_' + re.search('/[0-9]+',s).group()[1:]

        return name


    def add_delegation(self, fd):

        site_id = 'unknown'
        LAN_18_NETW = 'unknown'
        LAN_96_NETW = 'unknown'
        LAN_97_NETW = 'unknown'
        LAN_98_NETW = 'unknown'
        HOST_LAN_96_NETW = 'unknown'
        LAN_18_NAME = 'unknown'
        LAN_96_NAME = 'unknown'
        LAN_97_NAME = 'unknown'
        LAN_98_NAME = 'unknown'
        HOST_LAN_96_NAME = 'unknown'

        for line in fd:
            if re.match('reth0\.18', line):
                LAN_18_NETW = self._extract_subnet(line)
                LAN_18_NAME = self._extract_name(line)
            if re.match('reth0\.96', line):
                LAN_96_NETW = self._extract_subnet(line)
                LAN_96_NAME = self._extract_name(line)
                HOST_LAN_96_NETW = re.match('[0-9]+\.[0-9]+\.[0-9]+', LAN_96_NETW).group() + '.28' + '/32'
                HOST_LAN_96_NAME = re.match('[0-9]+\.[0-9]+\.[0-9]+', LAN_96_NETW).group() + '.28' + '_32'
                site_id = LAN_96_NETW.split('.')[2]
            if re.match('reth0\.97', line):
                LAN_97_NETW = self._extract_subnet(line)
                LAN_97_NAME = self._extract_name(line)
            if re.match('reth0\.98', line):
                LAN_98_NETW = self._extract_subnet(line)
                LAN_98_NAME = self._extract_name(line)

        if site_id != 'unknown':

            logger1.debug('Networks for delegation {0} found'.format(site_id))

            self.topology[site_id] = {'LAN-18-NETW' : LAN_18_NETW}
            self.topology[site_id]['LAN-18-NAME'] = LAN_18_NAME
            self.topology[site_id]['LAN-96-NETW'] = LAN_96_NETW
            self.topology[site_id]['LAN-96-NAME'] = LAN_96_NAME
            self.topology[site_id]['HOST-LAN-96-NETW'] = HOST_LAN_96_NETW
            self.topology[site_id]['HOST-LAN-96-NAME'] = HOST_LAN_96_NAME
            self.topology[site_id]['LAN-97-NETW'] = LAN_97_NETW
            self.topology[site_id]['LAN-97-NAME'] = LAN_97_NAME
            self.topology[site_id]['LAN-98-NETW'] = LAN_98_NETW
            self.topology[site_id]['LAN-98-NAME'] = LAN_98_NAME


    def write_result(self, file):

        fd = open(file, 'w')
        csv_fd = csv.writer(fd, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='', lineterminator='\n')

        header = ['Site ID'] + sorted(list(self.topology[list(self.topology.keys())[0]].keys()))
        csv_fd.writerow(header)

        for site in sorted(self.topology.keys()):

            logger1.debug('Writing result for site {0}'.format(site))

            tmp_list = list()
            tmp_list.append(site)

            for key in sorted(self.topology[site].keys()):
                tmp_list.append(self.topology[site][key])

            csv_fd.writerow(tmp_list)

        fd.close()




def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', action='store', dest='log_file', help='Log files to parse')
    parser.add_argument('-d', action='store', dest='dir', help='Directory where log files are located')

    parser_result = parser.parse_args()
    topo = Topology()

    for file in [f for f in listdir(parser_result.dir) if isfile(join(parser_result.dir, f))]:
        if re.match(parser_result.log_file, file):
            logger1.debug('Opening file {0}'.format(join(parser_result.dir, file)))

            with open(join(parser_result.dir, file), 'r') as fd:
                topo.add_delegation(fd)

    topo.write_result(join('Config', 'delegation_networks.csv'))


if __name__ == '__main__':
    logger1 = logging.getLogger("__main__")
    logging.basicConfig(level=logging.DEBUG, format='=%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()