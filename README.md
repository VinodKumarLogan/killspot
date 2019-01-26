# killspot
A simulator for man in the middle attack for public Wi-Fi hotspots and Access points

Requirements:

Linux:

Python3: sudo apt-get install python3 python3-pip

Access Points: pip3 install access_points

Network Interfaces: pip3 install netifaces

Argparse: pip3 install argparse



Usage:

Need to be run as root user

sudo -i


python3 hotspot.py -s <SSID> -i <Wi-Fi Interface>

Example: 

python3 hotspot.py -s killspot-access -i wlan0