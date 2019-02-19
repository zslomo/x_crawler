# coding=utf-8
import os
import re
import random
import time
import json
import wget
import ssl
from tqdm import tqdm
import requests
from urllib.request import urlopen
from lxml import etree
ssl._create_default_https_context = ssl._create_unverified_context

all_page_list = []
#page number
start_page_num = 1
end_page_num = 10
#search key such as 'japan'
search = ''
root_page = "https://www.pornhub.com/video/"
start_page = "https://www.pornhub.com/video/search?search={}&page={}".format(search,start_page_num)
dist_root = '/home/bintan/kaggle/image/porn_hub/{}'.format(search)
#socks proxy
_proxies = {
  "http": "socks5://10.141.221.110:1085",
  "https": "socks5://10.141.221.110:1085"
}
_proxies2 = {
  "http": "socks5://127.0.0.1:1086",
  "https": "socks5://127.0.0.1:1086"
}
headers = {
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Chrome/56.0.2924.87'
}

def download_from_url(url, dst):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    try:
        file_size = int(urlopen(url).info().get('Content-Length', -1))

        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)
        else:
            first_byte = 0

        if first_byte >= file_size:
            return file_size
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        pbar = tqdm(
            total=file_size, initial=first_byte,
            unit='B', unit_scale=True, desc=url.split('/')[-1])
        req = requests.get(url, headers=header, stream=True)
        with(open(dst, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        pbar.close()
        return file_size
    except Exception:
        print(Exception)
        return 0
    
def process_per_page(page_url, page_num):
    title_list = []
    k = 0
    while len(title_list) == 0 and k < 5:
        if k % 2 == 0:
            proxies = _proxies
        else:
            proxies = _proxies2
        try:
            print('\nget sub_page {} of page {}'.format(page_url, page_num))
            html = s.get(page_url, headers=headers,  proxies=proxies).content
            html_origin = html.decode('utf-8')
            html = etree.HTML(html_origin)
            print('get url list, {} times'.format(k))
            title_list = html.xpath('//*[@id="main-container"]/div[2]/div[3]/h1/span/text()')
        except Exception as e:
            print(str(e))
            return
        k+=1
        time.sleep(10)
    if len(title_list) == 0:
        print('can not get page_list, quit...')
        return
    title = title_list[0]
    print(title)
    try:
        reg_720 = '\"quality\":\"720\",\"videoUrl\":\"(.*?)\"'
        reg_480 = '\"quality\":\"480\",\"videoUrl\":\"(.*?)\"'
        urlegre_720 = re.compile(reg_720)
        urlegre_480 = re.compile(reg_480)
        video_url = ''
        if len(re.findall(urlegre_720, html_origin)) != 0:
            video_url = re.findall(urlegre_720, html_origin)[0]
        else:
            video_url = re.findall(urlegre_480, html_origin)[0]
        video_url = video_url.replace('\\','')
        dist = os.path.join(dist_root,title)
#         if os.path.exists(os.path.join(dist, '{}.mp4'.format(title))):
#             print('{} has been down!'.format(title))
#             return
        if not os.path.exists(dist):
            os.makedirs(dist)
        print('download -----> {}'.format(video_url))
        print('dist is ------>{}'.format(os.path.join(dist, '{}.mp4'.format(title))))
        try:
             os.system('wget -c \"{}\" -O \"{}\"'.format(video_url,os.path.join(dist, '{}.mp4'.format(title))))
        except Exception as e:
            print('error {}-------try wget'.format(str(e)))
            try:
                download_from_url(video_url,os.path.join(dist, '{}.mp4'.format(title)))
#                 wget.download(video_url, out=os.path.join(dist, '{}.mp4'.format(title))) 
            except Exception as e:
                print('\n failed!!!!------->>>{}'.foramt(str(e)))
                return
    except Exception as e:
        print(str(e))
        return
               


    
    
s = requests.session()
#get page
curr_page = start_page
for i in range(start_page_num, end_page_num):
    # print(html)
    page_list = []
    k = 0
    while len(page_list) == 0 and k < 5:
        if k % 2 == 0:
            proxies = _proxies
        else:
            proxies = _proxies2
        try:
            print('get page {}, {} times'.format(i, k))
            html = s.get(curr_page, headers=headers, proxies=proxies).content
            html = html.decode('utf-8')
            html = etree.HTML(html)
            page_list = html.xpath('//*[@id="videoSearchResult"]/li/div/div/span[1]/a/@href')
        except Exception as e:
            print(str(e))
            continue
        k+=1
        time.sleep(10)
    if len(page_list) == 0:
        print('can not get page_list, quit...')
        continue
    for page_url in page_list:
        time.sleep(0.5)
        process_per_page('https://www.pornhub.com{}'.format(page_url), i)    
    curr_page = 'https://www.pornhub.com/video/search?search={}&page={}'.format(search,i+1)
s.close()
