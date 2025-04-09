import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check_broken_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = [a.get('href') for a in soup.find_all('a', href=True)]
    broken_links = []

    for link in links:
        full_link = urljoin(url, link)  # Convert relative URLs to absolute
        try:
            res = requests.head(full_link, allow_redirects=True)
            if res.status_code >= 400:
                broken_links.append(full_link)
        except requests.exceptions.RequestException:
            broken_links.append(full_link)

    return broken_links

url = "https://www.glftsh.org" \
""  # Replace with your website URL
print("Broken Links:", check_broken_links(url))
