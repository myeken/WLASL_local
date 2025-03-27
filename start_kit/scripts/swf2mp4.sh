#!/bin/bash

echo "Start converting formats.."

src_path='raw_videos'
dst_path='raw_videos_mp4'

# Create the destination folder if it doesn't exist
mkdir -p ${dst_path}

# Find all video files in the source folder (including subfolders)
files=$(find ${src_path} -type f \( -iname "*.swf" -o -iname "*.mkv" -o -iname "*.webm" -o -iname "*.mp4" \))
total=$(echo "${files}" | wc -l)
i=0

# Process each file
echo "${files}" | while read -r src_file; do
    ((i=i+1))
    filename=$(basename -- "$src_file")
    extension="${filename##*.}"
    relative_path="${src_file#$src_path/}"  # Remove the src_path prefix
    dst_file="${dst_path}/${relative_path%.*}.mp4"  # Change extension to .mp4

    # Create the destination subfolder if it doesn't exist
    mkdir -p "$(dirname "${dst_file}")"

    # Skip if the file already exists
    if [ -f "${dst_file}" ]; then
        echo "${i}/${total}, ${dst_file} exists."
        continue
    fi

    echo "${i} / ${total}, ${filename}"

    # Convert non-mp4 files to mp4
    if [ "${extension}" != "mp4" ]; then
        ffmpeg -loglevel panic -i "${src_file}" -vf "pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2" "${dst_file}"
    else
        cp "${src_file}" "${dst_file}"
    fi
done

echo "Finish converting formats.."