"""Klassen für die Verwendung mit Netmiko
"""
import abc
from netmiko import ConnectHandler

def create_device(ip, username, password,
                  secret, connection, platform):
    """Eine Convenience Function zur Instanziierung
    der passenden Klasse
    """
    if platform == "cisco_ios":
        return CiscoIos(ip=ip, username=username, password=password,
                         secret=secret, connection=connection, platform=platform)
    elif platform == "cisco_nxos":
        return CiscoNxos(ip=ip, username=username, password=password,
                         secret=secret, connection=connection, platform=platform)

class CiscoDevice:
    """Abstrace Base Class fuer Klasse, die man mit 
    Netmikos ConnectHandler verwendet.
    """
    def __init__(self, ip, username,password,
                 secret, connection, platform):
        self.ip = ip
        self.username = username
        self.password = password
        self.secret = secret
        if platform == "cisco_ios" and connection == "telnet":
            self.device_type = f"{platform}_{connection}"
        else:
            self.device_type = platform

    @abc.abstractmethod
    def config_to_tftp(self, tftp_ip, filename_ende):
        pass

    @abc.abstractmethod
    def clean_up(self):
        """Methode, um die startup-config zu löschen, auf Switchen die vlan.dat zu löschen"""
        pass

    @abc.abstractmethod
    def schedule_reload(self):
        """Methode, um einen Neustart mit 2 Min. Verzögerung anzustoßen"""
        pass

class CiscoIos(CiscoDevice):
    def config_to_tftp(self, tftp_ip, filename_ende):
        with ConnectHandler(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            device_type=self.device_type,
                            secret=self.secret) as session:
                
            print(f"Verbunden mit {self.ip}")
            session.enable()
            prompt_quiet = ["file prompt quiet"]
            session.send_config_set(prompt_quiet)
                
            hostname = session.send_command("show running-config " +
                                                "| in hostname").split()[-1]
                
            copy_cmd = (f"copy running-config tftp://{tftp_ip}" +
                        f"/{hostname}_{filename_ende}.cfg")
                
            session.send_command(copy_cmd)
            print(f"{self.ip}: Config kopiert!", end="\n\n")

    def clean_up(self):
        with ConnectHandler(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            device_type=self.device_type,
                            secret=self.secret) as session:
            print(f"Verbunden mit {self.ip}")
            session.enable()

            # 1) Startup-config löschen
            cmd_list_erase = [["erase startup-config", "confirm"],
                              ["\n", ""]]
            session.send_multiline(cmd_list_erase)

            # 2) Auf Switchen vlan.dat löschen
            cmd_list_vlan = [["delete vlan.dat", "vlan.dat"],
                             ["\n", "confirm"],
                             ["\n", ""]]

            session.send_multiline(cmd_list_vlan)

            print(f"{self.ip}: Erase start-up config [auf Switch auch delete vlan.dat]!")
    
    def schedule_reload(self):
         with ConnectHandler(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            device_type=self.device_type,
                            secret=self.secret) as session:
            print(f"Verbunden mit {self.ip}")
            session.enable()

            # Neustart anstoßen
            cmd_list_reload = [["reload in 2", "confirm"],
                               ["\n", ""]]
            session.send_multiline(cmd_list_reload)
            print(f"{self.ip}: Neustart in 2 Minuten!")


class CiscoNxos(CiscoDevice):

    def config_to_tftp(self, tftp_ip, filename_ende):
        with ConnectHandler(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            device_type=self.device_type
                            ) as session:
            
            print(f"Verbunden mit {self.ip}")
            
            hostname = session.send_command("show run | in hostname|switchname").split()[-1]
            
            copy_cmd = (f"copy running-config tftp://{tftp_ip}" +
                        f"/{hostname}_{filename_ende}.cfg vrf management")
            
            session.send_command(copy_cmd)
            print(f"{self.ip}: Config kopiert!", end="\n\n")

    def clean_up(self):
         with ConnectHandler(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            device_type=self.device_type
                            ) as session:
             
            print(f"Verbunden mit {self.ip}")

            # 1) Startup-config löschen
            cmd_list_erase = [["write erase", "proceed anyway"],
                              ["y", ""]]
            session.send_multiline(cmd_list_erase)

            print(f"{self.ip}: Erase start-up config!")

    def schedule_reload(self):
        with ConnectHandler(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            device_type=self.device_type
                            ) as session:
             
            print(f"Verbunden mit {self.ip}")

             # 2) Neustart anstoßen
            cmd_list_reload = [["reload in 120", "reboot the system"],
                               ["y", ""]]
            session.send_multiline(cmd_list_reload)
             
            print(f"{self.ip}: Neustart in 2 Minuten!")
