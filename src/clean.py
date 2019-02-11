def main():
	pwd = os.getcwd()
	pid_file = open('%s/configs/hostapd.pid' % (pwd), 'r')
	pid = str(pid_file.read().strip())
	pid_file.close()
	wifi_file = open('%s/configs/wifi_iface' % (pwd), 'r')
	wifi = str(wifi_file.read().strip())
	wifi_file.close()
	nat_file = open('%s/configs/nat_internet_iface' % (pwd), 'r')
	nat = str(nat_file.read().strip())
	nat_file.close()
	os.system('kill -9 %s' % (pid))
	os.system('''
cp -f %s/configs/ip_forward /proc/sys/net/ipv4
iptables -w -t nat -D POSTROUTING -s192.168.16.0/24 ! -o %s -j MASQUERADE
iptables -w -D FORWARD -i %s -s 192.168.16.0/24 -j ACCEPT
iptables -w -D FORWARD -i %s -d 192.168.16.0/24 -j ACCEPT
iptables -w -D INPUT -p tcp -m tcp --dport $DNS_PORT -j ACCEPT
iptables -w -D INPUT -p udp -m udp --dport $DNS_PORT -j ACCEPT
iptables -w -t nat -D PREROUTING -s 192.168.16.0/24 -d 192.168.16.1 -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 5353
iptables -w -t nat -D PREROUTING -s 192.168.16.0/24 -d 192.168.16.1 -p udp -m udp --dport 53 -j REDIRECT --to-ports 5353
iptables -w -D INPUT -p udp -m udp --dport 67 -j ACCEPT
ip link set down dev ks0
ip addr flush ks0
iw dev ks0 del
rm -rf %s/configs
sed -i '$ d' /etc/NetworkManager/NetworkManager.conf
sed -i '$ d' /etc/NetworkManager/NetworkManager.conf
service network-manager restart
''' % (pwd, pwd, wifi, wifi, nat, pwd))

if __name__=="__main__":
	main()