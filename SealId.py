import os
import cv2
import pytesseract
import re
import pandas as pd
import numpy as np
from pdf2image import convert_from_path

# 配置Tesseract路径（根据实际安装路径修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_seal_info(image_path):
    # 读取图片并转为灰度图
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # # 颜色检测（针对彩色公章，可选步骤）
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # lower_red = np.array([0, 100, 100])
    # upper_red = np.array([10, 255, 255])
    # mask = cv2.inRange(hsv, lower_red, upper_red)
    # contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # if contours:
    #     x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    #     roi = gray[y:y+h, x:x+w]
    # else:
    #     roi = gray  # 若未检测到红色区域，使用全图

    roi = gray  # 若未检测到红色区域，使用全图
    # OCR识别
    text = pytesseract.image_to_string(roi, lang='chi_sim')
    
    # 正则提取企业名称和备案编码
    company = re.search(r'企业名称[:：]\s*([^\n]+)', text)
    code = re.search(r'备案编码[:：]\s*([A-Za-z0-9]+)', text)
    
    return {
        "企业名称": company.group(1) if company else "",
        "备案编码": code.group(1) if code else ""
    }

# 处理所有合同文件
currentDir = os.getcwd()
for file in os.listdir(currentDir):
    if file.endswith((".png", ".jpg", ".pdf")):
        if file.endswith(".pdf"):
            images = convert_from_path(os.path.join(currentDir, file))
            for i, img in enumerate(images):
                img.save(f"temp_{i}.jpg")
                results.append(extract_seal_info(f"temp_{i}.jpg"))
        else:
            results.append(extract_seal_info(os.path.join(currentDir, file)))

# 导出到Excel
df = pd.DataFrame(results)
df.to_excel("提取结果.xlsx", index=False)