import subprocess
import datetime
import argparse
import os

parser = argparse.ArgumentParser(description='Process a Dashcam MOV file\'s GPS Track, stops and get an equivalent GPX file')
parser.add_argument('-V', '--video', required=True)
parser.add_argument('-O', '--output', required=False, default='out.gpx')
parser.add_argument('-S', '--splice_name', required=False, default='out')
args = parser.parse_args()
#FILE = "data/2020_0924_120847_004.mov"
FILE = args.video
OUTPUT = args.output
SPLICE = args.splice_name
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

###########################################################

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


def stops_by_location(dict_arr):
    stops = []
    stop_start = ""
    stop_end = ""

    stop_loc_start_lat = dict_arr[0]["latitude"]
    stop_loc_start_long = dict_arr[0]["longitude"]

    start_time = dict_arr[0]["date/time"]

    i = 0
    #print(stop_loc_start_lat)
    #print(stop_loc_start_long)
    while(i < len(dict_arr)):
#        if(i == 188):
#            print(stop_start, stop_loc_start_lat, stop_loc_start_long)
#        if(i == 189):
#            print(stop_start, stop_loc_start_lat, stop_loc_start_long)
#        if(i == 190):
#            print(stop_start, stop_loc_start_lat, stop_loc_start_long)

        if(dict_arr[i]["latitude"] == stop_loc_start_lat and dict_arr[i]["longitude"] == stop_loc_start_long):
            if (stop_start == ""):
                stop_start = dict_arr[i]["date/time"]
            last_stop = dict_arr[i]["date/time"]

        if(stop_start != "" and (dict_arr[i]["latitude"] != stop_loc_start_lat or dict_arr[i]["longitude"] != stop_loc_start_long)):
            stop_end = last_stop
            rel_stop_start, rel_stop_end = process_time_frame(stop_start, stop_end, start_time)
            if(rel_stop_start != rel_stop_end):
                stop_frame = rel_stop_start + " " + rel_stop_end
                stops.append(stop_frame)

            stop_start = ""
            stop_end = ""



        stop_loc_start_lat = dict_arr[i]["latitude"]
        stop_loc_start_long = dict_arr[i]["longitude"]




        i+=1

    return stops

###########################################################

def parse_gps_track(et_out):
    gps_track_start = et_out.find("GPS")
    gps_track_end = et_out.find("Image Size")
    gps_track = et_out[gps_track_start:gps_track_end]
    if (os.name == 'nt'):
        gps_track_arr = gps_track.split("\r\n")
    if (os.name == 'posix'):
        gps_track_arr = gps_track.split("\n")

    gps_track_arr.pop()
    return gps_track_arr

def quick_trim(file, output, start, end):
    trim_command = "ffmpeg -y -i {} -ss {} -to {} -c copy {}".format(file, start, end, output)
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
        dict["latitude"] = deg_lat
    elif (i.find("GPS Longitude") != -1):
        deg_long = i.split(": ")[-1]
        dict["longitude"] = deg_long
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

create_gpx(dict_arr)
#print(dict_arr[35:38])
stops1 = stops_by_location(dict_arr)
#print(stops1)

for i in range(len(stops1)):
    start, end = stops1[i].split(" ")
    trim_res = quick_trim(FILE, SPLICE + "-" + str(i + 1) + ".mov", start, end)

print("Processed using stops by readings...")