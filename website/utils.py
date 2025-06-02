from urllib.parse import urlparse

def tld_extractor(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    tld = domain.split('.')[-1]
    return '.' + tld
