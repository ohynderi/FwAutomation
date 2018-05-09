import csv
import re
import time
import logging
logger1 = logging.getLogger("ConfigParser")

class InvalidTopology(Exception):
    pass

class InvalidInstruction(Exception):
    pass

class MalformCsv(Exception):
    pass


class ConfigParser:
    def __init__(self):
        self._topology = dict()
        self._instruction = dict()

    def load_topology(self, fd):
        """ Loads the topology

        This function loads the topology into the object internal structure.

        The topology is csv file listing one or more device groups.
        All devices part of a group share the same credentials

        Device group syntax:
            group: <group_name>,
            username: <username>,
            password: <password>,
            <device_ip>
            <device_ip>

        Args:
            fd: topology file descriptor

        Returns:

        Raises:

        """

        csv_fd = csv.reader(fd, delimiter=',')

        new_group = None
        new_user = None
        new_password = None
        new_dev_list = None

        for line in csv_fd:
            if len(line) == 0:
                raise MalformCsv

            if re.match('group: .+', line[0]):
                new_group = line[0].split()[1]
                logger1.debug('New group found: {0}'.format(new_group))

            elif re.match('username: .+', line[0]):
                new_user = line[0].split()[1]
                logger1.debug('\twith user: {0}'.format(new_user))

            elif re.match('password: .+', line[0]):
                new_password = line[0].split()[1]
                logger1.debug('\twith password: {0}'.format(new_password))

            elif re.match('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', line[0]):
                if not new_dev_list:
                    new_dev_list = list()
                new_dev_list.append(line[0])
                logger1.debug('\twith device: {0}'.format(line[0]))

            elif re.match('^$', line[0]) and new_group and new_user and new_password and new_dev_list:
                logger1.debug('\t|-> Group {0} discovered'.format(new_group))
                self._topology[new_group] = {'username' : new_user}
                self._topology[new_group]['password'] = new_password
                self._topology[new_group]['device_list'] = new_dev_list

                new_group = None
                new_user = None
                new_password = None
                new_dev_list = None

            elif re.match('^$', line[0]) and (new_group or new_user or new_password or new_dev_list):
                logger1.warning('Group definition incomplete, skipping'.format())

                new_group = None
                new_user = None
                new_password = None
                new_dev_list = None

            elif re.match('^$', line[0]):
                logger1.debug('Empty line, skipping : {0}'.format(line))

            else:
                logger1.warning('This line makes no sense, skipping : {0}'.format(line))

        if new_group and new_user and new_password and new_dev_list:
            logger1.debug('\t|-> Group {0} discovered'.format(new_group))
            self._topology[new_group] = {'username': new_user}
            self._topology[new_group]['password'] = new_password
            self._topology[new_group]['device_list'] = new_dev_list

        if len(self._topology.keys()) == 0:
            raise InvalidTopology('No proper topology found')


    def load_instruction(self, fd):
        """ Loads the instruction

        This function loads the instructions into the object internal structure.

        Instructions are listed into a CSV file.
        For each line, first column is the group the instruction applies. Second column is the instruction.

        Hence syntax is the following:
        <group>,<instruction>

        Args:
            fd: instruction file descriptor

        Returns:

        Raises:
        """

        csv_fd = csv.reader(fd, delimiter=',')

        for line in csv_fd:
            if len(line) == 0:
                raise MalformCsv

            if line[0] == '^$':
                pass

            elif line[0] not in self._topology.keys():
                logger1.debug('This is an instruction for a group that doesnt exit. Skipping... {0}'.format(line))

            elif line[0] in self._instruction.keys():
                self._instruction[line[0]].append(line[1])
                logger1.debug('Adding instruction {0} to group {1}'.format(line[1], line[0]))

            elif line[0] not in self._instruction.keys():
                # Group exists in the topology but this is the first instruction for that group being parsed
                self._instruction[line[0]] = list()
                self._instruction[line[0]].append(line[1])
                logger1.debug('Adding {0} with instruction {1}'.format(line[0], line[1]))

        if len(self._instruction.keys()) == 0:
            raise InvalidInstruction('No valid instruction found')


    def print_instruction(self):
        ''' Printed the different instruction as loaded from the instruction file

        Args:

        Returns:

        Raises:
        '''

        print('---------------- Loaded Instructions ----------------')
        for key in self._instruction.keys():
            print(key)
            for instruction in self._instruction[key]:
                print('\t{0}'.format(instruction))
        print('---------------- Loaded Instructions ----------------')


    def print_topology(self):
        ''' Printed the topology as loaded from the topology file

        Args:

        Returns:

        Raises:
        '''

        print('---------------- Loaded Topology ----------------')

        for key in self._topology.keys():
            print('group: {0}'.format(key))
            print('\tusername: {0}'.format(self._topology[key]['username']))
            print('\tpassword: {0}'.format(self._topology[key]['password']))

            for ip in self._topology[key]['device_list']:
                print('\t\t{0}'.format(ip))

        print('---------------- Loaded Topology ----------------')


    def __iter__(self):
        ''' Generator function yielding  the instruction for the devices.

        Args:

        Returns: (device_ip, group, username, password, instruction set)

        Raises:
        '''

        iter = 0

        for group in self._instruction.keys():
            for device in self._topology[group]['device_list']:
                iter += 1
                logger1.warning('Creating Task-{0} for {1}, part of group {2}'.format(iter, device, group))
                yield (device, self._topology[group]['username'], self._topology[group]['password'], self._instruction[group])







