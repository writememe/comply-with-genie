#!/usr/bin/env python
"""
This is a basic proof of concept using Nornir and Genie
to retrieve data from Cisco devices.
"""

# Import modules
import json
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir import InitNornir
from nornir.plugins.tasks.files import write_file
import pathlib


def n_genie(task, command):
    """
    #TODO: Fix documentation
    :param task:
    :param command:
    :return:
    """
    # Assign command directory to variable
    cmd_dir = "commands"
    # Assign hostname directory to a variable
    host_dir = task.host.name
    # Assign the destination directory to a variable. i.e commands/hostname/
    entry_dir = cmd_dir + "/" + host_dir
    # Create command directory and/or check that it exists
    pathlib.Path(cmd_dir).mkdir(exist_ok=True)
    # Create entry directory and/or check that it exists
    pathlib.Path(entry_dir).mkdir(exist_ok=True)
    try:
        # Gather command result using netmiko_send_command and assign to a variable
        cmd_result = task.run(
            task=netmiko_send_command,
            name="Netmiko Send Command",
            command_string=command,
            use_textfsm=False,
            use_genie=True,
        )
        # Write the results to a JSON, using the convention <command>.json
        task.run(
            task=write_file,
            content=json.dumps(cmd_result[0].result, indent=2),
            filename=f"" + str(entry_dir) + "/" + str(command) + ".json",
        )
    # Handle NAPALM Not Implemented Error exceptions
    except NotImplementedError:
        return "Getter Not Implemented"


def n_cmd_parser():
    # Initialize Nornir and define the inventory variables.
    nr = InitNornir(
        inventory={
            "options": {
                "host_file": "inventory/hosts.yaml",
                "group_file": "inventory/groups.yaml",
                "defaults_file": "inventory/defaults.yaml",
            }
        }
    )
    """
    The following block of lists are the supported parsers per OS based
    on the website:
    https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers
    """
    ios_commands = [
        "show version",
        "show ip route",
        "show inventory",
        "show ip interface",
        "show vtp status",
        "show users",
        "show ntp associations",
        "cbd",  # fake command for testing purposes
    ]

    nxos_commands = [
        "show version",
        "show feature",
        "show ip arp",
        "show ip route",
        "show ip arp",
        "show inventory",
        "show ip interface",
        "show vtp status",
        "show users",
        "show ntp associations",
        "show lldp neighbors detail",
    ]

    """
    The following block of code assigns a filter based on platform to a variable.
    This variable is used later on to apply logic in for loops
    """
    ios_devices = nr.filter(platform="ios")
    nxos_devices = nr.filter(platform="nxos")
    iosxr_devices = nr.filter(platform="iosxr")
    print(iosxr_devices)
    # IOS Platform Block
    for host in ios_devices.inventory.hosts.items():
        # Assign the hostname to a variable from the host tuple
        hostname = host[0]
        # Starting processing of a host
        print("** Start Processing Host: " + str(hostname))
        # log_file.write("** Start Processing Host: " + str(hostname) + "\n")
        for cmd in ios_commands:
            # Start collecting the command outputs
            print("Processing " + str(cmd) + " Command ... ")
            # log_file.write("Processing " + str(cmd) + " config ... " + "\n")
            # Execute the n_genie function
            configs = nr.run(task=n_genie, command=cmd, num_workers=1)
            # Debur print
            print(configs)
    # NXOS Platform Block
    for host in nxos_devices.inventory.hosts.items():
        # Assign the hostname to a variable from the host tuple
        hostname = host[0]
        # Starting processing of a host
        print("** Start Processing Host: " + str(hostname))
        # log_file.write("** Start Processing Host: " + str(hostname) + "\n")
        for cmd in nxos_commands:
            # Start collecting the command outputs
            print("Processing " + str(cmd) + " Command ... ")
            # log_file.write("Processing " + str(cmd) + " config ... " + "\n")
            # Execute the n_genie function
            configs = nr.run(task=n_genie, command=cmd, num_workers=1)
            print(configs)


# Execute function
n_cmd_parser()
