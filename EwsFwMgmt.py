import FwMgmt
import sys
from os import getcwd
import logging
logger1 = logging.getLogger("__main__")
import logging.config

def print_help():
    print('usage: EwsFwMgmt.py [-h] [-c "show command"] [-g "group"]\n')
    print('example: EwsFwMgmt.py -c "show version" -g group1')


def show_cmd(cmd, grp):
    logger1.debug('Getting {0} output from {1}'.format(cmd, grp))

    parser1 = FwMgmt.TopoParser()

    with open(getcwd() + '/Config/topology.csv') as fd_topology:
        parser1.load_topology(fd_topology)

    parser1.load_instruction(cmd, grp)

    task_gen = (FwMgmt.NetconfCliTask(getcwd() + '/Log/', '', device, username, password, cmd) for
                device, username, password, cmd in iter(parser1))
    FwMgmt.task_engine(task_gen)


def set_cmd():
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
    if len(sys.argv) == 1:
        set_cmd()

    elif '-h' in sys.argv:
        print_help()

    elif '-c' in sys.argv:
        cmd = sys.argv[sys.argv.index('-c') + 1]

        if '-g' in sys.argv:
            grp = sys.argv[sys.argv.index('-g') + 1]
            show_cmd(cmd, grp)
        else:
            print_help()

    else:
        print_help()


if __name__ == '__main__':
    logging.config.fileConfig('Config/logging.conf')
    main()








