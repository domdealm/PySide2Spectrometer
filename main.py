# MAIN

import sys
import os
import cv2
from cv2 import MARKER_CROSS
import numpy as np

from qt_core import *
from GUI.Window.Main.MainWindow import *
from App.GetRGBValue import *


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Espectrômetro")
        # Importando a janela:
        self.ui = MainWindow()
        self.ui.setup_UI(self)
        
        # Índice atual
        self.CurrPage = 0

        # Definições OpenCV
        self.CamID = 0
        self.VideoSize = QSize(640,480)
        self.font = cv2.FONT_HERSHEY_COMPLEX
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
        self.ui.UiPages.CamList2.currentIndexChanged.connect(self.CamRelease2)
        self.ui.UiPages.PixRowSlider.valueChanged.connect(self.PREditUpdater)
        self.ui.UiPages.PixelRowEdit.textChanged.connect(self.LEUpdater)
        self.ui.UiPages.CamSnap.clicked.connect(self.debugCallback)
        self.ui.HomeButton.clicked.connect(self.PAGE0)
        self.ui.ConfigCam.clicked.connect(self.PAGE1)
        self.ui.ConfigGraph.clicked.connect(self.PAGE2)
        self.ui.UiPages.Calibrate.clicked.connect(self.CalEnable)
        self.ui.UiPages.ToggleCursor.clicked.connect(self.CursorEnable)
        self.ui.UiPages.ApplyCal.clicked.connect(self.ApplyCal)
        self.ui.UiPages.ApplyIPCAM.clicked.connect(self.AppendCam)

        # Criando a escala + calibração:
        # [ (X,Y pixeis),(X,Y nanometros)]
        self.CalPoints = [(0,640),(780,380)]
        self.PixRange = abs(self.CalPoints[0][0] - self.CalPoints[0][1])
        self.NMRange = abs(self.CalPoints[1][0] - self.CalPoints[1][1])
        self.scaleZero = 38
        self.ScaleZeroVal = 380

        # Mostrar a janela:
        self.show()
    
    def VideoLabel(self):
        # Feed da Webcam:
        ret, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self.ui.UiPages.ImgFlip.isChecked():
            frame1 = cv2.flip(frame, 1)
            frame = cv2.flip(frame,1)
        else:
            ret,frame1 = self.capture.read()  #Frame1 é o que é exibido
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        # Desenhando Linha antes de dar o resize:
        self.RowCursor = self.ui.UiPages.PixRowSlider.value()
        cv2.line(frame1,(0,self.RowCursor),(640,self.RowCursor),(0,0,0),3)
        cv2.line(frame1,(0,self.RowCursor),(640,self.RowCursor),(255,255,255))

        # Gráfico:
        
        # Criando uma imagem vazia
        graph = np.zeros([300,720,3],dtype=np.uint8)
        graph.fill(255) # Preenchendo com branco
        bw =  cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)

        _,cols = bw.shape
        self.intensity = [0]*640
        # Desenhando a escala do gráfico (primeiras linhas):
        cv2.line(graph,(28,273),(688,273),(0,0,0),1)
        cv2.line(graph,(37,281),(37,13),(0,0,0),1)

        # Grade
        cv2.line(graph,(28,209),(684,209),(10,10,10),1)
        cv2.line(graph,(28,146),(684,146),(10,10,10),1)
        cv2.line(graph,(28,78),(684,78),(10,10,10),1)
        cv2.line(graph,(28,17),(684,17),(10,10,10),1)
        
        cv2.putText(graph,"0",(26,267),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"0.25",(10,206),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"0.5",(16,143),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"0.75",(10,75),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"1",(26,14),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)

        # Criando a lista contendo os valores de intensidade
        for i in range(cols):
                data = bw[self.RowCursor,i]
                self.intensity[i] = data
        
        # Laço que vai preencher a imagem
        index = 0
        self.wavelengthdata = []

        for i in self.intensity:
            wavelength = self.ScaleZeroVal+(index/(self.PixRange/self.NMRange))
            wavelengthdata = round(wavelength,1)
            wavelength = round(wavelength)
            self.wavelengthdata.append(wavelengthdata)
            rgb= wavelength_to_rgb(wavelength)
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            cv2.line(graph, (self.scaleZero+index,272), (self.scaleZero+index,272-i), (r,g,b), 1)
            #cv2.line(graph, (index,253-i), (index,255-i), (0,0,0), 1,cv2.LINE_AA)
            index += 1
        
        GraphLabel = QImage(graph, graph.shape[1], graph.shape[0],graph.strides[0], QImage.Format_RGB888)
        

        # Calibração

        FPCursor = self.ui.UiPages.FirstPoint.value() + self.scaleZero
        SPCursor = self.ui.UiPages.SecondPoint.value() + self.scaleZero
        MWCursor = self.ui.UiPages.AdCursor.value() + self.scaleZero
        if self.ui.UiPages.Calibrate.isChecked():
            cv2.line(graph,(FPCursor,0),(FPCursor,290),(0,0,0),1)
            cv2.line(graph,(SPCursor,0),(SPCursor,290),(0,0,0),1)
        if self.ui.UiPages.ToggleCursor.isChecked():
            cv2.drawMarker(graph,(MWCursor,(260-self.intensity[self.ui.UiPages.AdCursor.value()])),(0,0,0),MARKER_CROSS,10,3)
            cv2.drawMarker(graph,(MWCursor,(260-self.intensity[self.ui.UiPages.AdCursor.value()])),(255,255,255),MARKER_CROSS,10,1)
        # Exibição:

        # Primeira Página:
        if self.CurrPage == 0:
            resizedFrame = cv2.resize(frame1,(320,240))
            image = QImage(resizedFrame, resizedFrame.shape[1], resizedFrame.shape[0],resizedFrame.strides[0], QImage.Format_RGB888)
            self.ui.UiPages.LiveFeed.setPixmap(QPixmap.fromImage(image))
            self.ui.UiPages.LiveGraph.setPixmap(QPixmap.fromImage(GraphLabel))
        
        # Segunda Página:
        elif self.CurrPage == 1:
            resizedFrame = cv2.resize(frame1,(400,300))
            image = QImage(resizedFrame, resizedFrame.shape[1], resizedFrame.shape[0],resizedFrame.strides[0], QImage.Format_RGB888)
            self.ui.UiPages.CamFeed.setPixmap(QPixmap.fromImage(image))
        
        # Terceira Página:
        elif self.CurrPage == 2:
            self.ui.UiPages.LiveGraph_2.setPixmap(QPixmap.fromImage(GraphLabel))


    
    def CamRelease(self):
        self.capture.release()
        self.capture = cv2.VideoCapture(self.ui.UiPages.List[self.ui.UiPages.CamList.currentIndex()])
    def CamRelease2(self):
        print("oi")
        self.capture.release()
        self.capture = cv2.VideoCapture(self.ui.UiPages.List[self.ui.UiPages.CamList2.currentIndex()])
    
    def PREditUpdater(self):
        self.ui.UiPages.PixelRowEdit.setText(str(self.ui.UiPages.PixRowSlider.value()))
    def LEUpdater(self):
        self.ui.UiPages.PixRowSlider.setValue(int(self.ui.UiPages.PixelRowEdit.text()))
    
    

    def PAGE0(self):
        self.ui.pages.setCurrentWidget(self.ui.UiPages.page)
        self.CurrPage = 0
    def PAGE1(self):
        self.ui.pages.setCurrentWidget(self.ui.UiPages.page_2)
        self.CurrPage = 1
    def PAGE2(self):
        self.ui.pages.setCurrentWidget(self.ui.UiPages.page_3)
        self.CurrPage = 2

    def CalEnable(self):
        if self.ui.UiPages.Calibrate.isChecked():
            self.ui.UiPages.FirstPoint.setEnabled(True)
            self.ui.UiPages.SecondPoint.setEnabled(True)            

        else:
            self.ui.UiPages.FirstPoint.setEnabled(False)
            self.ui.UiPages.SecondPoint.setEnabled(False)
    
    def CursorEnable(self):
        if self.ui.UiPages.ToggleCursor.isChecked():
            self.ui.UiPages.AdCursor.setEnabled(True)
            self.ui.UiPages.ToggleNM.setEnabled(True)
            self.ui.UiPages.ToggleAmp.setEnabled(True)

        else:
            self.ui.UiPages.AdCursor.setEnabled(False)
            self.ui.UiPages.ToggleNM.setEnabled(False)
            self.ui.UiPages.ToggleNM.setChecked(False)
            self.ui.UiPages.ToggleAmp.setChecked(False)
    
    def ApplyCal(self):
        CalA = (self.ui.UiPages.FirstPoint.value(),self.ui.UiPages.SecondPoint.value())
        CalB = (self.ui.UiPages.SPWL.value(),self.ui.UiPages.FPWL.value())
        self.CalPoints = [CalA,CalB]
        self.PixRange = abs(self.CalPoints[0][0] - self.CalPoints[0][1])
        self.NMRange = abs(self.CalPoints[1][0] - self.CalPoints[1][1])
        self.ScaleZeroVal = (self.ui.UiPages.FPWL.value() - (self.ui.UiPages.FirstPoint.value()/(self.PixRange/self.NMRange)))
        
    def AppendCam(self):
        cap = cv2.VideoCapture(self.ui.UiPages.IPCAM.text())
        if cap.read()[0]:
            index = 0
            self.ui.UiPages.List.append(self.ui.UiPages.IPCAM.text())
            self.ui.UiPages.CamList.addItem(f"IPCam {index}")
            self.ui.UiPages.CamList2.addItem(f"IPCam {index}")
            index += 1
        else:
            error = QErrorMessage()
            error.showMessage("Não foi possível adicionar a câmera, certifique-se que o link está correto.")
            error.exec()



    def debugCallback(self):
        print(self.CalPoints)
        print("Px/nm = ",self.PixRange/self.NMRange)
        print("Nm/Px = ",self.NMRange/self.PixRange)
        print("Valor Cursor: ",self.intensity[self.ui.UiPages.AdCursor.value()])
        print("Nm Cursor: ",self.ScaleZeroVal+(self.ui.UiPages.AdCursor.value()/(self.PixRange/self.NMRange)))
        print("Pixel do cursor: ",self.ui.UiPages.AdCursor.value()+self.scaleZero)
        print(self.ui.UiPages.List)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_Window()
    sys.exit(app.exec_())
