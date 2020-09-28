# NDSG HOMEWORK

Team 1
* DP2340 GPS track extraction (exiftool) (done)
* Auto-detect stopped segments (Using embedded speed, done)
* Splice video using data generated from previous image (ffmpeg) (WIP)
## Reqs and Dependencies

* Exiftool
* FFMPEG-Python

## Instructions

* Run `python process.py -V <video_directory> -O <gpx_output_file>`. An `exiftool.exe` must be in the same directory. (Available [here](https://exiftool.org/))