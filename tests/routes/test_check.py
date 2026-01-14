import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_get_health():
    test_urls = [{
        "name": "Valid URL - google.com",
        "data": {
            "url": "https://www.google.com",
            "timeout": 20,
        },
    },{
        "name": "Empty URL - ",
        "data": {
            "url": "",
            "timeout": 20,
        }
    },{
        "name": "Invalid URL scheme - hyyf://",
        "data": {
            "url": "hyyf://www.google.com",
            "timeout": 20,
        },
    },{
        "name": "Invalid timeout",
        "data": {
            "url": "https://www.google.com",
            "timeout": "yyj",
        },
    },{
        "name": "Invalid timeout - beyond the permitted limit",
        "data": {
            "url": "https://www.google.com",
            "timeout": 50,
        },
    }]

    for url in test_urls:
        print(f"Testing for url-> {url['name']}")
        result = requests.post(
            url=f"{BASE_URL}/check",
            json=url["data"]
        )
        print(f"Result -> {json.dumps(result.json(), indent=2)}")
if __name__ == '__main__':
    test_get_health()
