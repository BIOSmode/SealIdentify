import os
import json
import pandas as pd
from pdf2image import convert_from_path

def extract_seal_number(info):
    result = ''.join(filter(str.isdigit, info))
    print(result)
    return result

def extract_seal_info(responsePath):
    responseFile = open(responsePath, 'rb')
    response = responseFile.read().decode('utf-8')
    info = json.loads(response)

    return {
        "企业名称": info['result'][0]['text']['content'],
        "备案编码": extract_seal_number(info['result'][0]['general_text'][0]['content']),
        "文件来源": responsePath.split("\\")[-1]
    }

# 处理所有合同文件
results = []
currentDir = os.getcwd()
responseDir = os.path.join(currentDir, "responses")
for file in os.listdir(responseDir):
    if file.endswith((".txt")):
            results.append(extract_seal_info(os.path.join(responseDir, file)))


# 导出到Excel
df = pd.DataFrame(results)
df.to_excel("提取结果.xlsx", index=False)