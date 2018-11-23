# FwAutomation
## Overview

The purpose of this script is to automate the provision of Juniper SRX firewalls using the Juniper PyEZ Python libraries.

The script can be ran in two modes:
1. **show command**: this is to apply a (show) command, given as an agurtment to the script, to a list of devices
2. **set command**: this is to apply set commands to a list of devices

Regardless of the mode, the script creates a different task per firewall, and run them in parallel making the execution very fast. The output of each task is redirected into a separate file. 

```
EwsFwMgmt.py --help
usage: EwsFwMgmt.py [-h] [-c SHOW_COMMAND] [-d DEVICES] [-i INSTRUCTION_FILE]
                    [-t TOPOLOGY_FILE] [-n NETWORK_FILE]

optional arguments:
  -h, --help           show this help message and exit
  -c SHOW_COMMAND      A show command. To be used in combination with -d. Eg:
                       show version
  -d DEVICES           Comma separate device list. To be used in combination
                       with -c. Eg: hostname1, hostname2
  -i INSTRUCTION_FILE  By default: /Config/instruction.csv
  -t TOPOLOGY_FILE     By default: /Config/topology.csv
  -n NETWORK_FILE      By default: /Config/delegation_networks.csv
  ```
