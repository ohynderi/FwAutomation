# FwAutomation
## Overview

The purpose of this script is to automate the provision of Juniper SRX firewalls using the Juniper PyEZ Python libraries.

The script can be ran in two modes:
1. **show command**: this is to apply one show command, given as a script argument, to one ore more firewall(s).
2. **set command**: this is to apply a set of instructions to one or more firewall(s).

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

This is a CSV file that lists the different sites, site ID and corresponding FW management IP address.

File syntax is the following:
```
Hostname,City,country,site ID,mgt IP,
BELBRU,Brussels,Belgium,1,192.168.1.1,
BELANT,Antwerp,Belgium,2,192.168.2.1,
```

Default file location: Config/topology.csv


### The instruction file

When running in "set command" mode, the script parses this file and apply the instructions under the *set_commands* section to the firewalls included the devices list.  

File syntax is the following:
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

The instruction file may include multiple instruction block. Sor for instance:
```
devices: BELBRU
set_commands:
 set interfaces ge-0/0/0 unit 0 family inet address 203.0.113.5
 set interfaces ge-0/0/1 unit 0 family inet address 203.0.113.6
devices: BELANT
set_commands:
 set security address-book Eng-dept address a1 203.0.113.1
 set security address-book Eng-dept address a2 203.0.113.
```

Important remarks:
1. The script takes care of going in configuration mode as well as committing the changes. Hence configuration and commit must not be part of the command set.
2. Devices is a coma separated list of Hostname (see first column in the topology file)
3. **all_devices** can be used in replacement of a device list. So "devices: all_devices". In that case, the set_commands are applied to all firewall listed in the topology file. 

Default file location: Config/instruction.csv

### The Variable File
This is a CSV file that defines some variables and corresponding values for each site. The variable names is given by the CSV header.   
When generating a task for a specific site, the script replaces matching variables in the command set by the corresponding value for the site. 

File syntax is the following:
```
site id,variable1, variable2, variable3, .... variable<n>
1,site1_value1,site1_value2,site1_value3,.... site1_value<n> 
2,site2_value1,site2_value2,site2_value3,.... site2_value<n> 
```
Site id must match the topology file.

So for instance:
```
site id,hostname,network1, network2
1,FW_BELBRU,10.1.0.0/24,10.1.1.0/24
2,FW_BELANT,10.2.0.0/24,10.2.1.0/24
```

Those variable can then later be used in the instruction file.
```
devices: all_devices
set_commands:
 set security address-book my_zone address end_user_subnet1 network1
 set security address-book my_zone address end_user_subnet2 network2
```

This will generate task for BELBRU with below instruction set:
```
set security address-book my_zone address end_user_subnet1 10.1.0.0/24
set security address-book my_zone address end_user_subnet2 10.1.1.0/24
```
...same for BELANT:
```
set security address-book my_zone address end_user_subnet1 10.2.0.0/24
set security address-book my_zone address end_user_subnet2 10.2.1.0/24
```

# Script Execution
## Mode
### show command

See below how to run a show command on a list of firewall

```
EwsFwMgmt.py -c "show interfaces terse" -d "BELBRU,BELANT"
EwsFwMgmt.py -c "show interfaces terse" -d "all_devices"
```

For each firewall, a separate task will be generate. Task output is redirected to Log/Task-<id>

### set command

See below how to apply commands to a list of firewalls.
```
EwsFwMgmt.py -i instruction.txt -t topology.csv -v variables.csv
EwsFwMgmt.py
```

## Execution Examples
