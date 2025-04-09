import requests
from bs4 import BeautifulSoup

def get_meta_tags(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string if soup.title else "No Title Found"
    description = soup.find("meta", attrs={"name": "description"})
    description = description["content"] if description else "No Description Found"
    h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]

    return {
        "Title": title,
        "Meta Description": description,
        "H1 Tags": h1_tags
    }

url = "https://www.glftsh.org"
print(get_meta_tags(url))
