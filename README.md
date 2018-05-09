# cinder
NOTE: SCRIPT IS CURRENTLY BROKEN, WILL FIX TONIGHT I HOPE

This program is designed to convert stepmania .sm files to Beat Saber json
files.

It does this by turning left and down arrows to left hand beats and right and
up arrows to right hand beats.

It has preliminary support for variable BPM. If there is more then one BPM
for the song the output BPM will be set to 200 and the beats will be adjusted
compensate. This makes the files unable to be edited by the current editors.

To use the program, install python version 3.6.5 (other version 3 will
  probably work).

drop the .sm file in the folder with SM2BS.py. Open a cmd prompt and

py SM2BS.py <filename>

This will output info.json and a json for each difficulty. Make a folder in
your CustomSongs Folder for the new song and drop the .json files in there
as well as the song file (.ogg). also if you want an image for the Songs
make a 256x256 png and put it in the folder with the name cover.png.

(edit difficulties may crash the program at this point untested)
