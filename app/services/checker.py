from typing import Optional
import time
import requests

def check_health(url:str, timeout:Optional[float]=10)->dict:
    """
    Check the health of URL
    Args
        url - The URL to health check
        timeout - in seconds (optional, defaults to 10)
    Response
        dict - containing the results
    """
    # record start time for response time calculation
    start_time = time.time()

    # Initialize the response dictionary
    result = {
        "url": url,
        "timeout_seconds": timeout,
        "status_code": None,
        "status": "unhealthy",
        "response_time_ms": None,
        "error": None,
    }
    try:
        response = requests.get(
            url=url,
            timeout=timeout,
            allow_redirects=True,
            verify=True
        )
        result['status_code'] = response.status_code
        result['status'] = "healthy" if 200 <= response.status_code < 400 else "unhealthy"
        response_time = (time.time() - start_time) * 1000 # Convert to milliseconds
        result['response_time_ms'] = response_time
    except requests.exceptions.Timeout:
        result['error'] = f"Request timedout in {timeout} seconds."
    except requests.exceptions.SSLError:
        result['error'] = "SSLError: SSL certificate verification failed."
    except requests.exceptions.ConnectionError as e:
        if "SSLError" in str(e):
            result['error'] = "SSLError: SSL certificate verification failed."
        elif "NameResolutionError" in str(e):
            result['error'] = "DNSError: Invalid domain/hostname"
        else:
            result['error'] = f"Connection Error: {str(e)}"
    except Exception as e:
        result['error'] = f"Unexpected Error: {str(e)}"

    return result
        
