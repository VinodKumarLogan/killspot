import datetime, time

def create_log_filename():
	log_file = "../log/" + str(int(datetime.datetime.now().timestamp())) + ".log"
	file = open(log_file, "a")
	file.close()
	return log_file

def write_to_log_file(log_file, data):
	file = open(log_file, "a")
	file.write(get_current_time() + " " + str(data) + "\n")
	file.close()	

def get_current_time():
	return str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
