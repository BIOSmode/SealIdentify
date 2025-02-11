import os
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

# 配置Tesseract路径（根据实际安装路径修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def unwrap_seal(img_roi):
      polar = cv2.warpPolar(img_roi, (300, 1000), (150,150), 150, 
                        cv2.WARP_POLAR_LINEAR + cv2.WARP_INVERSE_MAP)
      return cv2.rotate(polar, cv2.ROTATE_90_COUNTERCLOCKWISE)

def extract_seal_info(image_path):
    #增强对比度
    img = cv2.imread(image_path)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l_enhanced = clahe.apply(l)
    enhanced_lab = cv2.merge((l_enhanced,a,b))
    enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    cv2.imshow("enhanced_img", enhanced_img)

    #降噪处理
    denoised = cv2.fastNlMeansDenoisingColored(enhanced_img, None, 10, 10, 7, 21)
    cv2.imshow("denoised", denoised)

    #公章定位
    #颜色阈值法
    hsv = cv2.cvtColor(denoised, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv", hsv)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(denoised, lower_red, upper_red)
    cv2.imshow("mask", mask)

    #形态学优化
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    # closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    #轮廓检测与筛选
    # contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000 
    #                   and abs(cv2.matchShapes(cnt, cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt,True), True)) < 0.1)]

    #环形文字展开技术
    unwrapped_img = unwrap_seal(denoised)
    cv2.imshow("unwrapped_img", unwrapped_img)
    cv2.waitKey(0)

    #OCR增强配置
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    text = pytesseract.image_to_string(denoised, config=custom_config, lang='chi_sim')
    text1 = pytesseract.image_to_string(denoised, lang='chi_sim')

    print(text)
    print(text1)


# 处理所有合同文件
results = []
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
