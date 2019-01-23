from access_points import get_scanner
from logger import create_log_file, get_current_time

def retrieve_access_points():
	wifi_scanner = get_scanner()
	access_points = dict()
	for ap in wifi_scanner.get_access_points():
		access_points[ap['ssid']] = ap['bssid']
	for ap,mac in access_points.items():
		print("Access Points: ", ap, " ; MAC Address: ", mac)
	return access_points

def main():
	log_file = "../log/" + create_log_file()
	aps = retrieve_access_points()
	file = open(log_file, "a")
	file.write(get_current_time() + " " + str(aps) + "\n")
	file.close()

if __name__=="__main__":
	main()