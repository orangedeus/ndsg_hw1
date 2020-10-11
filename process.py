import subprocess
import datetime
import argparse
import os
import shutil
import timeit

def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    if x == 0:
        return 0

class Process:
    def __init__(self, dir, out_gpx, out_vid, sens, noise):
        self.directory = dir
        self.output_gpx = out_gpx
        self.output_vid = out_vid
        self.sensitivity = sens
        self.noise = noise

    def start(self):
        print('[-] Starting...')
        start = timeit.default_timer()
        listdir = os.listdir(self.directory)
        concat_gps_track = self.concat_gps_track(listdir)
        print('[-] Parsing...')
        dict_arr = self.gps_dict_arr(concat_gps_track)
        dict_arr2 = self.gps_dict_arr2(concat_gps_track)
        print('[-] Creating GPX file...')
        self.create_gpx(dict_arr)
        print('[-] Concatenating...')
        self.quick_concat(listdir)
        print('[-] Getting stops...')
        stops1 = self.stops_by_speed(dict_arr)
        print('--- STOPS BY SPEED ---')
        for i in stops1:
            print(i)
        stops2 = self.stops_by_location(dict_arr)
        print('--- STOPS BY LOCATION ---')
        for i in stops2:
            print(i)
        stops3 = self.clean_stops(self.stops_by_freezedetect(self.freezedetect(self.output_vid, self.sensitivity, self.noise)))
        print('--- STOPS BY FREEZEDETECT ---')
        for i in stops3:
            print(i)
        print('[-] Splicing...')
        self.splice("speed", stops1)
        self.splice("location", stops2)
        self.splice("freezedetect", stops3)
        stop = timeit.default_timer()
        print('[-] Done! Time elapsed: {}s'.format(stop - start))

    def stop_sens(self, stop, sensitivity):
        start, end = stop.split(" ")
        if (int(end) - int(start) < sensitivity):
            return False
        else:
            return True
    
    def clean_stops(self, stops):
        new_stops = []

        prev_end = -1 * self.sensitivity
        for i in stops:
            start, end = i.split(" ")
            start, end = int(start), int(end)

            if start - prev_end < self.sensitivity:
                prev_start, prev_end = new_stops.pop().split(" ")
                new_stop = "{} {}".format(prev_start, end)
                new_stops.append(new_stop)
            else:
                new_stops.append(i)
            prev_end = end

        return new_stops

    def exiftool_call(self, file):
        exif_command = "exiftool -ee {}".format(file)
        try:
            res = subprocess.check_output(exif_command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            res = e.output
        return res

    def quick_concat(self, listdir):
        cl_comm = "("
        for i in range(len(listdir)):
            if (i != len(listdir) - 1):
                cl_comm += "echo file \'{}/{}\' &".format(self.directory, listdir[i])
            else:
                cl_comm += "echo file \'{}/{}\') > list.txt".format(self.directory, listdir[i])
        try:
            res = subprocess.check_output(cl_comm, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            res = e.output

        concat_command = "ffmpeg -y -f concat -safe 0 -i list.txt -c copy {}".format(self.output_vid)

        try:
            res = subprocess.check_output(concat_command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            res = e.output

    def splice(self, method, stops):
        if os.path.exists(method):
            shutil.rmtree(method)
        os.makedirs(method)
        for i in range(len(stops)):
            start, end = stops[i].split(" ")
            trim_res = self.quick_trim(self.output_vid, "{}/output-{}.mov".format(method, str(i + 1)), start, end)


    def concat_gps_track(self, listdir):
        concat_gps_track = []
        for i in listdir:
            et_out = self.exiftool_call("{}/{}".format(self.directory, i)).decode('utf-8')
            concat_gps_track += self.parse_gps_track(et_out)
        return concat_gps_track

    def gps_dict_arr(self, gps_track_arr): # Complexity : O(TRACKPOINTS^2)
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
                dict["latitude"] = self.deg_to_dec(deg_lat)
            elif (i.find("GPS Longitude") != -1):
                deg_long = i.split(": ")[-1]
                dict["longitude"] = self.deg_to_dec(deg_long)
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

        return dict_arr

    def gps_dict_arr2(self, gps_track_arr): # Complexity : O(TRACKPOINTS^2)
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
        return dict_arr

    def create_gpx(self, dict_arr):
        file = open(self.output_gpx, "w")
        head = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<gpx version=\"1.0\" creator=\"ExifTool 12.06\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns=\"http://www.topografix.com/GPX/1/0\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd\">\n<trk>\n<trkseg>\n"
        tail = "</trkseg>\n</trk>\n</gpx>"

        body = ""
        for i in dict_arr:
            entry = "<trkpt lat=\"{}\" lon=\"{}\">\n<ele>{}</ele>\n<time>{}</time>\n<speed>{}</speed>\n</trkpt>\n".format(i["latitude"], i["longitude"], i["altitude"].strip(" m") if i.get("altitude") != None else 0, i["date/time"], i["speed"])
            body += entry

        gpx_content = head + body + tail
        file.write(gpx_content)
        file.close()

    def get_time_attr(self, datetime):
        dt_arr = datetime.split(" ")
        date = dt_arr[0]
        time = dt_arr[1].strip("Z")
        year, month, day = date.split(":")
        hour, minute, second = time.split(":")
        return int(year), int(month), int(day), int(hour), int(minute), int(second)

    def process_time_frame(self, stop_start, stop_end, start_time):
        start_year, start_month, start_day, start_hour, start_minute, start_second = self.get_time_attr(stop_start)
        end_year, end_month, end_day, end_hour, end_minute, end_second = self.get_time_attr(stop_end)
        begin_year, begin_month, begin_day, begin_hour, begin_minute, begin_second = self.get_time_attr(start_time)

        begin_t = datetime.datetime(begin_year, begin_month, begin_day, begin_hour, begin_minute, begin_second)
        start_t = datetime.datetime(start_year, start_month, start_day, start_hour, start_minute, start_second)
        end_t = datetime.datetime(end_year, end_month, end_day, end_hour, end_minute, end_second)
        start = start_t - begin_t
        end = end_t - begin_t

        return str(start.seconds), str(end.seconds)


    def stops_by_speed(self, dict_arr): # Complexity : O(TRACKPOINTS)
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
                rel_stop_start, rel_stop_end = self.process_time_frame(stop_start, stop_end, start_time)
                stop_frame = rel_stop_start + " " + rel_stop_end
                if (self.stop_sens(stop_frame, self.sensitivity)):
                    stops.append(stop_frame)
                stop_start = ""
                stop_end = ""
        if (stop_start != ""):
            rel_stop_start, rel_stop_end = self.process_time_frame(stop_start, last_stop, start_time)
            stop_frame = rel_stop_start + " " + rel_stop_end
            if (self.stop_sens(stop_frame, self.sensitivity)):
                stops.append(stop_frame)
        return stops

    def stops_by_location(self, dict_arr): # Complexity : O(TRACKPOINTS)
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
                rel_stop_start, rel_stop_end = self.process_time_frame(stop_start, stop_end, start_time)
                if(rel_stop_start != rel_stop_end):
                    stop_frame = rel_stop_start + " " + rel_stop_end
                    if (self.stop_sens(stop_frame, self.sensitivity)):
                        stops.append(stop_frame)
                stop_start = ""
                stop_end = ""
                
            stop_loc_start_lat = dict_arr[i]["latitude"]
            stop_loc_start_long = dict_arr[i]["longitude"]
            i+=1
        return stops

    def parse_gps_track(self, et_out):
        gps_track_start = et_out.find("GPS")
        gps_track_end = et_out.find("Image Size")
        gps_track = et_out[gps_track_start:gps_track_end]
        if (os.name == 'nt'):
            gps_track_arr = gps_track.split("\r\n")
        if (os.name == 'posix'):
            gps_track_arr = gps_track.split("\n")

        gps_track_arr.pop()
        return gps_track_arr

    def deg_to_dec(self, coord):
        coord_arr = coord.split(" ")
        degrees = float(coord_arr[0])
        minutes = float(coord_arr[2].strip("'"))
        seconds = float(coord_arr[3].strip("\""))
        res = sign(degrees) * (abs(degrees) + (minutes / 60) + (seconds / 3600))
        return str(res)

    def gps_track_to_json(self, gps_track_arr):
        return

    def quick_trim(self, file, output, start, end):
        trim_command = "ffmpeg -y -i {} -ss {} -to {} -c copy {}".format(file, start, end, output)
        try:
            res = subprocess.check_output(trim_command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            res = e.output
        return res
    
    def freezedetect(self, file, sensitivity, noise):
        command = "ffmpeg -i {} -vf \"freezedetect=n=-{}dB:d={}\" -map 0:v:0 -f null -".format(file, noise, sensitivity)
        try:
            res = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            res = e.output
        return res.decode('utf-8')

    def get_sec(self, str):
        sec = ""

        for i in str:
            if not(i.isnumeric()):
                break
            sec += i
        return sec

    def clean(self, str):
        st = str.find("[freezedetect")
        return str[st:]

    def stops_by_freezedetect(self, res):
        start = res.find("[freezedetect")
        list = res[start:].split("\r\n")
        for i in range(3):
            list.pop()
        
        stops = []
        stop = ""
        for i in list:
            
            parts = self.clean(i).split(" ")
            if i.find("freeze_start") != -1:
                str = parts[4]
                start = self.get_sec(str)
                #print("start: ", str)
            elif i.find("freeze_end") != -1:
                str = parts[4]
                end = self.get_sec(str)
                #print("end: ", str)
                stop = "{} {}".format(start, end)
                if (self.stop_sens(stop, self.sensitivity)):
                    stops.append(stop)
        return stops

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--directory', required=False, default='data')
    parser.add_argument('-O', '--output_vid', required=False, default='output.mov')
    parser.add_argument('-OG', '--output_gpx', required=False, default='output.gpx')
    parser.add_argument('-S', '--sensitivity', required=False, default=2)
    parser.add_argument('-N', '--noise', required=False, default=35)
    args = parser.parse_args()
    try:
        Process(dir=args.directory, out_vid=args.output_vid, out_gpx=args.output_gpx, sens=args.sensitivity, noise=args.noise).start()
    except Exception as e:
        print('[-] Directory may not be accessible, or: %s' % e)