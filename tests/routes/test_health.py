import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    print("Testing service health endpoint")
    result = requests.get(f"{BASE_URL}/health")
    print(f"Result -> {json.dumps(result.json(), indent=2)}")

if __name__ == '__main__':
    test_health()
