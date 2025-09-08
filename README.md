# Portcat
Portcat is a lightweight, Python-based network monitoring and firewall tool. It allows you to see live network connections, block/unblock apps or IPs, and sort/filter connections.

---

## Features

- **Live Network Monitoring**: View all active connections with process name, PID, local and remote addresses, and status.  
- **Block / Unblock**: Easily block or unblock processes or IP addresses with a single click.  
- **Blocked / Unblocked Status**: Each connection shows `[BLOCKED]` or `[UNBLOCKED]`.  
- **Sorting Options**: Sort by newest → oldest, A → Z, or connection status (Established first).  
- **Filter by Blocked State**: Toggle between showing all connections, blocked only, or unblocked only.  
- **Modern UI**: Dark bubble-style interface, rounded buttons, and Chrome-style scrollbar.  
- **Auto-Refresh**: Connections update every second without disturbing your current sorting or filters.  
- **Cross-Platform Ready**: Works on Windows (requires admin rights to block/unblock IPs).  

---

## Installation

1. **Clone the repository**:

<pre>git clone https://github.com/fwextx/Portcat.git
cd Portcat</pre>

2. Set Up a Virtual Environment
- Create the Virtual Enviroment
<pre>py -m venv Portcat</pre>
- Enable the Virtual Enviroment
<pre>Portcat\Scripts\activate</pre>

3. Install Requirements
- On a Computer using Python 3.13, install the required packages:
<pre>pip install -r requirements.txt</pre>

4. Run the file 
<pre>py main.py</pre>
<h3>Administrator Privileges Required to open (To allow Firewall Modification)</h3>

Made with ❤️ by Extx / `fwextx`
