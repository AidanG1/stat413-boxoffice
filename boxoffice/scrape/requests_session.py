import requests


HEADERS = {
    # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    "User-Agent": "Statistical Machine Learning Box Office Scraper, gerber@rice.edu"
}


s = requests.Session()

s.headers.update(HEADERS)
