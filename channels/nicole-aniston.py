# coding=utf-8
import os,sys
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
# page number
start_page_num = 1
end_page_num = 3
# search key such as 'japan'
search = 'teens-hd'
root_page = "https://www.pornhub.com/video/"
start_page = "https://www.pornhub.com/channels/{}/videos?o=ra&page={}".format(search, start_page_num)
dist_root = 'F:\\dist\\{}'.format(search)
# socks proxy
if not os.path.exists(dist_root):
    os.makedirs(dist_root)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}


def download_from_url(url, dst, page_url):
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
        header = {
            "Accept-Encoding": "identity;q=1, *;q=0",
            "Range": "bytes=%s-%s" % (first_byte, file_size),
            "Referer": page_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        # print(header)

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
        try:
            print('\nget sub_page {} of page {}'.format(page_url, page_num))
            html = s.get(page_url, headers=headers).content
            html_origin = html.decode('utf-8')
            html = etree.HTML(html_origin)

            # title_list = html.xpath('//*[@id="main-container"]/div[2]/div[3]/h1/span/text()')
            title_list = html.xpath('//*[@class="title"]/span/text()')
            print(title_list)
        except Exception as e:
            print(str(e))
            return
        k += 1
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

        if len(re.findall(urlegre_720, html_origin)) != 0:
            video_url = re.findall(urlegre_720, html_origin)[0]
        else:
            video_url = re.findall(urlegre_480, html_origin)[0]
        video_url = video_url.replace('\\', '')

        print('download -----> {}'.format(video_url))
        # print(video_url)
        print('dist is ------>{}'.format(os.path.join(dist_root, '{}.mp4'.format(title))))
        download_from_url(video_url, os.path.join(dist_root, '{}.mp4'.format(title.replace(':', '_'))), page_url)
        # try:
        #     os.system('wget -c -e "http_proxy=http://127.0.0.1:12649" \"{}\" -O \"{}\"'.format(
        #         video_url, os.path.join(dist_root, '{}.mp4'.format(title))))
        # except Exception as e:
        #     print('error {}-------try wget'.format(str(e)))
        #     try:
        #         download_from_url(video_url, os.path.join(dist_root, '{}.mp4'.format(title)))
        #     #                 wget.download(video_url, out=os.path.join(dist, '{}.mp4'.format(title)))
        #     except Exception as e:
        #         print('\n failed!!!!------->>>{}'.foramt(str(e)))
        #         return
    except Exception as e:
        print(str(e))
        return


s = requests.session()
# get page
curr_page = start_page
for i in range(start_page_num, end_page_num):
    # print(html)
    page_list = []
    k = 0
    while len(page_list) == 0 and k < 5:
        try:
            print('get page {}, {} times'.format(i, k))
            html = s.get(curr_page, headers=headers).content
            html = html.decode('utf-8')
            html = etree.HTML(html)
            page_list = html.xpath('//*[@id="showAllChanelVideos"]/li/div[1]/div[3]/span/a/@href')
        except Exception as e:
            print(str(e))
            continue
        k += 1
        time.sleep(10)
    if len(page_list) == 0:
        print('can not get page_list, quit...')
        continue
    for page_url in page_list:
        time.sleep(0.5)
        process_per_page('https://www.pornhub.com{}'.format(page_url), i)
    curr_page = "https://www.pornhub.com/channels/{}/videos?o=ra&page={}".format(search, i + 1)
s.close()
