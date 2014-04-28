import json
try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection

DEF_HEADERS = {'User-Agent': 'TrueBlue bluealliance Scraper',
        'X-TBA-App-Id': 'frc2994:scouting:v2'}

BLUEALLIANCE_DOMAIN = 'www.thebluealliance.com'
BASEPATH = '/api/v2'

def tba_download_file(path):
    conn = HTTPConnection(BLUEALLIANCE_DOMAIN)
    conn.request('GET', BASEPATH + path, headers=DEF_HEADERS)

    r = conn.getresponse()
    answer = r.read().decode('utf-8')

    return json.loads(answer)
