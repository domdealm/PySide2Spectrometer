# MAIN

import sys
import os
import numpy as np

from qt_core import *
from GUI.Window.Main.MainWindow import *
from App.GetStream import *


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Espectrômetro - domdealm")
        # Importando a janela:
        self.ui = MainWindow()
        self.ui.setup_UI(self)
        # Teste Atualizar OpenCV
        self.CamID = 0
        self.VideoSize = QSize(640,480)
        #self.PixelRow = 241
        
        # Inicializando o OpenCV:
        self.capture = cv2.VideoCapture(self.CamID)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.VideoSize.width())
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.VideoSize.height())

        # Criando o timer que vai atualizar as imagens:
        self.timer = QTimer()
        self.timer.timeout.connect(self.VideoLabel)
        self.timer.start(60)

        # Conexões e sinais:
        self.ui.UiPages.CamList.currentIndexChanged.connect(self.CamRelease)
        self.ui.UiPages.PixRowSlider.valueChanged.connect(self.PREditUpdater)
        self.ui.UiPages.PixelRowEdit.textChanged.connect(self.LEUpdater)
        self.ui.HomeButton.clicked.connect(self.PAGE0)
        self.ui.ConfigCam.clicked.connect(self.PAGE1)
        self.ui.ConfigGraph.clicked.connect(self.PAGE2)

        # Criando a escala + calibração:
        # [ (X,Y pixeis),(X,Y nanometros)]
        self.CalPoints = [(0,640),(750,380)]
        self.PixRange = abs(self.CalPoints[0][0] - self.CalPoints[0][1])
        self.NMRange = abs(self.CalPoints[1][0] - self.CalPoints[1][1])

        # Mostrar a janela:
        self.show()
    
    def VideoLabel(self):
        # Feed da Webcam:
        ret, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame1 = cv2.flip(frame, 1)
        frame = cv2.flip(frame,1)

        # Desenhando Linha antes de dar o resize:
        self.RowCursor = self.ui.UiPages.PixRowSlider.value()
        cv2.line(frame1,(0,self.RowCursor),(640,self.RowCursor),(0,0,0),3)
        cv2.line(frame1,(0,self.RowCursor),(640,self.RowCursor),(255,255,255))

        resizedFrame = cv2.resize(frame1,(320,240))
        image = QImage(resizedFrame, resizedFrame.shape[1], resizedFrame.shape[0],resizedFrame.strides[0], QImage.Format_RGB888)
        self.ui.UiPages.LiveFeed.setPixmap(QPixmap.fromImage(image))

        # Gráfico:
        
        # Criando uma imagem vazia
        graph = np.zeros([290,700,3],dtype=np.uint8)
        graph.fill(255) # Preenchendo com branco
        bw =  cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)

        _,cols = bw.shape
        intensity = [0]*640
        
        # Criando a lista contendo os valores de intensidade
        for i in range(cols):
                data = bw[self.RowCursor,i]
                intensity[i] = data
        
        # Laço que vai preencher a imagem
        index = 30
        self.wavelengthdata = []

        for i in intensity:
            wavelength = (380+(index/(self.PixRange/self.NMRange)))
            wavelengthdata = round(wavelength,1)
            wavelength = round(wavelength)
            self.wavelengthdata.append(wavelengthdata)
            rgb=self.wavelength_to_rgb(wavelength)
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            cv2.line(graph, (index,265), (index,265-i), (r,g,b), 1)
            cv2.line(graph, (index,264-i), (index,265-i), (0,0,0), 1,cv2.LINE_AA)
            index += 1
        
        GraphLabel = QImage(graph, graph.shape[1], graph.shape[0],graph.strides[0], QImage.Format_RGB888)
        self.ui.UiPages.LiveGraph.setPixmap(QPixmap.fromImage(GraphLabel))

    def returnCameraIndexes(self):
    # checks the first 10 indexes.
        index = 0
        arr = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
            index += 1
            i -= 1
        self.List = arr
        for i in range(self.List):
            self.ui.UiPages.CamList.addItem(f"Camera {i}")
    
    def CamRelease(self):
        self.capture.release()
        self.capture = cv2.VideoCapture(self.ui.UiPages.List[self.ui.UiPages.CamList.currentIndex()])
    
    def PREditUpdater(self):
        self.ui.UiPages.PixelRowEdit.setText(str(self.ui.UiPages.PixRowSlider.value()))
    def LEUpdater(self):
        self.ui.UiPages.PixRowSlider.setValue(int(self.ui.UiPages.PixelRowEdit.text()))
    
    # Convertendo comprimento de onda para RGB
    def wavelength_to_rgb(self,nm):
        # from: https://www.codedrome.com/exploring-the-visible-spectrum-in-python/
        # returns RGB vals for a given wavelength
        gamma = 0.8
        max_intensity = 255
        factor = 0

        rgb = {"R": 0, "G": 0, "B": 0}

        if 380 <= nm <= 439:
            rgb["R"] = -(nm - 440) / (440 - 380)
            rgb["G"] = 0.0
            rgb["B"] = 1.0
        elif 440 <= nm <= 489:
            rgb["R"] = 0.0
            rgb["G"] = (nm - 440) / (490 - 440)
            rgb["B"] = 1.0
        elif 490 <= nm <= 509:
            rgb["R"] = 0.0
            rgb["G"] = 1.0
            rgb["B"] = -(nm - 510) / (510 - 490)
        elif 510 <= nm <= 579:
            rgb["R"] = (nm - 510) / (580 - 510)
            rgb["G"] = 1.0
            rgb["B"] = 0.0
        elif 580 <= nm <= 644:
            rgb["R"] = 1.0
            rgb["G"] = -(nm - 645) / (645 - 580)
            rgb["B"] = 0.0
        elif 645 <= nm <= 780:
            rgb["R"] = 1.0
            rgb["G"] = 0.0
            rgb["B"] = 0.0

        if 380 <= nm <= 419:
            factor = 0.3 + 0.7 * (nm - 380) / (420 - 380)
        elif 420 <= nm <= 700:
            factor = 1.0
        elif 701 <= nm <= 780:
            factor = 0.3 + 0.7 * (780 - nm) / (780 - 700)

        if rgb["R"] > 0:
            rgb["R"] = int(max_intensity * ((rgb["R"] * factor) ** gamma))
        else:
            rgb["R"] = 0

        if rgb["G"] > 0:
            rgb["G"] = int(max_intensity * ((rgb["G"] * factor) ** gamma))
        else:
            rgb["G"] = 0

        if rgb["B"] > 0:
            rgb["B"] = int(max_intensity * ((rgb["B"] * factor) ** gamma))
        else:
            rgb["B"] = 0

        return (rgb["R"], rgb["G"], rgb["B"])

    def PAGE0(self):
        self.ui.pages.setCurrentWidget(self.ui.UiPages.page)
    def PAGE1(self):
        self.ui.pages.setCurrentWidget(self.ui.UiPages.page_2)
    def PAGE2(self):
        self.ui.pages.setCurrentWidget(self.ui.UiPages.page_3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_Window()
    sys.exit(app.exec_()) #PySide2
    #sys.exit(app.exec())
