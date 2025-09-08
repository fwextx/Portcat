from PyQt5.QtCore import QThread, pyqtSignal
import psutil
import netifaces
import time

class ConnectionMonitor(QThread):
    update_signal = pyqtSignal(list)
    interfaces_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        interfaces = []
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            ip_list = addrs.get(netifaces.AF_INET, [{'addr': 'N/A'}])
            interfaces.append((iface, [ip['addr'] for ip in ip_list]))
        self.interfaces_signal.emit(interfaces)

        while self.running:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                try:
                    proc_name = psutil.Process(conn.pid).name() if conn.pid else "N/A"
                except:
                    proc_name = "N/A"
                connections.append({
                    "pid": conn.pid,
                    "proc": proc_name,
                    "laddr": laddr,
                    "raddr": raddr,
                    "status": conn.status
                })
            self.update_signal.emit(connections)
            time.sleep(3)
