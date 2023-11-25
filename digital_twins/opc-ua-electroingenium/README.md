# Install and Demonstrate

1. [Install Python 3.10](https://computingforgeeks.com/how-to-install-python-on-ubuntu-linux-system/).
   The program does not work on earlier versions of Python.
1. [Install pip3 for python3.10](https://stackoverflow.com/questions/69503329/pip-is-not-working-for-python-3-10-on-ubuntu/).
   `curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10`
1. Install pip dependencies. `pip3.10 install fmpy opcua odfpy pandas cryptography`
1. Install Prosys OPC UA server from
   [here](https://www.prosysopc.com/opcua/apps/JavaServer/dist/5.4.6-148/prosys-opc-ua-simulation-server-linux-x64-5.4.6-148.sh). **This server is not running properly in DTaaS user workspace but works well on Ubuntu 22.04.**
   **It seems there is a bug in the OPC UA server. This needs debugging.**
1. Start OPC UA server once and then close. This action will create
   `~/.prosysopc/prosys-opc-ua-simulation-server` directory.
1. Copy _default.simconf_ file into
   `~/.prosysopc/prosys-opc-ua-simulation-server` directory.
2. Start the OPC UA server again
    1. Make sure that the server is running at a port. Copy
       **Connection Address (UA TCP)**. This is used inside Main.py
    2. Replace
       `url = 'opc.tcp://Ubuntu.myguest.virtualbox.org:53530/OPCUA/SimulationServer'`
       with new **Connection Address**.
3. Run the script.
   `python Main.py`
