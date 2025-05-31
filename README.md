## Program to convert (or extract and convert) audio track from a media file to 2 channel wav 44100Hz mono file
## Made to create Polyend Tracker compatible samples

### List of supported input extentions:  
*.mp3, .wav, .aac, .ogg, .flac, .aiff, .pcm, .mp4, .mkv, .flv, .avi, .webm, .mpeg, .mpg*

### Build:
`pyinstaller --onefile index.py --name to_wav_44100_mono`  

*Output will appear in the dist folder*

### Run:
Requires ffmpeg to be available in PATH
*Note: input files will be deleted*  

`./to_wav_44100_mono <folder_or_file_to_convert>`
