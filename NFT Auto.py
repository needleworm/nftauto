"""
NFT AUTO
with GUI
Byunghyun Ban
https://github.com/needleworm
"""

import sys
from PyQt6 import QtGui
from PyQt6 import QtWidgets as Q
from PyQt6 import QtCore as QT
import time
from PIL import Image, ImageQt
import numpy as np
from ui import Ui_MainWindow
import os
import platform

ui_class = Ui_MainWindow


def resize_to_qpixmap(img, xdim, ydim):
    img = img.convert("RGB").resize((xdim, ydim))
    qim = ImageQt.ImageQt(img)
    qm = QtGui.QPixmap.fromImage(qim)
    return qm


def draw_from_layers(layer_list):
    canvas = layer_list[0].copy()
    if canvas.mode != "RGBA":
        canvas = canvas.convert("RGBA")
    xdim, ydim = canvas.size
    layer_list = layer_list[1:]
    for layer in layer_list:
        if layer == "":
            continue
        if layer.mode != "RGBA":
            continue
        x, y = layer.size
        if x != xdim or y != ydim:
            layer = layer.resize((xdim, ydim))
        canvas = Image.alpha_composite(canvas, layer)

    return canvas


class PixelRandomizer(QT.QThread):
    progress_out = QT.pyqtSignal(int)
    image_out = QT.pyqtSignal(Q.QGraphicsScene)

    def __init__(self):
        super().__init__()
        self.scene = Q.QGraphicsScene()
        a, b, c, _, e = time.ctime().split(" ")
        self.out_dir = '[Color Shuffle]' + " ".join([e, b, c, a])

    def run_process(self, image_file, sensitivity, xdim, ydim, isMac):
        self.progress_out.emit(0)
        if not isMac:
            if self.out_dir not in os.listdir():
                os.mkdir(self.out_dir)
        else:
            if self.out_dir not in os.listdir("../../.."):
                self.out_dir = "../../../" + self.out_dir    
                os.mkdir(self.out_dir)
            else:
                self.out_dir = "../../../" + self.out_dir

        origin_filename = image_file.split("/")[-1].split(".")[0].strip()
        i_file = Image.open(image_file)
        x, y = i_file.size
        if x / xdim > y / ydim:
            new_x = xdim
            new_y = int(y / x * xdim)
        else:
            new_y = ydim
            new_x = int(x / y * ydim)

        img = np.asarray(i_file)
        i_file.close()

        x, y, c = img.shape
        steps = int(9 + (sensitivity - 50) / 10)
        total_progress = float(steps ** 3)
        count = 0
        for w in range(steps):
            for q in range(steps):
                for i in range(steps):
                    canvas = np.zeros_like(img)
                    for j in range(x):
                        for k in range(y):
                            c = img[j, k]
                            c[0] += w * 255 / steps
                            c[1] += q * 255 / steps
                            c[2] += i * 255 / steps
                            c[:3] %= 255
                            canvas[j, k] = c

                    count += 1
                    progress = int(count / total_progress * 100)
                    self.progress_out.emit(progress)

                    # 저장
                    rndimage = Image.fromarray(canvas)
                    filename = self.out_dir + "/" + origin_filename + " #" + str(count) + ".png"
                    rndimage.save(filename)

                    # 화면 출력
                    self.scene.addPixmap(resize_to_qpixmap(rndimage, new_x, new_y))
                    self.image_out.emit(self.scene)
                    QtGui.QGuiApplication.processEvents()
        self.progress_out.emit(progress)
        QtGui.QGuiApplication.processEvents()
        return True


class LoadImage(QT.QThread):
    image_out = QT.pyqtSignal(Q.QGraphicsScene)

    def __init__(self):
        super().__init__()
        self.scene = Q.QGraphicsScene()

    def run_process(self, image_file, xdim, ydim):
        i_file = Image.open(image_file)
        x, y = i_file.size
        if x / xdim > y / ydim:
            new_x = xdim
            new_y = int(y / x * xdim)
        else:
            new_y = ydim
            new_x = int(x / y * ydim)

        self.scene.addPixmap(resize_to_qpixmap(i_file, new_x, new_y))
        i_file.close()
        self.image_out.emit(self.scene)

        QtGui.QGuiApplication.processEvents()


class LayerAugmentation(QT.QThread):
    progress_out = QT.pyqtSignal(int)
    image_out = QT.pyqtSignal(Q.QGraphicsScene)

    def __init__(self):
        super().__init__()
        self.scene = Q.QGraphicsScene()
        a, b, c, _, e = time.ctime().split(" ")
        self.out_dir = '[Layer Augment]' + " ".join([e, b, c, a])

    def run_process(self, layers, xdim, ydim, isMac):
        self.progress_out.emit(0)
        if not isMac:
            if self.out_dir not in os.listdir():
                os.mkdir(self.out_dir)
        else:
            if self.out_dir not in os.listdir("../../.."):
                self.out_dir = "../../../" + self.out_dir    
                os.mkdir(self.out_dir)
            else:
                self.out_dir = "../../../" + self.out_dir

        files = []
        for el in layers:
            file = []
            for f in os.listdir(el):
                if f.split(".")[-1] in "png PNG":
                    file.append(el + "/" + f)
            files.append(file)

        files = files + [[""] for i in range(10 - len(files))]
        total_progress = 1
        for el in files:
            total_progress *= len(el)
        new_x = 0
        new_y = 0

        count = 0
        for l0 in files[0]:
            if l0 == "":
                c0 = ""
            else:
                c0 = Image.open(l0)
            for l1 in files[1]:
                if l1 == "":
                    c1 = ""
                else:
                    c1 = Image.open(l1)
                for l2 in files[2]:
                    if l2 == "":
                        c2 = ""
                    else:
                        c2 = Image.open(l2)
                    for l3 in files[3]:
                        if l3 == "":
                            c3 = ""
                        else:
                            c3 = Image.open(l3)
                        for l4 in files[4]:
                            if l4 == "":
                                c4 = ""
                            else:
                                c4 = Image.open(l4)
                            for l5 in files[5]:
                                if l5 == "":
                                    c5 = ""
                                else:
                                    c5 = Image.open(l5)
                                for l6 in files[6]:
                                    if l6 == "":
                                        c6 = ""
                                    else:
                                        c6 = Image.open(l6)
                                    for l7 in files[7]:
                                        if l7 == "":
                                            c7 = ""
                                        else:
                                            c7 = Image.open(l7)
                                        for l8 in files[8]:
                                            if l8 == "":
                                                c8 = ""
                                            else:
                                                c8 = Image.open(l8)
                                            for l9 in files[9]:
                                                if l9 == "":
                                                    c9 = ""
                                                else:
                                                    c9 = Image.open(l9)
                                                canvas = draw_from_layers((c0, c1, c2, c3, c4, c5, c6, c7, c8, c9))

                                                if type(c9) != str:
                                                    c9.close()

                                                count += 1
                                                progress = int(count / total_progress * 100)
                                                self.progress_out.emit(progress)

                                                # 저장
                                                filename = self.out_dir + "/# " + str(count) + ".png"
                                                canvas.save(filename)

                                                if new_x == 0:
                                                    x, y = canvas.size
                                                    if x / xdim > y / ydim:
                                                        new_x = xdim
                                                        new_y = int(y / x * xdim)
                                                    else:
                                                        new_y = ydim
                                                        new_x = int(x / y * ydim)

                                                # 화면 출력
                                                self.scene.addPixmap(resize_to_qpixmap(canvas, new_x, new_y))
                                                self.image_out.emit(self.scene)
                                                QtGui.QGuiApplication.processEvents()

                                            if type(c8) != str:
                                                c8.close()
                                        if type(c7) != str:
                                            c7.close()
                                    if type(c6) != str:
                                        c6.close()
                                if type(c5) != str:
                                    c5.close()
                            if type(c4) != str:
                                c4.close()
                        if type(c3) != str:
                            c3.close()
                    if type(c2) != str:
                        c2.close()
                if type(c2) != str:
                    c1.close()
            if type(c0) != str:
                c0.close()

        QtGui.QGuiApplication.processEvents()
        return True


class WindowClass(Q.QMainWindow, ui_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.isMac = False
        if platform.system() == "Darwin":
            self.isMac = True
        
        self.basedir = "./"
        if self.isMac:
            self.basedir = "../../../"

        """
        # tab 1 컴포넌트들
            # input
            self.imageFileField_1   # 이미지 파일 경로          # QLineEdit
            self.getFile_1          # 탐색 버튼                # QToolButton
            self.slider             # 슬라이더                 # QSlider
            self.startButton_1      # 생성 시작 버튼            # QPushButton 
            
            # output
            self.imageOut_1         # 생성된 이미지 보여줌       # QGraphicsView
            self.progressBar_1      # 작업 진행 정도 보여줌      # QProgressBar
        """

        # Tab 1 구현
        self.doing_job_1 = False
        self.screen_height_1 = self.imageOut_1.size().height()
        self.screen_width_1 = self.imageOut_1.size().width()
        self.imageFile = ""
        self.worker_1 = PixelRandomizer()
        self.worker_2 = LoadImage()
        self.startButton_1.clicked.connect(self.pixel_randomizer)
        self.getFile_1.clicked.connect(self.get_image_file_1)

        """
        # tab 2 컴포넌트들
            # input
            self.layer_1            # 레이어 1번                # QLineEdit
            ...                     ...
            self.layer_10           # 레이어 10번               # QLineEdit
            self.getDir_1           # 탐색기 버튼 1번           # QToolButton
            ...                     ...
            self.getDir_10          # 탐색기 버튼 10번          # QToolButton
            self.startButton_2      # 시작 버튼                 # QPushButton

            # output
            self.imageOut_2         # 이미지 출력               # QGraphicsView
            self.progressBar_2      # 작업 진행 정도 보여줌      # QProgressBar
        """
        # Tab 2 구현
        self.doing_job_2 = False
        self.screen_height_2 = self.imageOut_2.size().height()
        self.screen_width_2 = self.imageOut_2.size().width()

        self.worker_3 = LayerAugmentation()
        self.startButton_2.clicked.connect(self.layer_augmentation)

        self.layer_dirs = ["" for i in range(10)]

        self.getDir_1.clicked.connect(self.get_layer_directory_1)
        self.getDir_2.clicked.connect(self.get_layer_directory_2)
        self.getDir_3.clicked.connect(self.get_layer_directory_3)
        self.getDir_4.clicked.connect(self.get_layer_directory_4)
        self.getDir_5.clicked.connect(self.get_layer_directory_5)
        self.getDir_6.clicked.connect(self.get_layer_directory_6)
        self.getDir_7.clicked.connect(self.get_layer_directory_7)
        self.getDir_8.clicked.connect(self.get_layer_directory_8)
        self.getDir_9.clicked.connect(self.get_layer_directory_9)
        self.getDir_10.clicked.connect(self.get_layer_directory_10)

    def layer_augmentation(self):
        layers = []
        for el in self.layer_dirs:
            if el != "":
                layers.append(el)

        if len(layers) < 2:
            return

        self.doing_job_2 = not self.doing_job_2
        if self.doing_job_2:
            self.startButton_2.setText("Processing..")
        else:
            self.startButton_2.setText("Start")

        # 멀티스레드로 작업
        self.worker_3.image_out.connect(self.imageOut_2.setScene)
        self.worker_3.progress_out.connect(self.progressBar_2.setValue)
        self.doing_job_2 = not self.worker_3.run_process(layers,
                                                         self.screen_width_2,
                                                         self.screen_height_2,
                                                         self.isMac)
        if self.doing_job_2:
            self.startButton_2.setText("Processing..")
        else:
            self.startButton_2.setText("Start")
        QtGui.QGuiApplication.processEvents()

    def pixel_randomizer(self):
        if len(self.imageFile) < 5:
            return

        self.doing_job_1 = not self.doing_job_1
        if self.doing_job_1:
            self.startButton_1.setText("Processing..")
        else:
            self.startButton_1.setText("Start")

        # 멀티스레드로 작업
        self.worker_1.image_out.connect(self.imageOut_1.setScene)
        self.worker_1.progress_out.connect(self.progressBar_1.setValue)
        self.doing_job_1 = not self.worker_1.run_process(self.imageFile,
                                                         float(self.slider.value()),
                                                         self.screen_width_1,
                                                         self.screen_height_1,
                                                         self.isMac)
        if self.doing_job_1:
            self.startButton_1.setText("Processing..")
        else:
            self.startButton_1.setText("Start")
        QtGui.QGuiApplication.processEvents()

    def get_image_file_1(self):
        getFile = Q.QFileDialog.getOpenFileName(self,
                                                "Select Source Image",
                                                self.basedir,
                                                filter="Images (*.png *.jpg *.jpeg)")
        self.imageFile = getFile[0]
        self.progressBar_1.setValue(0)
        self.imageFileField_1.setText(self.imageFile)
        self.worker_2.image_out.connect(self.imageOut_1.setScene)
        self.worker_2.run_process(self.imageFile, self.screen_width_1, self.screen_height_1)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_1(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 1",
                                                    self.basedir, 
                                                    )
        self.layer_dirs[0] = getDir
        self.layer_1.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_2(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 2",
                                                    self.basedir
                                                    )
        self.layer_dirs[1] = getDir
        self.layer_2.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_3(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 3",
                                                    self.basedir
                                                    )
        self.layer_dirs[2] = getDir
        self.layer_3.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_4(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 4",
                                                    self.basedir
                                                    )
        self.layer_dirs[3] = getDir
        self.layer_4.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_5(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 5",
                                                    self.basedir
                                                    )
        self.layer_dirs[4] = getDir
        self.layer_5.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_6(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 6",
                                                    self.basedir
                                                    )
        self.layer_dirs[5] = getDir
        self.layer_6.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_7(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 7",
                                                    self.basedir
                                                    )
        self.layer_dirs[6] = getDir
        self.layer_7.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_8(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 8",
                                                    self.basedir
                                                    )
        self.layer_dirs[7] = getDir
        self.layer_8.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_9(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 9",
                                                    self.basedir
                                                    )
        self.layer_dirs[8] = getDir
        self.layer_9.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()

    def get_layer_directory_10(self):
        getDir = Q.QFileDialog.getExistingDirectory(self,
                                                    "Select Directory for Layer 10",
                                                    self.basedir
                                                    )
        self.layer_dirs[9] = getDir
        self.layer_10.setText(getDir)
        self.progressBar_2.setValue(0)
        QtGui.QGuiApplication.processEvents()


if __name__ == "__main__":
    app = Q.QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec()
    sys.exit(app.exec)
