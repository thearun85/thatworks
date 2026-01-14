from app.services import check_health
import json

def test_core_checker():
    print("Starting Core check health tests")
    test_urls = [{
        'name': 'Valid https URL - google.com',
        'url': 'https://www.google.com'
    },
    {
        'name': 'Valid https URL - github.com',
        'url': 'https://www.github.com'
    },
    {
        'name': 'Valid http URL - example.com',
        'url': 'http://example.com'
    },
    {
        'name': 'Invalid URL - SSL Error',
        'url': 'https://wrong.host.badssl.com'
    },
    {
        'name': 'Invalid URL - Non existent domain',
        'url': 'https://this-domain-does-not-exist'
    },
    {
        'name': 'Invalid URL - Non existent domain',
        'url': 'https://arunraghunath.io'
    }]
    for url in test_urls:
        print(f"Testing {url['name']}")
        result = check_health(url['url'])
        print(f"Result -> {json.dumps(result, indent=2)}")

if __name__ == '__main__':
    test_core_checker()
