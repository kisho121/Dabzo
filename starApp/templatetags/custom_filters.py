from django import template
import re

register = template.Library()

@register.filter
def extract_youtube_id(url):
    """
    Extracts the YouTube video ID from a URL.
    Handles both youtu.be and youtube.com URLs.
    """
    if "youtu.be" in url:
        # Get ID for https://youtu.be/VIDEO_ID
        return url.split("/")[-1]  # Last part after slash is the ID
    elif "youtube.com" in url:
        # Match ID for https://www.youtube.com/watch?v=VIDEO_ID
        match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)  # Return the first capture group
    return None