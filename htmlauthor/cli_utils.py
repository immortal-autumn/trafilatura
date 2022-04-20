import requests, os, urllib3

from htmlauthor import extract


# Determine the input is a file path or a URL, return None if it is not for both.
def determine_file_or_url(path):
    try:
        r = requests.head(path, allow_redirects=True)
        if r.status_code == 200:
            return 'isURL'
    except BaseException:
        pass
    if os.path.exists(path):
        return 'isFile'
    return None


def process_url(url):
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    # print(resp.data)
    return extract(resp)


def process_file(path):
    return extract(open(path, 'rb').read())
