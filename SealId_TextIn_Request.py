import requests

import os
import json
from pdf2image import convert_from_path

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

class CommonOcr(object):
    def __init__(self, img_path=None, is_url=False):
        # 印章检测识别
        self._url = 'https://api.textin.com/ai/service/v1/recognize_stamp'
        # 请登录后前往 “工作台-账号设置-开发者信息” 查看 x-ti-app-id
        # 示例代码中 x-ti-app-id 非真实数据
        self._app_id = '8fc70a949dceb5ba9842e4e4804e716c'
        # 请登录后前往 “工作台-账号设置-开发者信息” 查看 x-ti-secret-code
        # 示例代码中 x-ti-secret-code 非真实数据
        self._secret_code = '630a8332c94f445ca6d942df28ee0231'
        self._img_path = img_path
        self._is_url = is_url

    def recognize(self):
        head = {}
        try:
            head['x-ti-app-id'] = self._app_id
            head['x-ti-secret-code'] = self._secret_code
            if self._is_url:
                head['Content-Type'] = 'text/plain'
                body = self._img_path
            else:
                image = get_file_content(self._img_path)
                head['Content-Type'] = 'application/octet-stream'
                body = image
            result = requests.post(self._url, data=body, headers=head)
            return result.text
        except Exception as e:
            return e

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
            
            response = CommonOcr(img_path=imageFile)
            print(response.recognize())
            # write response to file in the responses directory
            responseFile = open(os.path.join(responseDir, f"{name}.txt"), "w", encoding="utf-8")
            responseFile.write(response)

