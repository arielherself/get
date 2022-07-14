import requests

MEDIA_SUFFIXES = ('.jpg', '.jpeg', '.png', '.svg', '.gif', '.tif',
    '.tiff', 'ico', '.mp3', '.mp4', '.wmv', '.aac', '.webp', '.m3u', 
    '.m3u8', '.avi', '.mov', '.asf', '.rm', '.mpeg', '.mpg', '.qt',
    '.ram', '.dat', '.rmvb', '.ra', '.viv', '.asf', '.iso', '.bin',
    '.exe', '.img', '.tao', '.dao', '.cif', '.fcd', '.swf', '.flash', 
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.flv',)

autofill_schema = lambda url_list: ['http:'+each if each.startswith('//') else each for each in url_list]
autofill_uri = lambda uri, url_list: [(uri[:-1]+each if uri.endswith('/') else uri+each) if each.startswith("/") else each for each in url_list]

def geturls(uri: str, headers: dict, autofill=False, proxy=False, http_proxy='', https_proxy=''):
    try:
        if proxy:
            raw = requests.get(uri,headers=headers,proxies={'http': http_proxy, 'https': https_proxy}).text
        else:
            raw = requests.get(uri, headers=headers).text
    except:
        return []
    raw_list = list(raw)
    urls = []

    for i, chr in enumerate(raw_list):
        if chr == '"':
            raw_list[i] = "'"
    lines = ''.join(raw_list).split('\n')
    # print(lines)

    keywords = ["='/", "'//", "'http://", "'https://"]
    for keyword in keywords:
        for line in lines:
            while line.find(keyword) != -1 and line.find("'",len(keyword)) != -1:
                urls.append(keyword[1:]+line[line.find(keyword)+len(keyword):line.find("'",line.find(keyword)+1)])
                line = line[line.find("'",line.find(keyword)+len(keyword)):]

    # print(urls)
    for i, each in enumerate(urls):
        if each.startswith("'"):
            urls[i] = each[1:]
    if autofill:
        return autofill_schema(urls)
    else:
        return urls

def geturls_recur(url_key:str, uri: str, **other_para_of_geturls):
    urls = set()

    def core(uri: str, **other_para_of_geturls):
        nonlocal urls
        try:
            current_urls = list(filter(lambda url: url_key in url, set(autofill_uri(uri, geturls(uri, **other_para_of_geturls))).difference(urls)))
            for i, each in enumerate(current_urls):
                if each.endswith('>') or each.endswith('\\'):
                    current_urls[i] = each[:-1]
            print(f'current_urls = {current_urls}')
            if current_urls:
                urls = urls.union(current_urls)
                for each in current_urls:
                    mark = True
                    for suffix in MEDIA_SUFFIXES:
                        if each.endswith(suffix) or each.endswith(suffix.upper()):
                            mark = False
                            break
                    if mark:
                        under = core(each, **other_para_of_geturls)
                        if under:   urls = urls.union(under)
            else:
                print(f'Layer returned: {urls}')
        except:
            pass

    core(uri, **other_para_of_geturls)
    return urls

if __name__ == '__main__':
    result = list(geturls_recur('cloud.tencent.com', 'https://cloud.tencent.com', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}, autofill=True, proxy=False))
    with open('result.txt', 'w', encoding='utf-8') as fil:
        for each in result:
            print(each, file=fil)
