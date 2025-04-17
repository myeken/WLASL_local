import os
import json
import time
import sys
import urllib.request
import random
import logging
import subprocess
from youtubesearchpython import VideosSearch

# For scraping ASL websites
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Logging configuration
logging.basicConfig(
    filename='download_{}.log'.format(int(time.time())),
    filemode='w',
    level=logging.DEBUG
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Set this to "yt-dlp" or "youtube-dl" depending on your installation.
youtube_downloader = "yt-dlp"

# Define which ASL signs to target and the maximum allowed duration (in seconds)
TARGET_SIGNS = {"book", "hello", "thank you", "computer", "dog"}
MAX_DURATION = 15  # Updated maximum duration to 15 seconds

def request_video(url, referer=''):
    user_agent = ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; '
                  'rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7')
    headers = {'User-Agent': user_agent}
    if referer:
        headers['Referer'] = referer
    req = urllib.request.Request(url, None, headers)
    logging.info(f'Requesting URL: {url}')
    response = urllib.request.urlopen(req)
    data = response.read()
    return data

def save_video(data, saveto):
    with open(saveto, 'wb+') as f:
        f.write(data)
    time.sleep(random.uniform(0.5, 1.5))

def get_duration(file_path):
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        logging.error(f"Error getting duration for {file_path}: {e}")
        return float('inf')

def get_youtube_duration(url):
    try:
        cmd = [youtube_downloader, "--get-duration", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        duration_str = result.stdout.strip()  # Format: "mm:ss" or "hh:mm:ss"
        if not duration_str:
            return float('inf')
        parts = duration_str.split(":")
        seconds = 0
        for part in parts:
            seconds = seconds * 60 + float(part)
        return seconds
    except Exception as e:
        logging.error(f"Failed to get duration for {url}: {e}")
        return float('inf')

def download_youtube(url, dirname, video_id):
    # Not used directly—YouTube downloads are handled in download_yt_videos.
    raise NotImplementedError("Use download_yt_videos for YouTube links.")

def download_aslpro(url, dirname, video_id):
    saveto = os.path.join(dirname, f'{video_id}.swf')
    if os.path.exists(saveto):
        logging.info(f'{video_id} already exists at {saveto}')
        return saveto
    try:
        data = request_video(url, referer='http://www.aslpro.com/cgi-bin/aslpro/aslpro.cgi')
        save_video(data, saveto)
        return saveto
    except Exception as e:
        logging.error(f"Error downloading ASLPro video {video_id}: {e}")
        return None

def download_others(url, dirname, video_id):
    saveto = os.path.join(dirname, f'{video_id}.mp4')
    if os.path.exists(saveto):
        logging.info(f'{video_id} already exists at {saveto}')
        return saveto
    try:
        data = request_video(url)
        save_video(data, saveto)
        return saveto
    except Exception as e:
        logging.error(f"Error downloading video {video_id}: {e}")
        return None

def download_signingsavvy(url, dirname, video_id):
    try:
        html = request_video(url)
        soup = BeautifulSoup(html, 'html.parser')
        video_tag = soup.find('video')
        video_src = None
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and source_tag.has_attr('src'):
                video_src = source_tag['src']
            elif video_tag.has_attr('src'):
                video_src = video_tag['src']
        if not video_src:
            for a in soup.find_all('a', href=True):
                if a['href'].endswith('.mp4'):
                    video_src = a['href']
                    break
        if not video_src:
            logging.error(f"No video source found on Signingsavvy for video {video_id}")
            return None
        if not video_src.startswith('http'):
            video_src = urljoin(url, video_src)
        saveto = os.path.join(dirname, f'{video_id}.mp4')
        if os.path.exists(saveto):
            logging.info(f'{video_id} already exists at {saveto}')
            return saveto
        data = request_video(video_src)
        save_video(data, saveto)
        return saveto
    except Exception as e:
        logging.error(f"Error downloading Signingsavvy video {video_id}: {e}")
        return None

def download_handspeak(url, dirname, video_id):
    try:
        html = request_video(url)
        soup = BeautifulSoup(html, 'html.parser')
        video_tag = soup.find('video')
        video_src = None
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and source_tag.has_attr('src'):
                video_src = source_tag['src']
            elif video_tag.has_attr('src'):
                video_src = video_tag['src']
        if not video_src:
            for a in soup.find_all('a', href=True):
                if a['href'].endswith('.mp4'):
                    video_src = a['href']
                    break
        if not video_src:
            logging.error(f"No video source found on Handspeak for video {video_id}")
            return None
        if not video_src.startswith('http'):
            video_src = urljoin(url, video_src)
        saveto = os.path.join(dirname, f'{video_id}.mp4')
        if os.path.exists(saveto):
            logging.info(f'{video_id} already exists at {saveto}')
            return saveto
        data = request_video(video_src)
        save_video(data, saveto)
        return saveto
    except Exception as e:
        logging.error(f"Error downloading Handspeak video {video_id}: {e}")
        return None

def download_signasl(url, dirname, video_id):
    try:
        html = request_video(url)
        soup = BeautifulSoup(html, 'html.parser')
        video_tag = soup.find('video')
        video_src = None
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and source_tag.has_attr('src'):
                video_src = source_tag['src']
            elif video_tag.has_attr('src'):
                video_src = video_tag['src']
        if not video_src:
            for a in soup.find_all('a', href=True):
                if a['href'].endswith('.mp4'):
                    video_src = a['href']
                    break
        if not video_src:
            logging.error(f"No video source found on SignASL for video {video_id}")
            return None
        if not video_src.startswith('http'):
            video_src = urljoin(url, video_src)
        saveto = os.path.join(dirname, f'{video_id}.mp4')
        if os.path.exists(saveto):
            logging.info(f'{video_id} already exists at {saveto}')
            return saveto
        data = request_video(video_src)
        save_video(data, saveto)
        return saveto
    except Exception as e:
        logging.error(f"Error downloading SignASL video {video_id}: {e}")
        return None

def select_download_method(url):
    if 'aslpro' in url:
        return download_aslpro
    elif 'youtube' in url or 'youtu.be' in url:
        return download_youtube  # Handled separately in download_yt_videos
    elif 'signingsavvy.com' in url:
        return download_signingsavvy
    elif 'handspeak.com' in url:
        return download_handspeak
    elif 'signasl.org' in url:
        return download_signasl
    else:
        return download_others

def download_nonyt_videos(indexfile, saveto='raw_videos'):
    content = json.load(open(indexfile))
    for entry in content:
        gloss = entry['gloss'].lower()
        if gloss not in TARGET_SIGNS:
            continue
        target_dir = os.path.join(saveto, gloss)
        os.makedirs(target_dir, exist_ok=True)
        instances = entry['instances']
        for inst in instances:
            video_url = inst['url']
            video_id = inst['video_id']
            logging.info(f'Processing {gloss} video: {video_id}')
            download_method = select_download_method(video_url)
            if download_method == download_youtube:
                logging.warning(f'Skipping YouTube video {video_id} in non-YouTube downloader.')
                continue
            try:
                file_path = download_method(video_url, target_dir, video_id)
                # Only keep if file exists and its duration is within limit
                if file_path and get_duration(file_path) <= MAX_DURATION:
                    logging.info(f"Accepted video {video_id}.")
                else:
                    if file_path:
                        logging.info(f"Video {video_id} exceeds {MAX_DURATION}s; removing.")
                        os.remove(file_path)
            except Exception as e:
                logging.error(f'Failed downloading video {video_id}: {e}')

def check_youtube_dl_version():
    ver = os.popen(f'{youtube_downloader} --version').read().strip()
    assert ver, f"{youtube_downloader} not found in PATH. Verify installation."
    logging.info(f"{youtube_downloader} version: {ver}")

def download_yt_videos(indexfile, saveto='raw_videos'):
    content = json.load(open(indexfile))
    for entry in content:
        gloss = entry['gloss'].lower()
        if gloss not in TARGET_SIGNS:
            continue
        target_dir = os.path.join(saveto, gloss)
        os.makedirs(target_dir, exist_ok=True)
        instances = entry['instances']
        for inst in instances:
            video_url = inst['url']
            video_id = inst['video_id']
            if 'youtube' not in video_url and 'youtu.be' not in video_url:
                continue
            duration = get_youtube_duration(video_url)
            if duration > MAX_DURATION:
                logging.info(f"Skipping YouTube video {video_url} (duration {duration:.2f}s > {MAX_DURATION}s).")
                continue
            yt_filename = os.path.join(target_dir, video_url[-11:] + '.mp4')
            if os.path.exists(yt_filename):
                logging.info(f'YouTube video {video_url} already exists in {target_dir}.')
                continue
            cmd = f'{youtube_downloader} "{video_url}" -o "{target_dir}{os.path.sep}%(id)s.%(ext)s"'
            rv = os.system(cmd)
            if rv == 0:
                logging.info(f'Downloaded YouTube video {video_url} into {target_dir}')
                if os.path.exists(yt_filename) and get_duration(yt_filename) <= MAX_DURATION:
                    logging.info(f"Accepted YouTube video {video_id}.")
                elif os.path.exists(yt_filename):
                    logging.info(f"YouTube video {video_id} exceeds {MAX_DURATION}s; removing.")
                    os.remove(yt_filename)
            else:
                logging.error(f'Failed downloading YouTube video {video_url} into {target_dir}')
            time.sleep(random.uniform(1.0, 1.5))

def download_extra_videos(sign, saveto='raw_videos', limit_per_query=15):
    queries = [
        f"ASL {sign} sign",
        f"ASL {sign}",
        f"{sign} ASL gesture",
        f"American Sign Language {sign}",
        f"short {sign} ASL clip"
    ]
    target_dir = os.path.join(saveto, sign.lower())
    os.makedirs(target_dir, exist_ok=True)
    downloaded_ids = set()
    logging.info(f"Starting extra YouTube search for sign: {sign}")
    for query in queries:
        logging.info(f"Searching with query: {query}")
        search = VideosSearch(query, limit=limit_per_query)
        results = search.result().get('result', [])
        for result in results:
            video_url = result.get('link')
            video_id = result.get('id', video_url[-11:])
            if video_id in downloaded_ids:
                continue
            duration = get_youtube_duration(video_url)
            if duration > MAX_DURATION:
                logging.info(f"Skipping video {video_url} (duration {duration:.2f}s > {MAX_DURATION}s).")
                continue
            yt_filename = os.path.join(target_dir, f"{video_id}.mp4")
            if os.path.exists(yt_filename):
                logging.info(f'Video {video_url} already exists in {target_dir}.')
                downloaded_ids.add(video_id)
                continue
            cmd = f'{youtube_downloader} "{video_url}" -o "{target_dir}{os.path.sep}%(id)s.%(ext)s"'
            rv = os.system(cmd)
            if rv == 0:
                logging.info(f'Downloaded extra video {video_url} into {target_dir}')
                downloaded_ids.add(video_id)
                if os.path.exists(yt_filename) and get_duration(yt_filename) <= MAX_DURATION:
                    logging.info(f"Accepted extra video {video_id}.")
                elif os.path.exists(yt_filename):
                    logging.info(f"Extra video {video_id} exceeds {MAX_DURATION}s; removing.")
                    os.remove(yt_filename)
            else:
                logging.error(f'Failed downloading extra video {video_url} into {target_dir}')
            time.sleep(random.uniform(1.0, 1.5))

# --- New functions for additional website scraping ---

def scrape_signingsavvy_search(sign, target_dir, limit=10):
    search_url = f"https://www.signingsavvy.com/search.php?query={sign}"
    logging.info(f"Scraping Signingsavvy for sign '{sign}' using {search_url}")
    try:
        html = request_video(search_url)
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            if '/sign/' in a['href']:
                link = urljoin(search_url, a['href'])
                if link not in links:
                    links.append(link)
        links = links[:limit]
        for link in links:
            video_id = link.rstrip('/').split('/')[-1]
            download_signingsavvy(link, target_dir, video_id)
            time.sleep(random.uniform(1.0, 1.5))
    except Exception as e:
        logging.error(f"Error scraping Signingsavvy for sign {sign}: {e}")

def scrape_handspeak_search(sign, target_dir):
    url = f"https://www.handspeak.com/word/{sign}"
    logging.info(f"Scraping Handspeak for sign '{sign}' using {url}")
    try:
        download_handspeak(url, target_dir, sign + "_handspeak")
    except Exception as e:
        logging.error(f"Error scraping Handspeak for sign {sign}: {e}")

def scrape_signasl_search(sign, target_dir):
    url = f"https://www.signasl.org/sign/{sign}"
    logging.info(f"Scraping SignASL for sign '{sign}' using {url}")
    try:
        download_signasl(url, target_dir, sign + "_signasl")
    except Exception as e:
        logging.error(f"Error scraping SignASL for sign {sign}: {e}")

def ensure_minimum_videos(sign, min_count=10, saveto='raw_videos'):
    target_dir = os.path.join(saveto, sign.lower())
    os.makedirs(target_dir, exist_ok=True)
    current_files = [f for f in os.listdir(target_dir) if f.endswith('.mp4') or f.endswith('.swf')]
    count = len(current_files)
    logging.info(f"Sign '{sign}': {count} videos currently available.")
    if count >= min_count:
        return
    logging.info(f"Sign '{sign}': Only {count} videos found; attempting additional scraping.")
    scrape_signingsavvy_search(sign, target_dir, limit=10)
    current_files = [f for f in os.listdir(target_dir) if f.endswith('.mp4') or f.endswith('.swf')]
    count = len(current_files)
    if count >= min_count:
        logging.info(f"Sign '{sign}': Now have {count} videos after Signingsavvy.")
        return
    scrape_handspeak_search(sign, target_dir)
    current_files = [f for f in os.listdir(target_dir) if f.endswith('.mp4') or f.endswith('.swf')]
    count = len(current_files)
    if count >= min_count:
        logging.info(f"Sign '{sign}': Now have {count} videos after Handspeak.")
        return
    scrape_signasl_search(sign, target_dir)
    current_files = [f for f in os.listdir(target_dir) if f.endswith('.mp4') or f.endswith('.swf')]
    count = len(current_files)
    logging.info(f"Sign '{sign}': Final count is {count} videos.")

if __name__ == '__main__':
    index_file = 'WLASL_v0.3.json'
    raw_videos_dir = 'raw_videos'
    
    logging.info('Downloading non-YouTube videos from JSON.')
    download_nonyt_videos(index_file, saveto=raw_videos_dir)
    
    check_youtube_dl_version()
    
    logging.info('Downloading YouTube videos from JSON.')
    download_yt_videos(index_file, saveto=raw_videos_dir)
    
    logging.info('Downloading extra YouTube videos using multiple queries.')
    for sign in TARGET_SIGNS:
        download_extra_videos(sign, saveto=raw_videos_dir, limit_per_query=15)
    
    # Ensure minimum of 10 videos per sign by scraping additional sources if necessary.
    for sign in TARGET_SIGNS:
        ensure_minimum_videos(sign, min_count=12, saveto=raw_videos_dir)
    
    logging.info('All downloads complete. Run preprocess.py to convert non-MP4 files if needed.')