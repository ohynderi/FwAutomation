import FwMgmt
import sys
from os import getcwd
import logging
logger1 = logging.getLogger("__main__")
import logging.config
import argparse

def show_cmd(cmd, grp, topology_file):
    logger1.debug('Getting "{0}" output from {1}'.format(cmd, grp))

    parser1 = FwMgmt.TopoParser()

    with open(getcwd() + topology_file) as fd_topology:
        parser1.load_topology(fd_topology)

    parser1.load_instruction(cmd, grp)

    task_gen = (FwMgmt.NetconfCliTask(getcwd() + '/Log/', '', device, username, password, cmd) for
                device, username, password, cmd in iter(parser1))
    FwMgmt.task_engine(task_gen)


def set_cmd(instruction_file, topology_group):
    parser1 = FwMgmt.ConfigParser()

    with open(getcwd() + '/Config/topology.csv') as fd_topology:
        parser1.load_topology(fd_topology)

    if len(sys.argv) == 1:
        with open(getcwd() + '/Config/instructions.csv') as fd_instruction:
            parser1.load_instruction(fd_instruction)

        #parser1.print_topology()
        #parser1.print_instruction()

        task_gen = (FwMgmt.NetconfTask(getcwd() + '/Log/', '', device, username, password, cmd_set)
                    for device, username, password, cmd_set in iter(parser1))
        FwMgmt.task_engine(task_gen)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', action='store', dest='show_command', help='To be used in combination with -g')
    parser.add_argument('-g', action='store', dest='topology_group', help='To be used in combination with -c')
    parser.add_argument('-f', action='store', dest='instruction_file', help='By default: Config/instruction.csv', default='/Config/instructions.csv')
    parser.add_argument('-t', action='store', dest='topology_file', help='By default: Config/topology.csv', default='/Config/topology.csv')

    parser_result = parser.parse_args()

    if parser_result.show_command and parser_result.topology_group:
        show_cmd(parser_result.show_command, parser_result.topology_group, parser_result.topology_file)
    elif parser_result.show_command and not parser_result.topology_group:
        raise Exception('missing -g argument')

    elif not parser_result.show_command and parser_result.topology_group:
        raise Exception('missing -c argument')

    else:
        set_cmd(parser_result.instruction_file, parser_result.topology_file)


if __name__ == '__main__':
    logging.config.fileConfig('Config/logging.conf')
    main()








