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
* To process a concatenated video and create a concatenated GPX file, use `python process.py [-D <folder> -O <output_concatenated_vid> -OG <output_concatenated_gpx_file>]`.
    * Creates several folders for each method (stop, speed currently) and places the spliced videos in them.