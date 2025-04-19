import os
import json
import cv2
import shutil
import subprocess

def convert_video(input_file, output_file):
    """
    Convert a video file to MP4 using ffmpeg.
    """
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-movflags', '+faststart',
        '-y',
        output_file
    ]
    subprocess.run(cmd, check=True)

def convert_everything_to_mp4():
    """
    Convert all non-MP4 files in the 'raw_videos' directory to MP4.
    MP4 files are simply copied to 'raw_videos_mp4'.
    """
    raw_dir = 'raw_videos'
    output_dir = 'raw_videos_mp4'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            input_path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            dest_path = os.path.join(output_dir, name + ".mp4")
            if ext.lower() == ".mp4":
                if not os.path.exists(dest_path):
                    shutil.copyfile(input_path, dest_path)
                    print(f"Copied {input_path} to {dest_path}")
            else:
                if not os.path.exists(dest_path):
                    try:
                        convert_video(input_path, dest_path)
                        print(f"Converted {input_path} to {dest_path}")
                    except Exception as e:
                        print(f"Failed to convert {input_path}: {e}")

def video_to_frames(video_path, size=None):
    """
    Convert a video to a list of frames.
    video_path -> str, path to video.
    size -> (int, int), width, height.
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if ret:
            if size:
                frame = cv2.resize(frame, size)
            frames.append(frame)
        else:
            break
    cap.release()
    return frames

def convert_frames_to_video(frame_array, path_out, size, fps=25):
    out = cv2.VideoWriter(path_out, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
    for frame in frame_array:
        out.write(frame)
    out.release()

def extract_frame_as_video(src_video_path, start_frame, end_frame):
    frames = video_to_frames(src_video_path)
    return frames[start_frame: end_frame+1]

def extract_all_yt_instances(content):
    """
    Extract instances for YouTube videos and create video segments.
    For each instance, if frame_start and frame_end are provided,
    a segment is extracted from the full video.
    """
    cnt = 1
    if not os.path.exists('videos'):
        os.mkdir('videos')
    for entry in content:
        instances = entry['instances']
        for inst in instances:
            url = inst['url']
            video_id = inst['video_id']
            if 'youtube' in url or 'youtu.be' in url:
                cnt += 1
                yt_identifier = url[-11:]
                src_video_path = os.path.join('raw_videos_mp4', yt_identifier + '.mp4')
                dst_video_path = os.path.join('videos', video_id + '.mp4')
                if not os.path.exists(src_video_path):
                    continue
                if os.path.exists(dst_video_path):
                    print(f"{dst_video_path} exists.")
                    continue
                # Adjusting for JSON file indexing starting at 1.
                start_frame = inst.get('frame_start', 1) - 1
                end_frame = inst.get('frame_end', 0) - 1
                if end_frame <= 0:
                    shutil.copyfile(src_video_path, dst_video_path)
                    continue
                selected_frames = extract_frame_as_video(src_video_path, start_frame, end_frame)
                # OpenCV reads images as (height, width, channels); VideoWriter needs (width, height)
                size = selected_frames[0].shape[:2][::-1]
                convert_frames_to_video(selected_frames, dst_video_path, size)
                print(cnt, dst_video_path)
            else:
                cnt += 1
                src_video_path = os.path.join('raw_videos_mp4', video_id + '.mp4')
                dst_video_path = os.path.join('videos', video_id + '.mp4')
                if os.path.exists(dst_video_path):
                    print(f"{dst_video_path} exists.")
                    continue
                if not os.path.exists(src_video_path):
                    continue
                print(cnt, dst_video_path)
                shutil.copyfile(src_video_path, dst_video_path)

def main():
    # 1. Convert non-MP4 videos in raw_videos to MP4 in raw_videos_mp4.
    convert_everything_to_mp4()
    # 2. Load JSON metadata and extract YouTube video segments.
    content = json.load(open('WLASL_v0.3.json'))
    extract_all_yt_instances(content)

if __name__ == "__main__":
    main()