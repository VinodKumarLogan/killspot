from access_points import get_scanner

def retrieve_access_points():
	wifi_scanner = get_scanner()
	access_points = dict()
	for ap in wifi_scanner.get_access_points():
		#print(ap)
		access_points[ap['ssid']] = ap['bssid']
	for ap,mac in access_points.items():
		print("Access Points: ", ap, " ; MAC Address: ", mac)
	return access_points

retrieve_access_points()