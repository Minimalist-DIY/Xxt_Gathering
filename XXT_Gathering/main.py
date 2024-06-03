"""
此程序为主程序，下载好对应的库和驱动后就能跑
已写图形界面，操作简单

方式：
原理:通过已获取的课程链接跳过进入所需的人脸识别，通过去除蒙面识别暂停点的方式跳过课程中间的人脸识别和小测验。
"""

# pyqt5库
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtCore import QThread, pyqtSignal, QWaitCondition, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
# selenium库
from selenium import webdriver  # 模拟浏览器要用
from selenium.webdriver.edge.service import Service  # 新方法要用
from selenium.webdriver.common.by import By  # 定位要用
# from selenium.webdriver import ActionChains  # 动作链
from selenium.webdriver.edge.options import Options  # 无头浏览器要用
# from selenium.webdriver.support.wait import WebDriverWait  # 显式等待要用
# from selenium.webdriver.support import expected_conditions as EC  # xian配合使用
import selenium.common.exceptions as exceptions  # try异常要用
# from logging import error
from time import sleep, time  # 强制睡眠要用,计算运行用时

import os

# 浏览器程序位置
EXECUTABLE_PATH = r'./msedgedriver.exe'
# 隐式等待最大时长(s)
WAIT_TIME = 5


class UiTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        # 设置线程
        self.thread = XxtCourse()
        self.thread.message_sign.connect(self.message_send)
        self.thread.details_sign.connect(self.details_send)
        # self.thread.finished.connect(self.thread.deleteLater)
        # 设置字体
        self.font = QtGui.QFont()
        self.font2 = QtGui.QFont()
        # font.setFamily("楷体")
        # self.font.setFamily("等线")
        self.font.setPointSize(10)
        self.font2.setPointSize(8)
        # 设置父窗格
        self.setWindowTitle("学习通AUTO程序")
        # self.resize(552, 460)
        self.setGeometry(700, 200, 550, 460)
        self.setFont(self.font)

        self.login_tab = QtWidgets.QWidget()
        self.class_tab = QtWidgets.QWidget()
        self.tab_2 = QtWidgets.QWidget()

        self.addTab(self.login_tab, "登录")
        self.addTab(self.class_tab, "刷课")
        self.addTab(self.tab_2, "刷题")

    def main(self):
        self.login_tab_ui()
        self._import_u_p()
        self.class_tab_ui()
        self.tab2_ui()
        self.setTabVisible(1, False)
        self.setTabVisible(2, False)
        self.show()

    def details_send(self, details_txt):
        self.text_details.append(details_txt)

    def message_send(self, message_txt):
        if type(message_txt) == list:  # todo 放到第一去
            self.setTabVisible(1, True)
            self.setTabVisible(2, True)
            self.setTabVisible(0, False)
            for c in message_txt:
                self.course_comboBox.addItem(c)
        elif message_txt[0] == "x" and "thread" in self.__dir__():
            QMessageBox.warning(self, '报错信息', message_txt, QMessageBox.Yes)
            self.thread.terminate()  # todo 太复杂了直接停止报错算了
            self.thread.wait()
            self.thread = None
            quit()
        elif message_txt[0] == 'o':
            QMessageBox.warning(self, '信息', message_txt, QMessageBox.Yes)
            self.thread.wait_condition.wakeAll()

    def login_xxt(self, user, pwd, ismute, isvisiable=True):
        # self.thread.action = self.thread.configuration_program
        if not os.path.exists('Xxt_data.txt'):
            with open('Xxt_data.txt', 'w', encoding='utf-8') as fp1:
                text = f"username:{user}\npassword:{pwd}"
                fp1.write(text)
        self.thread.argument = ('login', user, pwd, ismute, isvisiable)
        self.thread.start()

    def _import_u_p(self):
        if os.path.exists('Xxt_data.txt'):
            with open('Xxt_data.txt', 'r', encoding='utf-8') as fp:
                username = fp.readline().split(':')[1]
                password = fp.readline().split(':')[1]
                self.lineEdit_user.setText(username)
                self.lineEdit_pwd.setText(password)

    def login_tab_ui(self):
        # 登录按钮
        login1_Button = QtWidgets.QPushButton(self.login_tab)
        login1_Button.setText("登录")
        login1_Button.setGeometry(QtCore.QRect(290, 210, 93, 28))
        login1_Button.setFont(self.font)
        login1_Button.setObjectName("login1_Button")
        login1_Button.clicked.connect(
            lambda: self.login_xxt(
                self.lineEdit_user.text(),
                self.lineEdit_pwd.text(),
                mute_checkBox.isChecked(),
                visible_checkBox.isChecked()))
        # 显示浏览器界面
        visible_checkBox = QtWidgets.QCheckBox(self.login_tab)
        visible_checkBox.setText("显示浏览器界面")
        visible_checkBox.setToolTip("不建议开启防止误触，反正开了你也基本不敢操控")
        visible_checkBox.setGeometry(QtCore.QRect(134, 210, 151, 28))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(visible_checkBox.sizePolicy().hasHeightForWidth())
        visible_checkBox.setSizePolicy(sizePolicy)
        visible_checkBox.setFont(self.font)
        visible_checkBox.setAutoRepeat(False)
        visible_checkBox.setObjectName("visible_checkBox")

        line = QtWidgets.QFrame(self.login_tab)
        line.setGeometry(QtCore.QRect(130, 250, 251, 20))
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setObjectName("line")
        # 扫码登录按钮
        lgoin2_Button = QtWidgets.QPushButton(self.login_tab)
        lgoin2_Button.setText("点我扫码登录")
        lgoin2_Button.setGeometry(QtCore.QRect(275, 272, 111, 31))
        lgoin2_Button.setFont(self.font)
        lgoin2_Button.setObjectName("lgoin2_Button")
        lgoin2_Button.clicked.connect(lambda: self.login_xxt('', '', mute_checkBox.isChecked()))
        # "本地登录"
        label_loc_login = QtWidgets.QLabel(self.login_tab)
        label_loc_login.setText("本地登录：")
        label_loc_login.setGeometry(QtCore.QRect(120, 88, 72, 15))
        label_loc_login.setFont(self.font)
        label_loc_login.setObjectName("label_loc_login")
        # "在线登录"
        label_onli_login = QtWidgets.QLabel(self.login_tab)
        label_onli_login.setText("在线登录:")
        label_onli_login.setGeometry(QtCore.QRect(125, 280, 72, 15))
        label_onli_login.setFont(self.font)
        label_onli_login.setObjectName("label_onli_login")
        # 欢迎
        label_wel = QtWidgets.QLabel(self.login_tab)
        label_wel.setText("欢迎使用学习通刷课程序")
        label_wel.setGeometry(QtCore.QRect(1, 26, 531, 18))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHeightForWidth(label_wel.sizePolicy().hasHeightForWidth())
        label_wel.setSizePolicy(sizePolicy)
        label_wel.setFont(self.font)
        label_wel.setAlignment(QtCore.Qt.AlignCenter)
        label_wel.setObjectName("label_wel")
        # 静音
        mute_checkBox = QtWidgets.QCheckBox(self.login_tab)
        mute_checkBox.setText("静音")
        mute_checkBox.setGeometry(17, 387, 95, 22)
        mute_checkBox.setObjectName("mute_checkBox")
        mute_checkBox.setFont(self.font)
        mute_checkBox.setChecked(True)
        # 水印
        label_watermask = QtWidgets.QLabel(self.login_tab)
        label_watermask.setText("这是水印")
        label_watermask.setGeometry(QtCore.QRect(440, 394, 72, 22))
        label_watermask.setFont(self.font)
        label_watermask.setObjectName("label_watermask")
        # 连接的
        layoutWidget = QtWidgets.QWidget(self.login_tab)
        layoutWidget.setGeometry(QtCore.QRect(140, 115, 241, 89))
        layoutWidget.setObjectName("layoutWidget")
        # 捆住手机号和密码两栏的
        gridLayout = QtWidgets.QGridLayout(layoutWidget)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setObjectName("gridLayout")
        # 输入密码
        self.lineEdit_pwd = QtWidgets.QLineEdit(layoutWidget)
        self.lineEdit_pwd.setMinimumSize(QtCore.QSize(30, 30))
        self.lineEdit_pwd.setPlaceholderText("重新保存请删除Xxt_data文件")
        self.lineEdit_pwd.setFont(self.font2)
        self.lineEdit_pwd.setObjectName("lineEdit_pwd")
        gridLayout.addWidget(self.lineEdit_pwd, 1, 1, 1, 1)
        # 输入手机号
        self.lineEdit_user = QtWidgets.QLineEdit(layoutWidget)
        self.lineEdit_user.setPlaceholderText("用户名及密码会本地保存")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_user.sizePolicy().hasHeightForWidth())
        self.lineEdit_user.setSizePolicy(sizePolicy)
        self.lineEdit_user.setMinimumSize(QtCore.QSize(30, 30))
        self.lineEdit_user.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lineEdit_user.setFont(self.font2)
        self.lineEdit_user.setObjectName("lineEdit_user")
        gridLayout.addWidget(self.lineEdit_user, 0, 1, 1, 1)
        # "密码"
        label_pwd = QtWidgets.QLabel(layoutWidget)
        label_pwd.setText("密码")
        label_pwd.setFont(self.font)
        label_pwd.setAlignment(QtCore.Qt.AlignCenter)
        label_pwd.setObjectName("label_pwd")
        gridLayout.addWidget(label_pwd, 1, 0, 1, 1)
        # "手机号"
        label_user = QtWidgets.QLabel(layoutWidget)
        label_user.setText("手机号")
        label_user.setFont(self.font)
        label_user.setObjectName("label_user")
        gridLayout.addWidget(label_user, 0, 0, 1, 1)

    def brush_xxt(self, isface):
        self.brush_Button.setEnabled(False)
        if not isface:
            course = self.course_comboBox.currentText()
        else:
            course = self.face_textEdit.toPlainText()

        self.thread.argument = ('brush', course, isface)
        self.thread.start()

    def _radio_button_toggled(self, checked):
        # 检查单选框的状态
        if checked:
            self.course_comboBox.setHidden(True)
            self.face_textEdit.setHidden(False)
        else:
            self.course_comboBox.setHidden(False)
            self.face_textEdit.setHidden(True)

    def class_tab_ui(self):
        """
        刷课页面
        """
        # 人脸识别课程选项
        isface_radioButton = QtWidgets.QRadioButton(self.class_tab)
        isface_radioButton.setText("我的课程有人脸识别")
        isface_radioButton.setGeometry(QtCore.QRect(40, 70, 340, 21))
        isface_radioButton.setObjectName("isface_radioButton")
        isface_radioButton.toggled.connect(self._radio_button_toggled)
        self.face_textEdit = QtWidgets.QTextEdit(self.class_tab)
        self.face_textEdit.setPlaceholderText("请输入课程网址：(不懂看教程!!!)")
        self.face_textEdit.setGeometry(QtCore.QRect(60, 100, 461, 41))
        self.face_textEdit.setAcceptRichText(False)
        self.face_textEdit.setHidden(True)
        self.face_textEdit.setObjectName("face_textEdit")

        label_watermask2 = QtWidgets.QLabel(self.class_tab)
        label_watermask2.setText("这是水印")
        label_watermask2.setGeometry(QtCore.QRect(450, 390, 72, 22))
        label_watermask2.setObjectName("label_watermask2")
        # 选择和选项两者间
        # splitter = QtWidgets.QSplitter(self.class_tab)
        # splitter.setGeometry(QtCore.QRect(40, 30, 136, 21))
        # splitter.setOrientation(QtCore.Qt.Horizontal)
        # splitter.setObjectName("splitter")

        xuanze_label = QtWidgets.QLabel(self.class_tab)
        xuanze_label.setText("选择：")
        xuanze_label.setGeometry(40, 30, 46, 21)
        xuanze_label.setObjectName("xuanze_label")
        # 下拉课程列表
        self.course_comboBox = QtWidgets.QComboBox(self.class_tab)
        self.course_comboBox.setGeometry(92, 31, 180, 21)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.course_comboBox.setSizePolicy(sizePolicy)
        self.course_comboBox.setObjectName("course_comboBox")
        # 连接的
        layout_widget2 = QtWidgets.QWidget(self.class_tab)
        layout_widget2.setGeometry(QtCore.QRect(40, 170, 471, 30))
        layout_widget2.setObjectName("layout_widget2")
        # 点击刷课-终止程序组合
        horizontalLayout = QtWidgets.QHBoxLayout(layout_widget2)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        horizontalLayout.setObjectName("horizontalLayout")

        # 点击刷课
        self.brush_Button = QtWidgets.QPushButton(layout_widget2)
        self.brush_Button.setText("点击刷课")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.brush_Button.sizePolicy().hasHeightForWidth())
        self.brush_Button.setSizePolicy(sizePolicy)
        self.brush_Button.setObjectName("brush_Button")
        horizontalLayout.addWidget(self.brush_Button)
        self.brush_Button.clicked.connect(
            lambda: self.brush_xxt(isface_radioButton.isChecked()))
        # 终止程序
        stop_Button = QtWidgets.QPushButton(layout_widget2)
        stop_Button.setText("终止程序")
        stop_Button.setObjectName("stop_Button")
        horizontalLayout.addWidget(stop_Button)
        stop_Button.clicked.connect(lambda: self.message_send('x程序终止'))

        label_details = QtWidgets.QLabel(self.class_tab)
        label_details.setText('输出详细信息')
        label_details.setGeometry(QtCore.QRect(40, 240, 101, 16))
        label_details.setObjectName("label_details")
        # 详细信息打印
        self.text_details = QtWidgets.QTextBrowser(self.class_tab)
        self.text_details.setGeometry(QtCore.QRect(40, 270, 381, 131))
        self.text_details.setObjectName("text_details")

    def tab2_ui(self):
        # 刷题页面
        # 提示
        label_tips = QtWidgets.QLabel(self.tab_2)
        label_tips.setText("此程序暂不可用，请待完善")
        label_tips.setGeometry(QtCore.QRect(40, 40, 211, 141))
        label_tips.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        label_tips.setObjectName("label_tips")


class XxtCourse(QThread):
    message_sign = pyqtSignal(object)
    details_sign = pyqtSignal(object)

    def __init__(self):
        super(XxtCourse, self).__init__()
        # self.action = None
        self.argument = ()

        self.wait_condition = QWaitCondition()  # 控制阻塞调用
        self.mutex = QMutex()  # 锁对象

    def run(self):
        self.mutex.lock()
        if self.argument[0] == 'login':
            self.configuration_program()
            self.login_chaoxing()
            self.switch_course1()
        elif self.argument[0] == 'brush':
            self.switch_course2()
            self.handle_lesson()
        self.mutex.unlock()

    def configuration_program(self):
        s = Service(executable_path=EXECUTABLE_PATH)
        # 无头浏览器配置（可选）
        edge_options = Options()
        if not self.argument[4]:
            edge_options.add_argument('--headless')
            edge_options.add_argument('--disable-gpu')
        if self.argument[3]:
            edge_options.add_argument('--mute-audio')
        # 规避监测（默认开启）
        edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        try:
            self.bro = webdriver.Edge(service=s, options=edge_options)
        except Exception as e:
            message = 'x驱动未正常启动，可能未安装驱动或驱动与浏览器版本不同\n' \
                      f'报错类型:{e.__class__}'
            self.message_sign.emit(message)

        # 隐式等待
        self.bro.implicitly_wait(WAIT_TIME)

    def login_chaoxing(self):
        url = 'https://passport2.chaoxing.com/login' \
              '?fid=&newversion=true&refer=https://i.chaoxing.com'
        self.bro.get(url)
        # 学习通登录
        if self.argument[1]:
            phone = self.bro.find_element(By.ID, 'phone')
            phone.send_keys(self.argument[1])
            password_to = self.bro.find_element(By.ID, 'pwd')
            password_to.send_keys(self.argument[2])
            self.bro.find_element(By.ID, 'loginBtn').click()
            sleep(0.5)
        else:
            self.message_sign.emit("o请扫码登录后点我确定")
            self.wait_condition.wait(self.mutex)

        if self.bro.title == "用户登录":
            self.message_sign.emit("x账号密码有误!!!")
            # self.__del__()
        
    def switch_course1(self):
        # sleep(1)
        try:
            self.bro.find_element(By.NAME, '课程').click()
        except exceptions.StaleElementReferenceException:
            self.bro.find_element(By.NAME, '课程').click()
        self.bro.switch_to.frame('frame_content')
        # [1]正常方式
        courses = self.bro.find_elements(By.XPATH, '/html/body/div/div/div/div[2]/div/div[2]/div[3]/div/div['
                                                   '2]/div/div[2]/h3/a/span')
        courses_list = []
        for c in courses:
            courses_list.append(c.text)
        self.message_sign.emit(courses_list)

    def switch_course2(self):
        if not self.argument[2]:
            course = self.bro.find_element(By.XPATH, f'//span[@title="{self.argument[1]}"]')
            self.bro.execute_script('arguments[0].click();', course)
        else:
            self.bro.get(self.argument[self.argument[1]])

        # 跳转课程页面
        self.bro.switch_to.window(self.bro.window_handles[-1])
        self.bro.find_element(By.LINK_TEXT, '章节').click()
        self.bro.switch_to.frame('frame_content-zj')
        # 筛选出 未完成任务点 的章节
        chapters = self.bro.find_elements(By.XPATH,
                                          f'//div[@class="catalog_task"]/input[@value]/../preceding-sibling::div[1]/a/span')
        # ！这里包括 课程找不到未完成的课程 和 未找到课程 两种情况，一概处理了
        if not chapters:
            self.message_sign.emit("x本门课好像已经学完了呢 ^o^")
            # quit()  # todo del方法有问题，换quit（）试试
            # self.__del__()
        else:
            self.chapter_numbers = []
            for chapter in chapters:
                self.chapter_numbers.append(chapter.text)
            self.bro.execute_script('arguments[0].click();', chapters[0])
            # chapter[0].click()  # 进入到指定章节课程中

    def handle_lesson(self):
        sleep(2)
        chapter_name = self.bro.find_element(By.XPATH, '//*[@id="mainid"]/div[5]/div').text
        self.details_sign.emit('开始刷课:' + chapter_name)

        # input('等待人脸识别通过')
        if self.bro.execute_script("return document.getElementsByClassName('maskDiv1')[0]"):
            self.bro.execute_script("document.getElementsByClassName('maskDiv1')[0].remove()")
            self.details_sign.emit('*人脸弹窗已清除')

        # 每章第一节首页可能是学习目标，需要切换到视频页,也可能没有标签页（案例:思想道德与法治）
        video_screen = self.bro.find_elements(By.XPATH, '/html/body/div[4]/div/div[3]/div[6]/ul/li[@title="视频"]')
        if video_screen:
            video_screen = video_screen[0]
            if video_screen.get_attribute("id") == 'dct2':
                video_screen.click()

        self.bro.switch_to.frame('iframe')
        # ans-attach-ct 表示未完成的
        video_divs = self.bro.find_elements(By.XPATH, '/html/body/div[2]/div//div[@class="ans-attach-ct"]')
        if len(video_divs) != 0:  # 如果视频都完成了就不进行操作
            for video_div in video_divs:
                video_frame = video_div.find_element(By.TAG_NAME, 'iframe')
                self.bro.switch_to.frame(video_frame)

                if self.bro.execute_script("return document.getElementsByClassName"
                                           "('x-container ans-timelineobjects x-container-default')[0]"):
                    self.bro.execute_script("document.getElementsByClassName"
                                            "('x-container ans-timelineobjects x-container-default')[0].remove()")
                    self.details_sign.emit('*课中测')
                if self.bro.execute_script("return document.getElementsByClassName"
                                           "('x-component ans-timelineobjectsbg x-component-default')[0]"):
                    self.bro.execute_script("document.getElementsByClassName"
                                            "('x-component ans-timelineobjectsbg x-component-default')[0].remove()")
                    self.details_sign.emit('验已清除')

                # 如果页面过长，需要先移到该元素位置，在进行后续操作
                self.bro.execute_script("arguments[0].scrollIntoView();", self.bro.find_element(By.TAG_NAME, 'body'))
                # 播放视频
                # 由于之前是按任务点来定位的，有可能定位到的不是视频而是题目之类的，所以要辨别跳过非视频
                play_button = self.bro.find_elements(By.XPATH, '//*[@id="video"]/button')
                if not play_button:
                    self.details_sign.emit('没找到视频欸')
                    self.bro.switch_to.parent_frame()
                    continue
                # sleep(3)

                play_button[0].click()
                # bro.execute_script('arguments[0].click();', play_button)  # 可能在不可见区域
                self.details_sign.emit("开始播放视频")
                sleep(2)

                # 倍数播放(三次点击切换到二倍速)
                # 先检测是否可以倍数播放
                is_multiply_rate = self.bro.find_elements(By.XPATH,
                                                          "//div[@class='vjs-playback-rate-value' and not(@style)]")
                if is_multiply_rate:
                    self.details_sign.emit('倍数播放')
                    rate_button = self.bro.find_element(By.XPATH, '//button[@title="播放速度"]')
                    self.bro.execute_script('arguments[0].click();', rate_button)
                    self.bro.execute_script('arguments[0].click();', rate_button)
                    self.bro.execute_script('arguments[0].click();', rate_button)

                # 计算视频用时 以调整睡眠时间
                while True:
                    sleep(2)
                    completed_duration = self.bro.find_element(By.XPATH,
                                                               '//*[@id="video"]/div[@class="vjs-control-bar"]/'
                                                               'div[2]/span[2]').get_attribute('textContent')
                    original_duration = self.bro.find_element(By.XPATH,
                                                              '//*[@id="video"]/div[@class="vjs-control-bar"]/'
                                                              'div[4]/span[2]').get_attribute('textContent')
                    completed_duration = int(completed_duration.split(':')[0]) * 60 + int(
                        completed_duration.split(':')[1])
                    original_duration = int(original_duration.split(':')[0]) * 60 + int(original_duration.split(':')[1])
                    # 这里只检查下总时长
                    if original_duration:
                        break

                self.details_sign.emit(f"原时长:{original_duration}s")
                actual_duration = int(original_duration - completed_duration)
                if is_multiply_rate:
                    actual_duration /= 2
                self.details_sign.emit(f"实际时长{actual_duration}s")

                # 睡眠，等待视频观看结束
                # classname = 'ans-attach-ct'  # 即未完成
                self.details_sign.emit('进入休眠，等待课程结束。')
                self._csleep(actual_duration)

                # 准备进行检查任务点
                self.bro.switch_to.parent_frame()
                while video_div.get_attribute('class') != "ans-attach-ct ans-job-finished":  # 阻塞操作!
                    self.details_sign.emit('等待中,每隔 10s检查一遍')
                    sleep(10)  # todo 因为出了节点，再检测不方便,不管了，这个漏洞留着了
                self.details_sign.emit(r"呼...刷完一节 \^o^/")

        self.bro.switch_to.parent_frame()
        # while True:
        #     th_chap_n = self.bro.find_element(By.XPATH, '//div[@class="posCatalog_select posCatalog_active"]/span/em')
        #     self.bro.execute_script("arguments[0].scrollIntoView();", th_chap_n)
        #     if th_chap_n.text:
        #         print(th_chap_n.text)
        #         break
        #     sleep(0.2)

        self.chapter_numbers.remove(self.chapter_numbers[0])
        if self.chapter_numbers:
            next_chapter = self.bro.find_elements(By.XPATH, f"//*[text()='{self.chapter_numbers[0]}']")
            self.bro.execute_script("arguments[0].scrollIntoView();", next_chapter[0])
            self.bro.execute_script('arguments[0].click();', next_chapter[0])
            # try:
            #     self.bro.execute_script('arguments[0].click();', next_chapter[0])
            # except:
            #     self.bro.execute_script("arguments[0].scrollIntoView();", next_chapter[0])
            #     next_chapter[0].click()
            # self.bro.execute_script('arguments[0].click();', next_chapter)
            self.handle_lesson()
        else:
            self.details_sign.emit('The course is over!')
            sleep(1)
        sleep(3)

    def _video_replay(self):
        """
        内函数，监测视频是否暂停并重新播放
        """
        video_button = self.bro.find_element(By.XPATH, '//*[@id="video"]/div[@class="vjs-control-bar"]/button')
        if video_button.get_attribute('class') == "vjs-play-control vjs-control vjs-button vjs-paused":
            video_button.click()

    def _csleep(self, secs):
        """
        原因:课中有弹窗问题，前方删除弹窗元素后课程仍会暂停一下
        方法:修改sleep方法为每分钟都进行一次监测视频是否中断并重新播放
        """
        self._video_replay()  # 只要调用不论是否超过一分钟都进行一次判断，避免未知情况
        min = int(secs / 60) + 1
        for i in range(min):
            sleep(60)
            self._video_replay()


# todo
#   一开始没刷脸的课程继续刷时就会报错，不容易看出来问题，我选择不提示
#   课程限制了每天的刷课数量，弹出时也会报错，怎么检测提醒一下，没这课不用管


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = UiTabWidget()
    demo.main()
    # 退出
    sys.exit(app.exec_())

# pyinstaller -F -w-i ".\XXT_Gathering\favicon.ico" ".\XXT_Gathering\ui_ini.py" --clean
