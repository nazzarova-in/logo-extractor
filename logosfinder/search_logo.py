import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import  urljoin


def find_logo_clearbit(website):
    try:
        parsed_website = urlparse(website)
        domain = parsed_website.netloc or parsed_website.path

        if domain.startswith("www."):
            domain = domain[4:]

        logo_url = f"https://logo.clearbit.com/{domain}"

        response = requests.head(logo_url, timeout=20)
        if response.status_code == 200:
            return logo_url
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def find_logo_from_html(website):
  try:
    if not website.startswith("http"):
      website = "https://" + website
    response = requests.get(website, timeout = 40)
    soup = BeautifulSoup(response.text, "html.parser")

    icon_tags = soup.find_all("link", rel=lambda value: value and any(
      r in value.lower() for r in ["icon", "shortcut", "apple-touch-icon"]))

    for tag in icon_tags:
      href = tag.get("href")
      if href:
        return urljoin(website, href)

    parsed = urlparse(website)
    fallback_logo = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    response = requests.head(fallback_logo, timeout=10)
    if response.status_code == 200:
      return fallback_logo

    return None

  except Exception as e:
    print(f"Error: {e}")
    return None
