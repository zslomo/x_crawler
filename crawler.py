# coding=utf-8
import os
import random
import re
import time
from urllib.request import urlopen
import sys
import numpy as np
import requests
from tqdm import tqdm

from utils import read_params


def download_from_url(url, dst):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    # print(url)
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


def get_url():
    urlLists = []
    for i in range(params.start_page, params.end_page):
        time.sleep(random.randint(1, 3))
        if i == 0:
            url = landingPageBaseUrl
        else:
            url = landingPageBaseUrl + key + str(i)
        if i == 0 and params.ifnew:
            url = landingPageBaseUrl[:-4]
        print("get url : " + url)
        html = requests.get(url).text

        reg = r'<a href="(.*?)"><img src="(.*?)" data-src="(.*?)"(.*?)'
        urlegre = re.compile(reg)
        urls = re.findall(urlegre, html)

        urlList = np.array(urls)[:, 0]

        print('url counts in page {} is '.format(i), urlList.shape[0])
        urlLists.extend(urlList)
    return urlLists


def get_videos(urlList):
    for e in urlList:
        time.sleep(random.randint(1, 4))
        pageUrl = params.baseUrl + e
        print('get page : {} '.format(pageUrl))
        try:
            html = requests.get(pageUrl).text
        except Exception:
            print('page {} got exception{}'.format(pageUrl, Exception))
            continue
        reg = r'html5player.setVideoUrlHigh\((.*?)\);'
        title_reg = r'<head>\n<title>(.*?)</title>'
        urlegre = re.compile(reg)
        titlegre = re.compile(title_reg)
        # get url
        url = re.findall(urlegre, html)

        title = re.findall(titlegre, html)
        data_dir = os.path.join(params.data_dir, clas)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, mode=0o755)

        dist = os.path.join(data_dir, title[0] + '.mp4')
        # ignore the file which has already downloaded
        if os.path.exists(dist) or os.path.exists(dist[:-4] + ' - XVIDEOS.COM' + dist[-4:]):
            print('file {} exit'.format(title[0]))
            continue
        print('start download file to {}'.format(dist))
        try:

            file_size = download_from_url(url=url[0][1:-1], dst=dist)
        except IndexError:
            print('got IndexError : {} '.format(IndexError))
            continue
        # if the download function throw an error continue
        if (file_size == 0):
            print("down load {} failed delete it".format(title[0]))
            try:
                os.remove(dist)
            except Exception:
                print(Exception)
                continue


if __name__ == "__main__":
    params = read_params()

    key, clas= '', ''
    if params.iftag:
        landingPageBaseUrl = params.baseUrl + '/tag/' + params.tag_name
        clas = params.tag_name
    elif params.ifsearch:
        search_name = ''
        if ' ' in params.search_name:
            search_name = params.search_name.replace(' ','+')
        landingPageBaseUrl = params.baseUrl + '/?k=' + search_name
        clas = params.search_name
        key = '&p='
    else:
        landingPageBaseUrl = params.baseUrl + '/new/'
        clas = 'new'

    if params.ifsearch + params.iftag + params.ifnew > 1:
        print('Those three ifxx params only one can be 1 !!!')
        sys.exit()
    urlList = get_url()
    print('This page has {} videos'.format(len(urlList)))

    get_videos(urlList)
