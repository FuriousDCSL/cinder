# cinder

This program is designed to convert stepmania .sm files to Beat Saber json
files.

It does this by turning left and down arrows to left hand beats and right and
up arrows to right hand beats.

It has preliminary support for variable BPM. If there is more then one BPM
for the song the output BPM will be set to 200 and the beats will be adjusted
compensate. This makes the files unable to be edited by the current editors.

If there is only one BPM in the song it will be set normally and the file will
be normally editable

This program will insert the offset in the sm file, so the note may be off in 
another editor. You will have to fix that by editing the sound file and sm
file to sync 0 offset.

To use the program, install python version 3.6.5 (other version 3 will
  probably work).



 also if you want an image for the Songs
make a 256x256 png and put it in the folder with the name cover.png.

(edit difficulties may crash the program at this point untested)
