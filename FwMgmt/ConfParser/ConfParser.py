import csv
import re
import time
import logging
logger1 = logging.getLogger("ConfigParser")

class ConfigParser:
    def __init__(self):
        self._topology = dict()
        self._instruction = dict()

    def load_topology(self, fd):
        csv_fd = csv.reader(fd, delimiter=',')

        new_group = None
        new_user = None
        new_password = None
        new_dev_list = None

        for line in csv_fd:
            if re.match('group: .+', line[0]):
                new_group = line[0].split()[1]
                logger1.debug('New group found: {0}'.format(new_group))

            elif re.match('username: .+', line[0]):
                new_user = line[0].split()[1]
                logger1.debug('\tuser: {0}'.format(new_user))

            elif re.match('password: .+', line[0]):
                new_password = line[0].split()[1]
                logger1.debug('\tpassword: {0}'.format(new_password))

            elif re.match('[0-9]+.[0-9]+.[0-9]+.[0-9]+', line[0]):
                if not new_dev_list:
                    new_dev_list = list()
                new_dev_list.append(line[0])
                logger1.debug('\tdevice: {0}'.format(line[0]))

            elif re.match('', line[0]) and new_group and new_user and new_password and new_dev_list:
                self._topology[new_group] = {'username' : new_user}
                self._topology[new_group]['password'] = new_password
                self._topology[new_group]['device_list'] = new_dev_list

                new_group = None
                new_user = None
                new_password = None
                new_dev_list = None

            elif re.match('', line[0]):
                pass

            else:
                logger1.debug('This line makes no sense, skipping : {0}'.format(line))

        if new_group and new_user and new_password and new_dev_list:
            self._topology[new_group] = {'username': new_user}
            self._topology[new_group]['password'] = new_password
            self._topology[new_group]['device_list'] = new_dev_list


    def load_instruction(self, fd):
        csv_fd = csv.reader(fd, delimiter=',')

        for line in csv_fd:
            if line[0] == '':
                pass

            elif line[0] not in self._topology.keys():
                logger1.debug('This is an instruction for a group that doesnt exit. Skipping... {0}'.format(line))

            elif line[0] in self._instruction.keys():
                self._instruction[line[0]].append(line[1])
                logger1.debug('Adding instruction {0} to group {1}'.format(line[1], line[0]))

            elif line[0] not in self._instruction.keys():
                self._instruction[line[0]] = list()
                self._instruction[line[0]].append(line[1])
                logger1.debug('Adding {0} with instruction {1}'.format(line[0], line[1]))


    def print_instruction(self):
        print('---------------- Loaded Instructions ----------------')
        for key in self._instruction.keys():
            print(key)
            for instruction in self._instruction[key]:
                print('\t{0}'.format(instruction))
        print('---------------- Loaded Instructions ----------------')


    def print_topology(self):
        print('---------------- Loaded Topology ----------------')

        for key in self._topology.keys():
            print('group: {0}'.format(key))
            print('\tusername: {0}'.format(self._topology[key]['username']))
            print('\tpassword: {0}'.format(self._topology[key]['password']))

            for ip in self._topology[key]['device_list']:
                print('\t\t{0}'.format(ip))

        print('---------------- Loaded Topology ----------------')


    def __iter__(self):
        for group in self._instruction.keys():
            for device in self._topology[group]['device_list']:
                logger1.warning('Creating task for : {0}, part of group {1} at {2}: '.format(device, group, time.asctime()))
                yield (device, self._topology[group]['username'], self._topology[group]['password'], self._instruction[group])







