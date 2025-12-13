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

@register.filter
def cl_opt(url, size='medium'):
    """
    Optimize Cloudinary images with proper transformations
    Usage: 
        {{ image.url|cl_opt }}           # Default medium size
        {{ image.url|cl_opt:"small" }}   # Small size
        {{ image.url|cl_opt:"large" }}   # Large size
    """
    try:
        # Only modify Cloudinary URLs
        if not url or "res.cloudinary.com" not in url:
            return url

        # Define size presets
        size_presets = {
            'small': 'c_fill,w_200,h_200,q_auto:low,f_auto',
            'medium': 'c_fill,w_400,h_400,q_auto,f_auto',
            'large': 'c_fill,w_800,h_800,q_auto,f_auto',
            'thumb': 'c_thumb,w_100,h_100,q_auto:low,f_auto',
            # 'carousel': 'c_scale,w_1200,q_auto:eco,f_auto',  # Optimized for carousels
        }
        
        # Get transformation string
        transformation = size_presets.get(size, size_presets['medium'])
        
        # Split URL at '/upload/'
        if "/upload/" in url:
            parts = url.split("/upload/", 1)
            if len(parts) == 2:
                base, path = parts
                # Check if transformations already exist
                if not any(t in path for t in ['c_fill', 'w_', 'q_auto']):
                    return f"{base}/upload/{transformation}/{path}"
        
        return url

    except Exception as e:
        # Return original URL on any error
        return url


@register.filter
def cl_responsive(url):
    """
    Create responsive Cloudinary image with automatic format and quality
    Best for images that need to adapt to different screen sizes
    """
    try:
        if not url or "res.cloudinary.com" not in str(url):
            return url

        url_str = str(url)
        
        if "/upload/" in url_str:
            parts = url_str.split("/upload/", 1)
            if len(parts) == 2:
                base, path = parts
                # Simpler responsive transformation that works better
                transformation = 'c_scale,w_1200,q_auto:eco,f_auto'
                return f"{base}/upload/{transformation}/{path}"
        
        return url_str

    except Exception as e:
        print(f"Cloudinary filter error: {e}")
        return str(url)


@register.filter
def cl_card(url):
    """
    Optimize for card/grid images - square crop with good quality
    Perfect for artist images, album covers, etc.
    """
    try:
        if not url or "res.cloudinary.com" not in url:
            return url

        if "/upload/" in url:
            parts = url.split("/upload/", 1)
            if len(parts) == 2:
                base, path = parts
                # Card-optimized: square crop, auto format/quality
                transformation = 'c_fill,w_300,h_300,g_auto,q_auto:good,f_auto'
                return f"{base}/upload/{transformation}/{path}"
        
        return url

    except Exception:
        return url


@register.filter
def cl_album(url):
    """
    Optimize for larger album art images
    """
    try:
        if not url or "res.cloudinary.com" not in url:
            return url

        if "/upload/" in url:
            parts = url.split("/upload/", 1)
            if len(parts) == 2:
                base, path = parts
                # Album art: larger size, maintain aspect ratio
                transformation = 'c_scale,w_600,q_auto:good,f_auto'
                return f"{base}/upload/{transformation}/{path}"
        
        return url

    except Exception:
        return url
    
@register.filter
def cl_video_thumb(url):
    """
    Cloudinary optimization for 16:9 video thumbnails.
    Keeps aspect ratio, avoids cropping.
    """
    try:
        if not url or "res.cloudinary.com" not in url:
            return url

        if "/upload/" in url:
            base, path = url.split("/upload/", 1)
            # c_fill + aspect ratio safe (no cropping outside bounds)
            transformation = "c_fill,ar_16:9,w_400,q_auto,f_auto"
            return f"{base}/upload/{transformation}/{path}"

        return url

    except:
        return url
