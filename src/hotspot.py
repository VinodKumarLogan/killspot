from access_points import get_scanner
from logger import create_log_filename, get_current_time, write_to_log_file
import argparse

def retrieve_access_points():
	wifi_scanner = get_scanner()
	access_points = dict()
	for ap in wifi_scanner.get_access_points():
		access_points[ap['ssid']] = ap['bssid']
	for ap,mac in access_points.items():
		print("Access Points: ", ap, " ; MAC Address: ", mac)
	return access_points

def create_host(ssid, interface, password):
	file = open("hostapd.conf", "a")
	host_data = '''
beacon_int=100
ssid=%s
interface=%s
driver=%s
channel=6
ctrl_interface=hostapd_ctrl
ctrl_interface_group=0
ap_isolate=0
hw_mode=g
''' % (ssid, interface, "nl80211")
	print(host_data)
	file.write(host_data)
	file.close()
	file = open("dnsmasq.conf", "a")
	dhcp_data = '''
listen-address=192.168.12.1
bind-dynamic
dhcp-range=192.168.12.1,192.168.12.254,255.255.255.0,24hr
dhcp-option-force=option:router,192.168.12.1
dhcp-option-force=option:dns-server,192.168.12.1
dhcp-option-force=option:mtu,1500
no-hosts
'''
	file.write(dhcp_data)
	print(dhcp_data)
	file.close()

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