import datetime, time

def create_log_file():
	return str(int(datetime.datetime.now().timestamp())) + ".log"

def get_current_time():
	return str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
