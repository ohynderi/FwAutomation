import re

def str_to_device_list(str1):
    print(str1)
    return [device.lstrip().rstrip() for device in re.split(':', str1)[1].split(',')]

def list_to_command_set(cmd_list, site_id):
    return [re.sub(r'(?<=\.)X(?=\.[0-9]+)', site_id, str1) for str1 in cmd_list]