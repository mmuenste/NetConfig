#! env/Scripts/python
import concurrent.futures
import argparse
import sys
import cisco_device
from netmiko import exceptions
import yaml


def call_clean_up(device):

    device_obj = cisco_device.create_device(ip=device["ip"],
                                            username=device["username"],
                                            password=device["password"],
                                            secret=device["secret"],
                                            connection=device["connection"],
                                            platform=device["platform"])

    try:
        device_obj.clean_up()

    except exceptions.NetmikoAuthenticationException as ex:
        print(ex, end="\n\n")
    except (TimeoutError, exceptions.NetmikoTimeoutException) as ex:
        print(f"{device['ip']}", ex, end="\n\n")


def schedule_reloads(device):

    device_obj = cisco_device.create_device(ip=device["ip"],
                                            username=device["username"],
                                            password=device["password"],
                                            secret=device["secret"],
                                            connection=device["connection"],
                                            platform=device["platform"])

    try:
        device_obj.schedule_reload()

    except exceptions.NetmikoAuthenticationException as ex:
        print(ex, end="\n\n")
    except (TimeoutError, exceptions.NetmikoTimeoutException) as ex:
        print(f"{device['ip']}", ex, end="\n\n")
    except EOFError as ex:
        print(f"{device['ip']}", ex, "Bedingt durch Neustart", end="\n\n")


def main():
    descr = """
    ExperTeach Gesellschaft fuer Netzwerkkompetenz mbH
    ==================================================

    econfig (-->erase config): Tool zum Löschen der Startup-Config und 
     Anstoßen eines Neustarts (2 min Verzögerung) von Cisco Devices
    Das Tool ist konzipiert fuer Cisco IOS (Telnet, SSH) und Cisco NX-OS (SSH).
    """

    parser = argparse.ArgumentParser(description=descr,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("File", help=("Das File cconfig.yml mit den " +
                                      "IP-Adressen von den Cisco Devices"))

    args = parser.parse_args()
    
    print("*** Start erase config ***", end="\n\n")

    with open(args.File) as fobj:
        cconfig_yml_file = yaml.load(fobj, Loader=yaml.Loader)

    device_list = cconfig_yml_file["devices"]
    
    # Neustarts in Auftrag geben
    #with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        #e_1 = executor.map(schedule_reloads, device_list)
    e_1 = list(map(schedule_reloads, device_list))


    # Startup-Configs löschen [Bei Switchen auch vlan.dat löschen]
    #with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        #e_2 = executor.map(call_clean_up, device_list)
    e_2 = list(map(call_clean_up, device_list))

    print("*** Vorgang abgeschlossen! ***")

    return 0


if __name__ == "__main__":
    sys.exit(main())
