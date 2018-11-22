from .ConfigParserLib import str_to_device_list, list_to_command_set
import csv
import re
import logging
logger1 = logging.getLogger("ConfigParser")

class InvalidTopology(Exception):
    pass

class InvalidInstruction(Exception):
    pass

class MalformFile(Exception):
    def __init__(self, file, row):
        self._file = file
        self._row = row

    @property
    def file(self):
        return self._file

    @property
    def row(self):
        return self._row


class ConfigParser:
    def __init__(self):
        self._topology = dict()
        self._instruction = dict()
        self._delegation_networks = dict()


    def _variable_replacement(self, cmd_set, site_id):

        new_cmd_set = list()

        if site_id in self._delegation_networks.keys():
            for cmd in cmd_set:
                for var in self._delegation_networks[site_id].keys():

                    if re.search(var, cmd) and self._delegation_networks[site_id][var] != 'unknown':
                        cmd = re.sub(var, self._delegation_networks[site_id][var], cmd)

                new_cmd_set.append(cmd)

        else:
            logger1.warning('No variables know for site {0}'.format(site_id))
            new_cmd_set = cmd_set

        return new_cmd_set


    def load_delegation_networks(self, fd):

        csv_fd = csv.reader(fd, delimiter=',')

        header = None

        for row, line in enumerate(csv_fd):
            if not re.match('[0-9]+', line[0]):
                # This is the CSV header
                header = line[1:]

            else:
                if header != None:

                    site_id = line[0]
                    self._delegation_networks[site_id] = dict()

                    for column, el in enumerate(line[1:]):
                        self._delegation_networks[site_id][header[column]] = el

                        logger1.debug('{0} set to {1} for site {2}'.format(header[column], el, site_id))

                else:
                    logger1.critical('No proper header in the CSV file. Can process line {0}'.format(line))


    def load_topology(self, fd):
        """ Loads the topology

        This function loads the topology into the object internal structure.

        The topology is csv file with:
            column 0: firewall hostname:
            column 3: the site id
            column 4: the fw management ip

        Args:
            fd: topology file descriptor

        Returns:

        Raises:
            InvalidTopology if no valid entry found.
                A line is considered invalid if hostname is empty or
                the side_id is not an integer or
                the management ip is not and ipv4
        """

        csv_fd = csv.reader(fd, delimiter=',')

        for row, line, in enumerate(csv_fd):
            site_id = line[3].lstrip()
            hostname = line[0].lstrip()
            ip = line[4].lstrip()

            if hostname != '' and re.match('[0-9]+', site_id) and re.match('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',ip):
                if hostname not in self._topology.keys():
                    self._topology[hostname] = dict()
                    self._topology[hostname]['id'] = site_id
                    self._topology[hostname]['ip'] = ip

                else:
                    logger1.debug('Hostname at line {0} already in the topology db. Skipping'.format(row +1))
            else:
                logger1.debug('Line {0} of the topology file is invalid. Skipping'.format(row +1))

        if len(self._topology.keys()) == 0:
            raise InvalidTopology('No proper topology found')


    def load_instruction(self, fd):
        """ Loads the instructions

        This function loads the instructions into the object internal structure.

        The instruction are defined in a text with one or more instruction blocks.
        An instruction block has following syntax:

        devices: [(<hostname>,)+ | all_devices)]
        commands:
            <command1>
            <command2>
            ...

        Args:
            fd: topology file descriptor

        Returns:

        Raises:
        """

        # device_flag is true if parser is within an instruction block
        device_flag = False

        # command_flag is true if parser is within an instruction block, within a parser block
        command_flag = False

        # devices being the list of devices part the instruction block
        devices = list()

        # commands being the list of commands part of the instruction block
        commands = list()

        for row, line in enumerate(fd):
            if line.lstrip() == '':
                # Empty line, skipping
                logger1.debug("Line {0} of instruction file empty. Skipping...".format(row + 1))

            elif re.match('devices:', line) and device_flag and command_flag:
                # New device statement, exiting current block, entering new one.
                logger1.debug('Exiting instruction bloc')
                command_flag = False

                # Processing previous block
                for device in devices:
                    if device in self._topology.keys():
                        logger1.debug('Adding instruction set to device {0}'.format(device))

                        instruction_after_swapping_site_id = list_to_command_set(commands, self._topology[device]['id'])
                        instruction_after_swapping_var = self._variable_replacement(instruction_after_swapping_site_id, self._topology[device]['id'])
                        self._instruction[device] = instruction_after_swapping_var

                    else:
                        logger1.debug('Device {0} doesnt exist in the topology. Skipping...'.format(device))

                # Opening new block
                logger1.debug('Entering new block')
                commands = list()

                if re.search('all_devices', line):
                    devices = self._topology.keys()
                else:
                    devices = str_to_device_list(line)

            elif re.match('devices:', line) and not device_flag and not command_flag:
                # Entering first block of the instruction file
                logger1.debug('Entering instruction block')
                device_flag = True

                if re.search('all_devices', line):
                    devices = self._topology.keys()
                else:
                    devices = str_to_device_list(line)

            elif re.match('commands:', line) and device_flag and not command_flag:
                # command statement and we are in a block
                command_flag = True

            elif device_flag and command_flag and (re.match('[set|del|insert].*', line.lstrip())):
                # Instruction part part of a block
                logger1.debug('Adding instruction "{0}" to instruction set'.format(line.lstrip().rstrip()))
                commands.append(line.lstrip().rstrip())

            else:
                raise MalformFile('instruction file', row + 1)


        # EOF reached. Processing last block
        if device_flag and command_flag:
            for device in devices:
                if device in self._topology.keys():
                    logger1.debug('Adding instruction set to device {0}'.format(device))

                    instruction_after_swapping_site_id = list_to_command_set(commands, self._topology[device]['id'])
                    instruction_after_swapping_var = self._variable_replacement(instruction_after_swapping_site_id,
                                                                                self._topology[device]['id'])
                    self._instruction[device] = instruction_after_swapping_var
                else:
                    logger1.debug('Device {0} doesnt exist in the topology. Skipping...'.format(device))

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

        for hostname in self._topology.keys():
            print('Hostname: {0}'.format(hostname))
            print('\tSite ID: {0}'.format(self._topology[hostname]['id']))
            print('\tIP: {0}'.format(self._topology[hostname]['ip']))
        print('---------------- Loaded Topology ----------------')


    def __iter__(self):
        ''' Generator function yielding  the instruction for the devices.

        Args:

        Returns: (device_ip, group, username, password, instruction set)

        Raises:
        '''

        for device_nbr, device in enumerate(self._instruction.keys()):
            logger1.warning('Creating Task-{0} for {1}'.format(device_nbr + 1, device))
            yield (self._topology[device]['ip'], self._instruction[device])







