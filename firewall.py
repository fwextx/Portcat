import os
import platform

def block_ip(ip):
    if platform.system() == "Windows":
        os.system(f'netsh advfirewall firewall add rule name="PortcatBlock_{ip}" dir=out action=block remoteip={ip}')
        os.system(f'netsh advfirewall firewall add rule name="PortcatBlock_{ip}" dir=in action=block remoteip={ip}')

def unblock_ip(ip):
    if platform.system() == "Windows":
        os.system(f'netsh advfirewall firewall delete rule name="PortcatBlock_{ip}"')
