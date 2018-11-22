import FwMgmt
from os import getcwd, listdir, remove
from os.path import getctime, basename
import logging
logger1 = logging.getLogger("__main__")
import logging.config
import argparse
import zipfile
import re
import time

def archive_log_files():

    log_dir = getcwd() + '/Log/'

    file_list = [f for f in listdir(log_dir) if re.match('Task.*', f)]

    if len(file_list) > 0:
        logger1.warning('Archiving previous log file')
        creation_time = time.strftime('%Y%m%d%H%M%S', time.gmtime(getctime(log_dir + file_list[0])))

        with zipfile.ZipFile(log_dir + creation_time + ".zip", "w") as zip_fd:
            for file in file_list:
                zip_fd.write(log_dir + file, basename(log_dir + file))
                remove(log_dir + file)



def show_cmd(cmd, devices, topology_file):

    username = input('Please enter a username: ')
    password = input('Please enter corresponding password: ')

    try:
        logger1.warning('Requesting "{0}" from {1}'.format(cmd, devices))

        parser1 = FwMgmt.TopoParser()

        with open(getcwd() + topology_file) as fd_topology:
            parser1.load_topology(fd_topology)

        parser1.load_instruction(cmd, 'devices: ' + devices)

        task_gen = (FwMgmt.NetconfCliTask(getcwd() + '/Log/', '', device, username, password, cmd) for
                    device, cmd in iter(parser1))
        FwMgmt.task_engine(task_gen)

    except FwMgmt.InvalidCmd as e:
        logger1.critical('This is not a valid show command. Stopping')

    except FwMgmt.InvalidGrp as e:
        logger1.critical('Show command for a device that is not in the topology. Stopping')

    except FwMgmt.InvalidTopology:
        logger1.critical('No proper / empty topology. Stopping...')

    except FwMgmt.MalformFile as e:
        logger1.critical('Malformed {0} file at line {1}. Stopping'.format(e.file, e.row))

    except Exception as e:
        raise


def set_cmd(instruction_file, topology_file, network_file):

    username = input('Please enter a username: ')
    password = input('Please enter corresponding password: ')

    try:

        parser1 = FwMgmt.ConfigParser()

        with open(getcwd() + topology_file) as fd_topology:
            parser1.load_topology(fd_topology)

        with open(getcwd() + network_file) as fd_network:
            parser1.load_delegation_networks(fd_network)

        with open(getcwd() + instruction_file) as fd_instruction:
            parser1.load_instruction(fd_instruction)


        #parser1.print_topology()
        parser1.print_instruction()

        confirmation = input('Ready to proceed? [Y|N]')

        if confirmation == ('Y' or 'y'):
            task_gen = (FwMgmt.NetconfTask(getcwd() + '/Log/', '', device, username, password, cmd_set)
                    for device, cmd_set in iter(parser1))
            FwMgmt.task_engine(task_gen)

        else:
            logger1.critical('Stopping...')


    except FwMgmt.InvalidTopology as e:
        logger1.critical('No proper / empty topology. Stopping...')

    except FwMgmt.InvalidInstruction as e:
        logger1.critical('No proper instruction found. Stopping')

    except FwMgmt.MalformFile as e:
        logger1.critical('Malformed {0} file at line {1}. Stopping'.format(e.file, e.row))

    except Exception as e:
        raise


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', action='store', dest='show_command', help='A show command. To be used in combination with -d. Eg: show version')
    parser.add_argument('-d', action='store', dest='devices', help='Comma separate device list. To be used in combination with -c. Eg: hostname1, hostname2')
    parser.add_argument('-i', action='store', dest='instruction_file', help='By default: /Config/instruction.csv', default='/Config/instructions.csv')
    parser.add_argument('-t', action='store', dest='topology_file', help='By default: /Config/topology.csv', default='/Config/topology.csv')
    parser.add_argument('-n', action='store', dest='network_file', help='By default: /Config/delegation_networks.csv', default='/Config/delegation_networks.csv')


    archive_log_files()
    parser_result = parser.parse_args()

    if parser_result.show_command and parser_result.devices:
        show_cmd(parser_result.show_command, parser_result.devices, parser_result.topology_file)

    elif parser_result.show_command and not parser_result.devices:
        logger1.critical('missing -d argument. Stopping...')

    elif not parser_result.show_command and parser_result.devices:
        logger1.critical('missing -c argument. Stopping...')

    else:
        set_cmd(parser_result.instruction_file, parser_result.topology_file, parser_result.network_file)


if __name__ == '__main__':
    logging.config.fileConfig('Config/logging.conf')
    main()








