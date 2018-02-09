# coding:utf-8

import urllib.request
import re
import json
from urllib.parse import urljoin
import os
import sys
import platform

def merge_and_delete_video(save_path, name):
    sysstr = platform.system()
    if sysstr == "Windows":
        path = save_path.replace('/', '\\')
        os.system(r'copy /b "{path}\*.ts" "{path}\..\{name}.ts"'.format(path = path, name = name))
        os.system(r'del "{path}\*.ts" & rd "{path}"'.format(path=path))

    if sysstr == "Linux":
        os.system(r'cat {path}/*.ts > {path}/../{name}.ts'.format(path=save_path, name=name.replace(r' ', r'\ ')))
        os.system(r'rm -r {path}'.format(path=save_path))

def get_video_detail_url_list(video_url):
    resp = urllib.request.urlopen(video_url)
    html_content = resp.read()

    return re.findall(b'/.*?[.]ts', html_content)

def string_to_json(string_data):
    json_data = json.loads(string_data)
    
    return json_data.get('playUrl'), json_data.get('title')

def get_download_url(target_url):
    resp = urllib.request.urlopen(target_url)    

    html_content = resp.read()
    try:
        video_content = re.search(b'window.oPageConfig.oVideo.?=.?(.*?);', html_content).group(1)
        video_url, title = string_to_json(video_content)
        video_detail_url_list = get_video_detail_url_list(video_url)
        
        global global_title
        global_title = title

        path = sys.path[0] + '/' + video_url.split('/')[-1]
        sysstr = platform.system()
        if sysstr == "Windows":
            if not os.path.exists(path.replace('/', '\\')):
                os.system('md %s' % '"%s"' % path.replace('/', '\\'))
            
        if sysstr == "Linux":
            if not os.path.exists(path):
                os.makedirs(path)
        
        for video_detail_url in video_detail_url_list:
            download_url = urljoin(video_url, video_detail_url.decode(), allow_fragments=True)
            save_path = '{path}{name}'.format(path=path, name=video_detail_url.decode())

            yield download_url, save_path

    except:
        print('下载失败')

def download(target_url, save_path = None):
    '''
    target_url: 观看视频的网址
    save_path: 下载的视频文件保存的路径
    '''
    for download_url, path in get_download_url(target_url):
        headers = {
                    'Origin':'https://www.zhanqi.tv',
                    'Referer':target_url,
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                }
        req = urllib.request.Request(download_url, headers=headers)
        resp = urllib.request.urlopen(req)

        if not save_path:
            save_path = path

        with open(path, 'wb') as code:
            code.write(resp.read())
            print('download {path}'.format(path=path))
        # break

    return '/'.join(save_path.split('/')[:-1])

def main():
    # target_url = input('请输入战旗视频地址：')
    # save_name = input('请输入保存后视频文件名称：')
    target_url = 'https://www.zhanqi.tv/v2/videos/458607.html?from=owl'
    save_path = download(target_url)
    merge_and_delete_video(save_path, global_title)

if __name__ == "__main__":
    main()