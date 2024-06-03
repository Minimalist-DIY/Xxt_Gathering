"""
本脚本针对学习通章节测验进行自动回答
原理:使用正则对照网络答案及原文找到答案，由selenium操控浏览器进行输入操作。
要点:
1. 需要手动修改课程答案网址，具体请在本文件中搜索【
2. 图像识别使用Cnocr库
3. 本程序Bug很多变量命名混乱非常不稳定，从题库文件提取题目要求很严格
4. 由于过于复杂，程序中留下了很多print请勿删除，以防看不懂
5. 由于程序不稳定过高，找不到题目时不清楚是识别失败或题库没有，当识别失败默认直接结束程序
6. 其他坑清在本文中搜索】
"""

# selenium相关库
from selenium import webdriver  # 模拟浏览器要用
from selenium.webdriver.edge.service import Service  # 新方法要用
from selenium.webdriver.common.by import By  # 定位要用
from selenium.webdriver.edge.options import Options  # 无头浏览器要用
import selenium.common.exceptions  # try异常要用

from time import sleep, time  # 强制睡眠要用,计算运行用时
from difflib import get_close_matches  # 文本相似度要用
import re  # 正则获取答案
from PIL import Image  # 截图要用
from io import BytesIO  # bytes转换为bytesio
from cnocr import CnOcr  # OCR
input("断点调试0:")
# 浏览器程序位置
EXECUTABLE_PATH = r'\MicrosoftWebDriver.exe'
# 隐式等待最大时长(s)
WAIT_TIME = 5


class XxtCourse:
    def __init__(self):
        # self.lesson_name = input('请输入要刷的课程全名:')
        print('好的，程序即将启动(^人^)')
        self.lesson_name = '*'
        self.start_time = time()
        self.configuration_program()

    def main_program(self):
        self.login_chaoxing()
        self.switch_course()
        self.handle_lesson()

    def configuration_program(self):
        s = Service(executable_path=EXECUTABLE_PATH)
        # 无头浏览器配置（可选）
        edge_options = Options()
        # edge_options.add_argument('--headless')
        # edge_options.add_argument('--disable-gpu')
        edge_options.add_argument('--mute-audio')
        # 规避监测（默认开启）
        edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        edge_options.add_argument('--disable-blink-features=AutomationControlled')

        self.bro = webdriver.Edge(service=s, options=edge_options)
        # 隐式等待
        self.bro.implicitly_wait(WAIT_TIME)

        # cnocr
        self.cocr = CnOcr(det_model_name='native_det')

        # 打开答案文件
        self.fp = open('xxt_answers.txt', 'r', encoding='utf-8')
        self.lines = self.fp.readlines()

    def login_chaoxing(self):
        url = 'https://passport2.chaoxing.com/login' \
              '?fid=&newversion=true&refer=https://i.chaoxing.com'
        self.bro.get(url)
        # 学习通登录
        phone = self.bro.find_element(By.ID, 'phone')
        phone.send_keys("*")
        password_to = self.bro.find_element(By.ID, 'pwd')
        password_to.send_keys('*')
        self.bro.find_element(By.ID, 'loginBtn').click()
        sleep(0.5)
        if self.bro.title == "用户登录":
            print("账号密码有误!!!")
            self.__del__()
        print("登录成功！")

    def switch_course(self):
        try:
            self.bro.find_element(By.NAME, '课程').click()
        except selenium.common.exceptions.StaleElementReferenceException:
            self.bro.find_element(By.NAME, '课程').click()
        self.bro.switch_to.frame('frame_content')

        # [1]正常方式
        courses = self.bro.find_elements(By.XPATH, '/html/body/div/div/div/div[2]/div/div[2]/div[3]/div/div['
                                                   '2]/div/div[2]/h3/a/span')
        courses_list = []
        for c in courses:
            courses_list.append(c.text)
        print(courses_list)  # 本用于图形界面下拉菜单
        course = self.bro.find_element(By.XPATH, f'//span[@title="{self.lesson_name}"]')
        self.bro.execute_script('arguments[0].click();', course)

        # 跳转课程页面
        self.bro.switch_to.window(self.bro.window_handles[-1])
        self.bro.find_element(By.LINK_TEXT, '章节').click()
        self.bro.switch_to.frame('frame_content-zj')
        # 筛选出 未完成任务点 的章节
        chapters = self.bro.find_elements(By.XPATH, '//div[@class="catalog_task"]/input['
                                                    '@value]/../preceding-sibling::div[1]/a/span')
        # ！这里包括 课程找不到未完成的课程 和 未找到课程 两种情况
        if not chapters:
            print("本门课程好像已经学完了呢 ^o^")
            quit()
        else:
            self.chapter_numbers = []
            for chapter in chapters:
                self.chapter_numbers.append(chapter.text)
            print(self.chapter_numbers)
            self.bro.execute_script('arguments[0].click();', chapters[0])

    def handle_lesson(self):
        sleep(2)
        chapter_name = self.bro.find_element(By.XPATH, '//*[@id="mainid"]/div[5]/div').text
        print('开始刷课:' + chapter_name)

        # 删除人脸识别弹窗
        if self.bro.execute_script("return document.getElementsByClassName('maskDiv1')[0]"):
            self.bro.execute_script("document.getElementsByClassName('maskDiv1')[0].remove()")

        # 每章第一节首页可能是学习目标，需要切换到题目页,也可能没有题目
        question_screen = self.bro.find_elements(By.XPATH, '//*[@title="章节测验"]')
        if question_screen:
            question_screen[0].click()

        # 关闭侧边栏防止挡住题目
        switch_button = self.bro.find_elements(By.XPATH, '//*[@id="selector"]/div[@class="switchbtn"]')
        if switch_button:
            switch_button[0].click()

        self.bro.switch_to.frame('iframe')
        second_frame = self.bro.find_element(By.TAG_NAME, 'iframe')
        self.bro.switch_to.frame(second_frame)
        self.bro.switch_to.frame('frame_content')

        divs = self.bro.find_elements(By.XPATH, '//*[@id="ZyBottom"]/div')  # 定位到全部题目及选项
        for i in range(len(divs)):
            # 】有坑:滑动可能不准仍有元素被挡的情况
            self.bro.execute_script("arguments[0].scrollIntoView(false);", divs[i])
            question = divs[i].find_element(By.XPATH, './div[1]/div')
            print('question:', question.text)
            question_png = question.screenshot_as_png
            true_answers = self.match_answer(question_png)  # 此时已为[,乱,]或“对/错”
            answer_elements = divs[i].find_elements(By.XPATH, "./div/div//ul/li")
            print('调试，看长度', len(answer_elements))
            all_answer_texts = []

            for answer_element in answer_elements:
                print('开始识别ocr，', end='')
                all_answer_texts.append(self.ocr(answer_element.screenshot_as_png))

            print('正确答案ture_answers:', true_answers)
            index_answers = []
            for true_answer in true_answers:
                true_answer = get_close_matches(true_answer, all_answer_texts, n=1, cutoff=0.2)
                print("正确答案匹配结果:", true_answer)
                if true_answer:
                    true_answer = true_answer[0]
                else:
                    print('答案匹配失败，all_answer:', all_answer_texts)
                    quit()
                index_answers.append(all_answer_texts.index(true_answer))

            for number in index_answers:
                answer_elements[number].click()
        # input('提交吗？')
        self.bro.find_element(By.XPATH, '//*[text()="提交"]').click()
        self.bro.find_element(By.XPATH, '//*[@id="popok"]').click()
        # input('看看结果')
        
        score = self.bro.find_element(By.XPATH, '//span[@class="achievement"]/i').text
        print("得分:", score)
        if score != '100':
            print('哪里错了╰（‵□′）╯')
            quit()

        self.bro.switch_to.default_content()  # ?
        self.chapter_numbers.remove(self.chapter_numbers[0])
        if self.chapter_numbers:
            next_chapter = self.bro.find_elements(By.XPATH, f"//*[text()='{self.chapter_numbers[0]}']")
            self.bro.execute_script("arguments[0].scrollIntoView();", next_chapter[0])
            self.bro.execute_script('arguments[0].click();', next_chapter[0])
            self.handle_lesson()
        else:
            print('The course is over!')
            print('\a')
            sleep(1)
            print('\a')
        sleep(3)

    def match_answer(self, png):
        question = self.ocr(png)
        print("识别出来的问题为", question)
        # 古老代码
        """
        #截获课程所在段
        if 'answer_column' not in dir():
            answer_column = ['000']
        if self.chapter_names[0] != answer_column[0].replace('\n',''):
            # 【1】如果txt标题不标准就搜不到了？
            start = self.lines.index(self.chapter_names[0] + '\n')
            if self.chapter_names[0] == self.chapter_names[1]:
                end = len(self.lines)
            end = self.lines.index(self.chapter_names[1] + '\n')
            answer_column = self.lines[start:end]
        """

        matched_question = get_close_matches(question, self.lines, n=1, cutoff=0.2)
        print(f'题库中对应的题目:{matched_question}')
        if matched_question:
            matched_question = matched_question[0]
        else:
            print(f'匹配失败，question:{question}')
            quit()

        index_start = self.lines.index(matched_question)
        for i in range(index_start + 1, len(self.lines)):
            if self.lines[i][0].isdigit():
                all_text = self.lines[index_start:i]
                break
        # 两种情况，先检查（）内有答案的情况
        # 有些不标准的没有括号（）请修正txt
        answer = re.search(r"[(|（]([A-F 对 错 x √ ×]{1,4})[)|）]", matched_question, flags=re.I)
        if answer:
            answer = answer.group(1).upper()
        # 第二种情况，找“答案”关键词
        else:
            for text in all_text[::-1]:
                answer = re.search(r"答案.*?([A-F 对 错 x √ ×]{1,4})", text, flags=re.I)
                if answer:
                    answer = answer.group(1).upper()
                    break
        if answer:
            replace_dict = {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5', 'F': '6',
                            '对': '对', '错': '错', 'X': '错', '√': '对', '×': '错'}  # 要是还有其他的就加进去
            for key, value in replace_dict.items():
                answer = answer.replace(key, value)
            if answer.isdigit():
                answer = list(answer)
                for i in range(len(answer)):
                    answer[i] = all_text[int(answer[i])]
        else:  # 完全找不到时
            print(f'txt文件中存在不符合规律的语句:{all_text},请修改后再尝试')
            quit()
        return answer

    def ocr(self, img_bytes):
        # 字节转image
        i = Image.open(BytesIO(img_bytes))
        # 识别
        out = self.cocr.ocr(i)[0]["text"]
        print("选项识别结果out:", out)
        return out

    @staticmethod
    def get_answers_txt():
        # 抓取网络答案
        import requests
        from lxml import etree
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                                 '537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/'
                                 '537.36 Edg/108.0.1462.54'}
        # 【1】这里填答案渠道的网址，格式越标准越好
        url = 'https://zhuanlan.zhihu.com/p/525625245'
        response = requests.get(url=url, headers=headers)
        tree = etree.HTML(response.text)
        # 【2】这里需要自己找下网页的答案位置
        answer_txt = tree.xpath('//*[@id="root"]/div/main/div/article/div[1]/div/div/div/p//text()')
        with open('xxt_answers.txt', 'a', encoding='utf-8') as fp:
            for text in answer_txt:
                fp.write(text + '\n')
            # fp.write(response.text)
            print("OK! The web page has been saved in txt format")
        # 【3】注意下文本中的判断题对，错是什么写法，去match_answer()里改

    def __del__(self):
        self.fp.close()
        end_time = time()
        run_time = end_time - self.start_time
        print("程序已结束", end=',')
        print("用时:{:.2f}".format(run_time))
        # 页面停留显示3秒（仅供有界面时使用）
        sleep(3)
        self.bro.quit()


demo = XxtCourse()
demo.main_program()
# demo.get_answers_txt()
