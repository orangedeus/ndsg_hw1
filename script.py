import os, argparse, shutil, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-D', '--directory', required=True)
parser.add_argument('-M', '--method', required=False, nargs='?', const=True, default=False)
args = parser.parse_args()

dir = args.directory
method = args.method

vids = os.listdir(dir)

if method:
    for i in vids:
            proc_command = "python process2.py -V {} -O {} -S {}".format(dir + "/" + i, str(i.split('.')[0]) + ".gpx", str(i.split('.')[0]))
            try:
                res = subprocess.check_output(proc_command, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                res = e.output
else:
    for i in vids:
            proc_command = "python process1.py -V {} -O {} -S {}".format(dir + "/" + i, str(i.split('.')[0]) + ".gpx", str(i.split('.')[0]))
            try:
                res = subprocess.check_output(proc_command, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                res = e.output

print(res.decode('utf-8'))