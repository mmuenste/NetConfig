#! env/Scripts/python
import yaml
import argparse
import sys
import cisco_device
from netmiko import exceptions

def main():
    descr = """
    ExperTeach Gesellschaft fuer Netzwerkkompetenz mbH
    ==================================================

    cconfig (-->copy config): Tool zum Kopieren der Running-Config von Cisco Devices
    an einen TFTP-Server
    Das Tool ist konzipiert fuer Cisco IOS (Telnet, SSH) und Cisco NX-OS (SSH).
    """

    parser = argparse.ArgumentParser(description=descr,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("File", help=("Das File cconfig.yml mit den " +
                                      "IP-Adressen von TFTP-Server und " +
                                      "den Cisco Devices"))

    args = parser.parse_args()
    
    print("*** Start copy config ***", end="\n\n")

    with open(args.File) as fobj:
        cconfig_yml_file = yaml.load(fobj, Loader=yaml.Loader)

    tftp_ip = cconfig_yml_file["tftp_server"]
    filename_ende = cconfig_yml_file["filename_ende"]

    for device in cconfig_yml_file["devices"]:

        device_obj = cisco_device.create_device(ip=device["ip"],
                                                username=device["username"],
                                                password=device["password"],
                                                secret=device["secret"],
                                                connection=device["connection"],
                                                platform=device["platform"])

        try:
            device_obj.config_to_tftp(tftp_ip=tftp_ip,
                                      filename_ende=filename_ende)

        except exceptions.NetmikoAuthenticationException as ex:
            print(ex, end="\n\n")
            continue
        except (TimeoutError, exceptions.NetmikoTimeoutException) as ex:
            print(f"{device['ip']}", ex, end="\n\n")
            continue

    print("*** Vorgang abgeschlossen! ***")

    return 0


if __name__ == "__main__":
    sys.exit(main())
