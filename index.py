import argparse
import os
import sys
from pathlib import Path
import threading
import subprocess as sp
import itertools

def validate_ext(path):
    extentions = ['.mp3','.wav','.aac','.ogg','.flac','.aiff','.pcm','.mp4','.mkv','.flv','.avi','.webm','.mpeg','.mpg']
    _, file_ext = os.path.splitext(path)

    if any(ext in file_ext for ext in extentions):
        return path
    else:
        return None

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def remove_basename_duplicates(input_files):
    if len(input_files) == 0:
        return []
        
    # find non duplicate dir + basenames
    input_files.sort()
    duplicate_filtered = []
    for k, _ in itertools.groupby(input_files, lambda f: os.path.splitext(f)[0]):
        duplicate_filtered.append(k)

    # make a list of unique full file paths 
    # pick first found basename match between input and duplicated-filtered lists
    # ignore other basename matches  
    duplicate_filtered_full_path = []

    for filtered_file_p in duplicate_filtered:
        for input_file_p in input_files:

            basename1 = os.path.basename(filtered_file_p)
            basename2 = os.path.splitext(os.path.basename(input_file_p))[0]
 
            if basename1 == basename2:
                duplicate_filtered_full_path.append(input_file_p)
                break
        
    return duplicate_filtered_full_path

def convert_to_wav_44100(file_path):

    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_basename = os.path.splitext(file_name)[0]
    output_path = os.path.join(dir_path, file_basename + '.wav')

    # rename input to prevent overwrite-inplace-ffmpeg erros
    input_file_path = os.path.join(dir_path, 'input' + file_basename + '.wav')
    os.rename(file_path,  input_file_path)

    convert_cmd = [
        'ffmpeg', 
        '-hide_banner', 
      #  '-loglevel', 'error',
        '-ac', '2', 
        '-i', input_file_path, 
        '-vn',
        '-sample_rate', '44100',
        '-ar', '44100',
        '-filter:a', 'loudnorm',
        '-y', output_path
    ]

    del_input_file_cmd = [
        '&', 
        'DEL', 
        '/F', 
        input_file_path
    ]


    cmd = convert_cmd + del_input_file_cmd

    ffmpeg = sp.Popen(cmd, stderr=sp.PIPE, shell=True)
    _, stderr = ffmpeg.communicate()

    if ffmpeg.returncode != 0:
        print('Error converting ', file_path)
        print(stderr)
    else:
        print('Finished processing ', output_path)




parser = argparse.ArgumentParser()

parser.add_argument('Path',
                       metavar='path',
                       type=str,
                       help='File path or folder path')

args = parser.parse_args()

input_path = args.Path

isdir = os.path.isdir(input_path)
isfile = os.path.isfile(input_path)

if not isdir and not isfile:
    print('The path specified does not exist')
    sys.exit()

if not os.path.isabs(input_path):
    print('Specify absolute path')
    sys.exit()

files_to_process = []

if isfile:
    files_to_process.append(input_path)
else:  
    files_to_process = listdir_fullpath(input_path)


files_to_process = remove_basename_duplicates(files_to_process)

for f_path in files_to_process:
    p = Path(f_path)

    if not p.is_file():
        print(f_path, 'is not a file, skipping')
        continue
        
    if not validate_ext(str((p))):
        print(f_path, 'is not a media file, skipping')
        continue

    t = threading.Thread(target=convert_to_wav_44100, args=(f_path,))   
    t.start()
