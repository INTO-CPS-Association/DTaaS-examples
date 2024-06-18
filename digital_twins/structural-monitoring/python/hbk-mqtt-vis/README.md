# A summary of files

| file name | purpose |
|:---|:---|
| config.json | config format for MQTT clients |
| mqtt-pub.py | skeleton publisher code; uses config.json |
| mqtt-sub_array.py | converts the streaming MQTT data into byte array and prints it |
| mqtt-sub_multiprocess.py | skeleton multi-threaded code |
| mqtt-sub_SysId.py | collection of two MQTT sensor data into python dictionary (please note that filling up the dictionary is not happening correctly; there is a bug in lines 49 to 53 of the file) |
| sysid_config.json | config format for mqtt-sub_SysId.py file |
| mqtt-sub.py | live plots of streaming MQTT sensor data for one sensor |
