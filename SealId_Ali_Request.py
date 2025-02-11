# -*- coding: UTF-8 -*-
try:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen, HTTPError

import ssl
import os
import base64
import json
from pdf2image import convert_from_path

context = ssl._create_unverified_context()

def get_img(img_file):
    """将本地图片转成base64编码的字符串，或者直接返回图片链接"""
    # 简单判断是否为图片链接
    if img_file.startswith("http"):
        return img_file
    else:
        with open(os.path.expanduser(img_file), 'rb') as f:  # 以二进制读取本地图片
            data = f.read()
    try:
        encodestr = str(base64.b64encode(data), 'utf-8')
    except TypeError:
        encodestr = base64.b64encode(data)

    return encodestr

def posturl(headers, body):
    """发送请求，获取识别结果"""
    try:
        params = json.dumps(body).encode(encoding='UTF8')
        req = Request(REQUEST_URL, params, headers)
        r = urlopen(req, context=context)
        response = r.read()
        return response.decode("utf8")
    except HTTPError as e:
        print(e.code)
        print(e.read().decode("utf8"))

def request(appcode, img_file):
    # 请求参数
    img = get_img(img_file)
    params = {
        'image': img
    }

    # 请求头
    headers = {
        'Authorization': 'APPCODE %s' % appcode,
        'Content-Type': 'application/json; charset=UTF-8'
    }

    response = posturl(headers, params)
    print(response)
    return response

# 请求接口
REQUEST_URL = "https://stamp.market.alicloudapi.com/api/predict/ocr_official_seal"

if __name__ == "__main__":
    # 配置信息
    appcode = "bebc0d2e711e4346acf776f9f994eca0"

    currentDir = os.getcwd()
    imageDir = os.path.join(currentDir, "images")
    responseDir = os.path.join(currentDir, "responses")
    for file in os.listdir(imageDir):
        if file.endswith((".png", ".jpg", ".pdf")):
            imageFile = os.path.join(imageDir, file)
            name = file.replace(".pdf", "").replace(".jpg", "").replace(".png", "")
            if file.endswith(".pdf"):
                images = convert_from_path(os.path.join(imageDir, file))
                for i, img in enumerate(images):
                    img.save(f"{name}.jpg")
                    imageFile = os.path.join(imageDir, f"{name}.jpg")
            
            response = request(appcode, imageFile)
            print(response)
            # write response to file in the responses directory
            responseFile = open(os.path.join(responseDir, f"{name}.txt"), "w", encoding="utf-8")
            responseFile.write(response)

