# NDSG HOMEWORK

Team 1
* DP2340 GPS track extraction (exiftool) (done)
* Auto-detect stopped segments (done)
* Splice video using data generated from previous section (done)
## Reqs and Dependencies

The following should be in your path.

* [Exiftool](https://exiftool.org/)
* [FFMPEG](https://ffmpeg.org/)

## Instructions

* Run `python process1.py -V <video> [-O <gpx_output_file> -S <splice_naming_scheme>]` to process using stops by speed.
* Run `python process2.py -V <video> [-O <gpx_output_file> -S <splice_naming_scheme>]` to process using stops by readings.
* To process videos in a folder use `python script.py [-M] -D <folder>`.
    * Use `-M` to use stops by readings to process the videos. Uses stops by speed by default.