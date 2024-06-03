"""
此程序只支持win64，edge浏览器最新版的webdriver导入，
结果:在当前目录下下载webdriver驱动
"""
import requests
import zipfile
import os
import shutil
from lxml import etree # todo 单独放

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44'}

# 到官网抓取下载链接
url = 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/'
response = requests.get(url=url, headers=headers)
tree = etree.HTML(response.text)
download_url = tree.xpath("//span[text()='Stable Channel']/../../../following-sibling::div"
                          "//a[contains(@href,'win64')]/@href")
version = str(download_url).split('/')[3]
print(download_url[0])
input(f'即将下载的驱动:Edge版本为{version}\n若不是请核对自己浏览器是否为最新，或手动到官网下载:(任意键开始下载)')

# 下载到本地
response = requests.get(url=download_url[0], headers=headers)
zip_path = "./webdriver.zip"
dezip_path = "./Webdriver"
with open(zip_path, 'wb') as f:
    f.write(response.content)
    f.flush()

# 解压缩
f = zipfile.ZipFile(zip_path)
f.extractall(dezip_path)
f.close()

# 处理多余文件
os.remove(zip_path)
os.replace('./Webdriver/msedgedriver.exe', './msedgedriver.exe')
shutil.rmtree(dezip_path)
