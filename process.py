import subprocess
import datetime
import argparse

parser = argparse.ArgumentParser(description='Process a Dashcam MOV file\'s GPS Track, stops and get an equivalent GPX file')
parser.add_argument('-V', '--video', required=True)
parser.add_argument('-O', '--output', required=False, default='out.gpx')
args = parser.parse_args()
#FILE = "data/2020_0924_120847_004.mov"
FILE = args.video
OUTPUT = args.output
command = "exiftool -ee " + FILE

def create_gpx(dict_arr):
    file = open(OUTPUT, "w")
    head = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<gpx version=\"1.0\" creator=\"ExifTool 12.06\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns=\"http://www.topografix.com/GPX/1/0\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd\">\n<trk>\n<trkseg>\n"
    tail = "</trkseg>\n</trk>\n</gpx>"

    body = ""
    for i in dict_arr:
        entry = "<trkpt lat=\"{}\" lon=\"{}\">\n<ele>{}</ele>\n<time>{}</time>\n<speed>{}</speed>\n</trkpt>\n".format(i["latitude"], i["longitude"], i["altitude"].strip(" m") if i.get("altitude") != None else 0, i["date/time"], i["speed"])
        body += entry

    gpx_content = head + body + tail
    file.write(gpx_content)
    file.close()

def get_time_attr(datetime):
    dt_arr = datetime.split(" ")
    date = dt_arr[0]
    time = dt_arr[1].strip("Z")
    year, month, day = date.split(":")
    hour, minute, second = time.split(":")
    return int(year), int(month), int(day), int(hour), int(minute), int(second)

def process_time_frame(stop_start, stop_end, start_time):
    start_year, start_month, start_day, start_hour, start_minute, start_second = get_time_attr(stop_start)
    end_year, end_month, end_day, end_hour, end_minute, end_second = get_time_attr(stop_end)
    begin_year, begin_month, begin_day, begin_hour, begin_minute, begin_second = get_time_attr(start_time)

    begin_t = datetime.datetime(begin_year, begin_month, begin_day, begin_hour, begin_minute, begin_second)
    start_t = datetime.datetime(start_year, start_month, start_day, start_hour, start_minute, start_second)
    end_t = datetime.datetime(end_year, end_month, end_day, end_hour, end_minute, end_second)
    start = start_t - begin_t
    end = end_t - begin_t

    return str(start.seconds), str(end.seconds)


def stops_by_speed(dict_arr):
    stops = []
    stop_start = ""
    stop_end = ""
    start_time = dict_arr[0]["date/time"]
    for i in dict_arr:
        if (float(i["speed"]) == 0.0):
            if (stop_start == ""):
                stop_start = i["date/time"]
            last_stop = i["date/time"]
        if ((stop_start != "") and (float(i["speed"]) != 0.0)):
            stop_end = last_stop
            rel_stop_start, rel_stop_end = process_time_frame(stop_start, stop_end, start_time)
            stop_frame = rel_stop_start + " " + rel_stop_end
            stops.append(stop_frame)
            stop_start = ""
            stop_end = ""
    return stops

def time_to_sec(stop_start, stop_end):
    time 

def parse_gps_track(et_out):
    gps_track_start = et_out.find("GPS")
    gps_track_end = et_out.find("Image Size")
    gps_track = et_out[gps_track_start:gps_track_end]
    gps_track_arr = gps_track.split("\r\n")
    gps_track_arr.pop()
    return gps_track_arr
def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    if x == 0:
        return 0

def deg_to_dec(coord):
    coord_arr = coord.split(" ")
    degrees = float(coord_arr[0])
    minutes = float(coord_arr[2].strip("'"))
    seconds = float(coord_arr[3].strip("\""))
    res = sign(degrees) * (abs(degrees) + (minutes / 60) + (seconds / 3600))
    return str(res)

def gps_track_to_json(gps_track_arr):
    return

def quick_trim(file, output, start, end):
    trim_command = "ffmpeg -y -ss {} -to {} -i {} -c copy {}".format(start, end, file, output)
    try:
        res = subprocess.check_output(trim_command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        res = e.output
    return res

try:
    res = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError as e:
    res = e.output

et_out = res.decode('utf-8')
gps_track_arr = parse_gps_track(et_out)

st = 0
dict_arr = []
dict = {}
for i in gps_track_arr:
    if (i.find("GPS Date/Time") != -1):
        if (dict.get("date/time") != None):
            dict_arr.append(dict)
        dict = {}
        dict["date/time"] = i.split(": ")[-1]
    elif (i.find("GPS Latitude") != -1):
        deg_lat = i.split(": ")[-1]
        dict["latitude"] = deg_to_dec(deg_lat)
    elif (i.find("GPS Longitude") != -1):
        deg_long = i.split(": ")[-1]
        dict["longitude"] = deg_to_dec(deg_long)
    elif (i.find("Altitude") != -1):
        dict["altitude"] = i.split(": ")[-1]
    elif (i.find("GPS Speed Ref") != -1):
        dict["speed_ref"] = i.split(": ")[-1]
    elif (i.find("GPS Speed") != -1):
        dict["speed"] = i.split(": ")[-1]
    elif (i.find("GPS Track Ref") != -1):
        dict["track_ref"] = i.split(": ")[-1]
    elif (i.find("GPS Track") != -1):
        dict["track"] = i.split(": ")[-1]
dict_arr.append(dict)

"""for i in range(0, len(gps_track_arr), 8):
    dict = {}
    dict["date/time"] = gps_track_arr[i].split(": ")[-1]
    deg_lat = gps_track_arr[i + 1].split(": ")[-1]
    dict["latitude"] = deg_to_dec(deg_lat)
    deg_long = gps_track_arr[i + 2].split(": ")[-1]
    dict["longitude"] = deg_to_dec(deg_long)
    dict["altitude"] = gps_track_arr[i + 3].split(": ")[-1]
    dict["speed"] = gps_track_arr[i+ 4].split(": ")[-1]
    dict["speed_ref"] = gps_track_arr[i + 5].split(": ")[-1]
    dict["track"] = gps_track_arr[i + 6].split(": ")[-1]
    dict["track_ref"] = gps_track_arr[i + 7].split(": ")[-1]
    dict_arr.append(dict)"""

create_gpx(dict_arr)
stops1 = stops_by_speed(dict_arr) # Array of start and end time in seconds relative to the video separated by a space

"""
SPLICE HERE
"""