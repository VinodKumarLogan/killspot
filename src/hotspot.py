from logger import create_log_filename, get_current_time, write_to_log_file
import argparse
import subprocess
import netifaces
import os

def create_host(ssid, interface, mac_address):
	pwd = os.getcwd()
	print(pwd)
	os.system('''mkdir %s/configs
mkdir %s/configs/hostapd_ctrl
mkdir %s/configs/ifaces
touch %s/configs/ifaces/ks0
echo ks0 > %s/configs/wifi_iface
echo %s > %s/configs/nat_internet_iface
touch %s/configs/dnsmasq.leases
echo 0 > %s/configs/ip_forward
echo 0 > %s/configs/%s_forwarding
touch %s/configs/hostapd.conf
touch %s/configs/dnsmasq.conf
''' % (pwd, pwd, pwd, pwd, pwd, interface, pwd, pwd, pwd, pwd, interface, pwd, pwd))
	file = open("%s/configs/hostapd.conf" % (pwd), "w")
	host_data = '''beacon_int=100
ssid=%s
interface=ks0
driver=%s
channel=6
ctrl_interface=%s/configs/hostapd_ctrl
ctrl_interface_group=0
ignore_broadcast_ssid=0
ap_isolate=0
hw_mode=g
''' % (ssid, "nl80211", pwd)
	print(host_data)
	file.write(host_data)
	file.close()
	file = open("%s/configs/dnsmasq.conf" % (pwd), "w")
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
	print("Adding new interface ks0 with ",mac_address)
	interface_commands = '''
echo -e "\\n\\n[keyfile]\\nunmanaged-devices=interface-name:ks0" >> /etc/NetworkManager/NetworkManager.conf
network_manager_pid=$(pidof NetworkManager)
[[ -n "$network_manager_pid" ]] && kill -HUP $network_manager_pid
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
	file = open("%s/configs/commands.sh" % (pwd), "w")
	file.write(interface_commands+"\n"+dns_commands)
	file.close()
	os.system('chmod 777 %s/configs/commands.sh' % (pwd))
	os.system('bash %s/configs/commands.sh' % (pwd)) 
	start_access_point = '''
dnsmasq -C %s/configs/dnsmasq.conf -x %s/configs/dnsmasq.pid -l %s/configs/dnsmasq.leases -p 5353
stdbuf -oL hostapd %s/configs/hostapd.conf &
''' % (pwd, pwd, pwd, pwd)
	file = open("%s/configs/deploy.sh" % (pwd), "w")
	file.write(start_access_point)
	file.close()
	os.system('chmod 777 %s/configs/deploy.sh' % (pwd))
	os.system('bash %s/configs/deploy.sh' % (pwd))
	

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-s','--ssid', help='SSID for the new access point', required=True, default="Killspot")
	parser.add_argument('-i','--interface', help='Name of the Wi-Fi interface', required=True, default="wlan0")
	parser.add_argument('-m','--mac_address', help='MAC address of the interface', required=True, default="00:00:00:00:00:00")
	args = vars(parser.parse_args())
	ssid, interface, mac_address = args['ssid'], args['interface'], args['mac_address'] 
	print("Create new access point with SSID ", ssid, " ; on Wi-Fi Interface ", interface, " with mac address ", mac_address)
	create_host(ssid, interface, mac_address)
	
if __name__=="__main__":
	main()