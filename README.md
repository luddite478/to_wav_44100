## Program to convert (or extract and convert) audio track from a media file to 2 channel wav 44100Hz file

### List of supported input extentions:  
*.mp3, .wav, .aac, .ogg, .flac, .aiff, .pcm, .mp4, .mkv, .flv, .avi, .webm, .mpeg, .mpg*

### Build:
`pyinstaller --onefile index.py --name to_wav_44100`  

*Output will appear in the dist folder*

### Run:
*Note: input files will be deleted*  

`./to_wav_44100 <folder_or_file_to_convert>`
