import abc
from netmiko import ConnectHandler

def create_device(ip, username, password,
                  secret, connection, platform):
    if platform == "cisco_ios":
        return CiscoIos(ip=ip, username=username, password=password,
                         secret=secret, connection=connection, platform=platform)
    elif platform == "cisco_nxos":
        return CiscoNxos(ip=ip, username=username, password=password,
                         secret=secret, connection=connection, platform=platform)

class CiscoDevice:
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
    def erase_start_up(self):
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
