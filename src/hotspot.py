from access_points import get_scanner
from logger import create_log_filename, get_current_time, write_to_log_file
import argparse
import subprocess
import netifaces
import os

def retrieve_access_points():
	wifi_scanner = get_scanner()
	access_points = dict()
	for ap in wifi_scanner.get_access_points():
		access_points[ap['ssid']] = ap['bssid']
	for ap,mac in access_points.items():
		print("Access Points: ", ap, " ; MAC Address: ", mac)
	return access_points

def create_host(ssid, interface, password):
	file = open("hostapd.conf", "w")
	host_data = '''beacon_int=100
ssid=%s
interface=ks0
driver=%s
channel=6
ctrl_interface=hostapd_ctrl
ctrl_interface_group=0
ap_isolate=0
hw_mode=g
''' % (ssid, "nl80211")
	print(host_data)
	file.write(host_data)
	file.close()
	file = open("dnsmasq.conf", "w")
	dhcp_data = '''listen-address=192.168.12.1
bind-dynamic
dhcp-range=192.168.12.1,192.168.12.254,255.255.255.0,24h
dhcp-option-force=option:router,192.168.12.1
dhcp-option-force=option:dns-server,192.168.12.1
dhcp-option-force=option:mtu,1500
no-hosts
'''
	file.write(dhcp_data)
	print(dhcp_data)
	file.close()
	mac_address = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr'][:-2] + "e2"
	print("Adding new interface ks0 with ",mac_address)
	interface_commands = '''chmod 777 hostapd.conf dnsmasq.conf
iw dev %s interface add ks0 type __ap
ip link set down dev ks0
ip link set dev ks0 address %s
ip addr flush ks0
ip link set up dev ks0
ip addr add 192.168.12.1/24 broadcast 192.168.12.255 dev ks0
iptables -w -t nat -I POSTROUTING -s 192.168.12.0/24 ! -o ks0 -j MASQUERADE
iptables -w -I FORWARD -i ks0 -s 192.168.12.0/24 -j ACCEPT
iptables -w -I FORWARD -i %s -d 192.168.12.0/24 -j ACCEPT
echo 1 > /proc/sys/net/ipv4/conf/%s/forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
modprobe nf_nat_pptp > /dev/null 2>&1''' % (interface, mac_address, interface, interface)

	dns_commands = '''
iptables -w -I INPUT -p tcp -m tcp --dport 5353 -j ACCEPT
iptables -w -I INPUT -p udp -m udp --dport 5353 -j ACCEPT
iptables -w -t nat -I PREROUTING -s 192.168.12.0/24 -d 192.168.12.1 -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 5353
iptables -w -t nat -I PREROUTING -s 192.168.12.0/24 -d 192.168.12.1 -p udp -m udp --dport 53 -j REDIRECT --to-ports 5353
iptables -w -I INPUT -p udp -m udp --dport 67 -j ACCEPT'''
	print(interface_commands, dns_commands)
	file = open("commands.sh", "w")
	file.wite(interface_commands+"\n"+dns_commands)
	file.close()
	os.system('chmod 777 -R commands.sh')
	subprocess.call(["commands.sh"])
	start_access_point = '''	
dnsmasq -C dnsmasq.conf -x dnsmasq.pid -l dnsmasq.leases -p 5353
mkdir hostapd_ctrl
stdbuf -oL hostapd hostapd.conf &
'''

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-s','--ssid', help='SSID for the new access point', required=True, default="Killspot")
	parser.add_argument('-i','--interface', help='Name of the Wi-Fi interface', required=True, default="wlan0")
	parser.add_argument('-p','--password', help='Password for the new access point', required=False, default=None)	
	args = vars(parser.parse_args())
	aps = retrieve_access_points()
	filename = create_log_filename()
	write_to_log_file(filename, aps)
	ssid, interface, password = args['ssid'], args['interface'], args['password'] 
	print("Create new access point with SSID ", ssid, " ; on Wi-Fi Interface ", interface, " with password ", password)
	create_host(ssid, interface, password)
	
if __name__=="__main__":
	main()