from typing import Tuple
from urllib.parse import urlparse

def validate_url(url:str)->Tuple[bool, str|None]:
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "URL must start with http:// or https"
        if not parsed.scheme in ['http', 'https']:
            return False, "URL scheme must be http or https"
        if not parsed.netloc:
            return False, "URL must include a valid domain"
            
    except Exception as e:
        return False, f"Invalid URL format : {str(e)}"

    return True, None

def validate_timeout(timeout:[int|float])->Tuple[bool, str|None]:
    if not isinstance(timeout, (int, float)):
        return False, "Invalid timeout format"

    if timeout < 0 or timeout > 30:
        return False, "Timeout must be between 0 and 30 seconds"

    return True, None  
