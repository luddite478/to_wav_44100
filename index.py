import argparse
import os
import sys
from pathlib import Path
import subprocess as sp
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Limit of concurrent FFmpeg conversions
MAX_CONCURRENT_JOBS = 4  # Change this to control resource usage

# Supported media extensions
def validate_ext(path):
    extensions = ['.mp3', '.wav', '.aac', '.ogg', '.flac', '.aiff', '.pcm',
                  '.mp4', '.mkv', '.flv', '.avi', '.webm', '.mpeg', '.mpg']
    return path if Path(path).suffix.lower() in extensions else None

def listdir_fullpath(d):
    return [str(Path(d) / f) for f in os.listdir(d)]

def remove_basename_duplicates(input_files):
    if not input_files:
        return []

    input_files.sort()
    seen = set()
    result = []

    for f in input_files:
        base = Path(f).stem
        if base not in seen:
            seen.add(base)
            result.append(f)

    return result

def convert_to_wav_44100(file_path):
    file_path = Path(file_path)
    dir_path = file_path.parent
    file_basename = file_path.stem
    output_path = dir_path / f"{file_basename}.wav"

    temp_input_path = dir_path / f"input_{file_basename}{file_path.suffix}"

    try:
        shutil.move(str(file_path), str(temp_input_path))
    except Exception as e:
        print(f"Failed to rename {file_path} -> {temp_input_path}: {e}")
        return

    convert_cmd = [
        'ffmpeg',
        '-hide_banner',
        '-i', str(temp_input_path),
        '-vn',                         
        '-sample_rate', '44100',
        '-ar', '44100',
        '-ac', '1',                    
        '-filter:a', 'loudnorm',      
        '-y', str(output_path)
    ]

    try:
        result = sp.run(convert_cmd, stderr=sp.PIPE, stdout=sp.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error converting {file_path}")
            print(result.stderr)
        else:
            print(f"Finished processing {output_path}")
    finally:
        if temp_input_path.exists():
            try:
                temp_input_path.unlink()
            except Exception as e:
                print(f"Failed to delete temporary file {temp_input_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert media files to WAV 44.1kHz mono")
    parser.add_argument('Path', metavar='path', type=str, help='File or folder path')
    args = parser.parse_args()

    input_path = Path(args.Path).expanduser().resolve()

    if not input_path.exists():
        print('The path specified does not exist')
        sys.exit(1)

    files_to_process = []

    if input_path.is_file():
        files_to_process.append(str(input_path))
    else:
        files_to_process = listdir_fullpath(str(input_path))

    files_to_process = remove_basename_duplicates(files_to_process)
    files_to_process = [f for f in files_to_process if Path(f).is_file() and validate_ext(f)]

    if not files_to_process:
        print("No valid media files to process.")
        return

    print(f"Processing {len(files_to_process)} files with up to {MAX_CONCURRENT_JOBS} concurrent conversions.")

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS) as executor:
        futures = [executor.submit(convert_to_wav_44100, f) for f in files_to_process]
        for future in as_completed(futures):
            future.result()  # Raise any exceptions

if __name__ == '__main__':
    main()
