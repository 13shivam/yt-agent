from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        return parsed.path.lstrip('/')
    elif 'youtube.com' in parsed.netloc:
        if 'shorts' in parsed.path:
            return parsed.path.split('/')[2]
        return parse_qs(parsed.query).get('v', [None])[0]
    return None

