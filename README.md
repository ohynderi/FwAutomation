# FwAutomation
## Overview

The purpose of this script is to automate the provision of Juniper SRX firewalls using the Juniper PyEZ Python libraries.

The script can be ran in two modes:
1. **show command**: this is to apply one show command, given as argument to the script, to one ore more firewall.
2. **set command**: this is to apply a set of instructions to one or more firewall.

Regardless of the mode, the script creates a different task per firewall, and run them in parallel making the execution very fast. The output of each task is redirected into a separate file. 

```
EwsFwMgmt.py --help
usage: EwsFwMgmt.py [-h] [-c SHOW_COMMAND] [-d DEVICES] [-i INSTRUCTION_FILE]
                    [-t TOPOLOGY_FILE] [-v VARIABLE_FILE]

optional arguments:
  -h, --help           show this help message and exit
  -c SHOW_COMMAND      A show command. To be used in combination with -d. Eg:
                       show version
  -d DEVICES           Comma separate device list. To be used in combination
                       with -c. Eg: hostname1, hostname2
  -i INSTRUCTION_FILE  By default: /Config/instruction.csv
  -t TOPOLOGY_FILE     By default: /Config/topology.csv
  -v VARIABLE_FILE      By default: /Config/variable.csv
  ```
  
## Configuration Files
### The Topology File
This is a CSV file that lists the different sites and corresponding site ID and FW management IP address.

Syntax of the file is the following:
```
Hostname,City,country,site ID,mgt IP,
BELBRU,Brussels,Belgium,1,192.168.1.1,
BELANT,Antwerp,Belgium,2,192.168.2.1,
```

The default location for this file is Config/topology.csv

### The instruction file
This file defines a set of instruction to be applied to a list of firewalls.   
When running in "set command" mode, the script parses this file and apply the instructions under the set_commands section to the firewalls in the devices list.  

Syntax of the file is the following:
```
devices: BELBRU,BELANT
set_commands:
 set interfaces ge-0/0/0 unit 0 family inet address 203.0.113.5
 set interfaces ge-0/0/1 unit 0 family inet address 203.0.113.6
 set security zones security-zone trust interfaces ge-0/0/0
 set security zones security-zone untrust interfaces ge-0/0/1
 set security address-book Eng-dept address a1 203.0.113.1
 set security address-book Eng-dept address a2 203.0.113.2
 set security address-book Eng-dept address a3 203.0.113.3
 set security address-book Eng-dept address a4 203.0.113.4
 whatever you have in mind
```

Important remarks:
1. The script takes care of going in configuration mode as well as committing the changes. Hence configuration and commit must not be part of the command set.
2. Devices is a coma separated list of Hostname (see first column in the topology file)
3. **all_devices** can be used in replacement of a device list. So "devices: all_devices". In that case, the set_commands are applied to all firewall listed in the topology file. 

The default location for this file is Config/instruction.csv

### The Variable File
This is a CSV file that list, for 
