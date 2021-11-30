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
        
        # Flags
        self.CurrPage = 0
        self.IsCropped = False
        self.ChannelSplit = 1

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
        self.ui.UiPages.CamSlide2.valueChanged.connect(self.PREditUpdater2)
        self.ui.UiPages.PixelRowEdit.textChanged.connect(self.LEUpdater)
        self.ui.UiPages.CamSnap.clicked.connect(self.SnapShot)
        self.ui.HomeButton.clicked.connect(self.PAGE0)
        self.ui.ConfigCam.clicked.connect(self.PAGE1)
        self.ui.ConfigGraph.clicked.connect(self.PAGE2)
        self.ui.UiPages.Calibrate.clicked.connect(self.CalEnable)
        self.ui.UiPages.ToggleCursor.clicked.connect(self.CursorEnable)
        self.ui.UiPages.ApplyCal.clicked.connect(self.ApplyCal)
        self.ui.UiPages.ApplyIPCAM.clicked.connect(self.AppendCam)
        self.ui.UiPages.GraphCSV.clicked.connect(self.GenCSV)
        self.ui.UiPages.GraphSnap.clicked.connect(self.SnapGraph)
        self.ui.UiPages.CropConEnable.clicked.connect(self.CropCons)
        self.ui.UiPages.ApplyCrop.clicked.connect(self.ApplyCrop)
        self.ui.UiPages.RevertCrop.clicked.connect(self.UndoCrop)
        self.ui.UiPages.KeepRatio.clicked.connect(self.AspectRatio)
        self.ui.UiPages.SpecMethod.currentIndexChanged.connect(self.SpecMethod)

        # Criando a escala + calibração:
        # [ (X,Y pixeis),(X,Y nanometros)]
        self.CalPoints = [(0,640),(780,380)]
        self.PixRange = abs(self.CalPoints[0][0] - self.CalPoints[0][1])
        self.NMRange = abs(self.CalPoints[1][0] - self.CalPoints[1][1])
        self.scaleZero = 38
        self.ScaleZeroVal = 380
        self.nanometers = [0]*640
        self.nanometersINT = [0]*640
        for i in range(640):
            self.nanometers[i] = self.ScaleZeroVal+(i/(self.PixRange/self.NMRange))
            self.nanometersINT[i] = int(self.ScaleZeroVal+(i/(self.PixRange/self.NMRange)))

        # Mostrar a janela:
        self.show()
    
    def VideoLabel(self):
        # Feed da Webcam:
        ret, capt = self.capture.read()

        if self.IsCropped:
            crop = capt[self.y1:self.y2,self.x1:self.x2]
            crop = cv2.resize(crop,(640,480))
            frame = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            frame1 = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        else:
            frame = cv2.cvtColor(capt, cv2.COLOR_BGR2RGB)
            frame1 = cv2.cvtColor(capt, cv2.COLOR_BGR2RGB)
        
        if self.ui.UiPages.ImgFlip.isChecked():
            frame1 = cv2.flip(frame, 1)
            frame = cv2.flip(frame,1)
        #else:
            #ret,frame1 = self.capture.read()  #Frame1 é o que é exibido
            #frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            

        # Desenhando Linha antes de dar o resize:
        self.RowCursor = self.ui.UiPages.PixRowSlider.value()
        cv2.line(frame1,(0,self.RowCursor),(640,self.RowCursor),(0,0,0),3)
        cv2.line(frame1,(0,self.RowCursor),(640,self.RowCursor),(255,255,255))

        # Gráfico:
        
        # Criando uma imagem vazia
        graph = np.zeros([300,720,3],dtype=np.uint8)
        graph.fill(255) # Preenchendo com branco

        if self.ChannelSplit ==1:
            bw =  cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
        else:
            bw = np.mean(frame,axis=2).astype(int)

        _,cols = bw.shape
        self.intensity = [0]*640

        # Grade
        # X
        cv2.line(graph,(28,209),(678,209),(155,155,155),1)
        cv2.line(graph,(28,146),(678,146),(155,155,155),1)
        cv2.line(graph,(28,78),(678,78),(155,155,155),1)
        cv2.line(graph,(28,17),(678,17),(155,155,155),1)
        # Y
        cv2.line(graph,(166,276),(166,17),(155,155,155),1)
        cv2.line(graph,(294,276),(294,17),(155,155,155),1)
        cv2.line(graph,(422,276),(422,17),(155,155,155),1)
        cv2.line(graph,(550,276),(550,17),(155,155,155),1)
        cv2.line(graph,(678,276),(678,17),(155,155,155),1)

        # Desenhando a escala do gráfico:
        cv2.line(graph,(28,273),(688,273),(0,0,0),1)
        cv2.line(graph,(37,281),(37,13),(0,0,0),1)
        

        # Eixo Y
        cv2.putText(graph,"0",(26,267),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"0.25",(10,206),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"0.5",(16,143),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"0.75",(10,75),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,"1",(26,14),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)

        # Eixo X
        cv2.putText(graph,str(self.nanometersINT[127])+'nm',(155,292),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,str(self.nanometersINT[255])+'nm',(285,292),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,str(self.nanometersINT[382])+'nm',(411,292),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,str(self.nanometersINT[511])+'nm',(538,292),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(graph,str(self.nanometersINT[639])+'nm',(666,292),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,0),1,cv2.LINE_AA)

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

        # Arquivos para Fotos:
        self.graphic = graph
        self.Frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        

        # Calibração

        FPCursor = self.ui.UiPages.FirstPoint.value() + self.scaleZero
        SPCursor = self.ui.UiPages.SecondPoint.value() + self.scaleZero
        MWCursor = self.ui.UiPages.AdCursor.value() + self.scaleZero
        if self.ui.UiPages.Calibrate.isChecked():
            cv2.line(graph,(FPCursor,0),(FPCursor,290),(0,0,0),1)
            cv2.line(graph,(SPCursor,0),(SPCursor,290),(0,0,0),1)
        
        # Recorte
        
        if self.ui.UiPages.CropConEnable.isChecked():
            if self.ui.UiPages.KeepRatio.isChecked():
                self.ui.UiPages.CropXEnd.setValue(self.ui.UiPages.CropXStart.value() + ((4/3)*\
                    self.ui.UiPages.CropYEnd.value()-self.ui.UiPages.CropYStart.value()))

            cv2.rectangle(frame1,(self.ui.UiPages.CropXStart.value(),self.ui.UiPages.CropYEnd.value()),\
                (self.ui.UiPages.CropXEnd.value(),self.ui.UiPages.CropYStart.value()),(255,140,0),1,cv2.LINE_AA)

        # Exibindo Cursor

        if self.ui.UiPages.ToggleCursor.isChecked():
            cv2.drawMarker(graph,(MWCursor,(272-self.intensity[self.ui.UiPages.AdCursor.value()])),(0,0,0),MARKER_CROSS,10,3)
            cv2.drawMarker(graph,(MWCursor,(272-self.intensity[self.ui.UiPages.AdCursor.value()])),(255,255,255),MARKER_CROSS,10,1)
            self.ui.UiPages.LNano.setText(' '+str(round(self.nanometers[self.ui.UiPages.AdCursor.value()],2))+"nm")
            self.ui.UiPages.LInt.setText(" "+str(round((self.intensity[self.ui.UiPages.AdCursor.value()]/255),2)))
        
        
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
        self.capture.release()
        self.capture = cv2.VideoCapture(self.ui.UiPages.List[self.ui.UiPages.CamList2.currentIndex()])
    
    def PREditUpdater(self):
        self.ui.UiPages.PixelRowEdit.setText(str(self.ui.UiPages.PixRowSlider.value()))
    def PREditUpdater2(self):
        self.ui.UiPages.PixRowSlider.setValue(self.ui.UiPages.CamSlide2.value())
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
            self.ui.UiPages.LNano.setEnabled(True)
            self.ui.UiPages.LInt.setEnabled(True)

        else:
            self.ui.UiPages.AdCursor.setEnabled(False)
            self.ui.UiPages.LNano.setEnabled(False)
            self.ui.UiPages.LInt.setEnabled(False)

    
    def ApplyCal(self):
        CalA = (self.ui.UiPages.FirstPoint.value(),self.ui.UiPages.SecondPoint.value())
        CalB = (self.ui.UiPages.SPWL.value(),self.ui.UiPages.FPWL.value())
        self.CalPoints = [CalA,CalB]
        self.PixRange = abs(self.CalPoints[0][0] - self.CalPoints[0][1])
        self.NMRange = abs(self.CalPoints[1][0] - self.CalPoints[1][1])
        self.ScaleZeroVal = (self.ui.UiPages.FPWL.value() - (self.ui.UiPages.FirstPoint.value()/(self.PixRange/self.NMRange)))
        for i in range(640):
            self.nanometers[i] = self.ScaleZeroVal+(i/(self.PixRange/self.NMRange))
            self.nanometersINT[i] = int(self.ScaleZeroVal+(i/(self.PixRange/self.NMRange)))
        
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
        print("Nm Cursor: ",self.nanometers[self.ui.UiPages.AdCursor.value()])
        print("Pixel do cursor: ",self.ui.UiPages.AdCursor.value()+self.scaleZero)
        print(self.ui.UiPages.List)

    def GenCSV(self):
        file= QFileDialog()
        fileName = file.getSaveFileName(self,'Salvar Arquivo .csv','','*.csv')
        # print(fileName[0])
        # print(len(self.intensity))
        # print(str(self.intensity[1]))
        fcsv = open(fileName[0],'w')
        if self.ui.UiPages.SplitChannel.isChecked():
            R,G,B = cv2.split(self.Frame)
            fcsv.write('Lambda,Média,R,G,B'+','+self.ui.UiPages.SpecMethod.currentText()+'\n')
            for i in range(640):
                fcsv.write(str(self.nanometers[i])+','+str(self.intensity[i])+','+str(R[self.RowCursor,i])\
                    +','+str(G[self.RowCursor,i])+','+str(B[self.RowCursor,i])+'\n')
        else:
            fcsv.write('Lambda,Intensidade'+','+self.ui.UiPages.SpecMethod.currentText()+'\n')
            for i in range(640):
                fcsv.write(str(self.nanometers[i])+','+str(self.intensity[i])+'\n')
    
    def SnapGraph(self):
        file= QFileDialog()
        fileName = file.getSaveFileName(self,'Salvar Imagem do gráfico','','*.jpg,*.png,*.svg')
        cv2.imwrite(fileName[0],cv2.cvtColor(self.graphic,cv2.COLOR_BGR2RGB))

    def SnapShot(self):
        file= QFileDialog()
        fileName = file.getSaveFileName(self,'Salvar Imagem da câmera','','*.jpg,*.png,*.svg')
        cv2.imwrite(fileName[0],self.Frame)

    def CropCons(self):
        self.ui.UiPages.KeepRatio.setEnabled(True)
        if self.ui.UiPages.CropConEnable.isChecked():
            self.ui.UiPages.CropXEnd.setEnabled(True)
            self.ui.UiPages.CropYEnd.setEnabled(True)
            self.ui.UiPages.CropXStart.setEnabled(True)
            self.ui.UiPages.CropYStart.setEnabled(True)
        else:
            self.ui.UiPages.CropXEnd.setEnabled(False)
            self.ui.UiPages.CropYEnd.setEnabled(False)
            self.ui.UiPages.CropXStart.setEnabled(False)
            self.ui.UiPages.CropYStart.setEnabled(False)

        pass

    def ApplyCrop(self):
        self.IsCropped = True
        self.ui.UiPages.CropConEnable.setChecked(False)
        self.ui.UiPages.ApplyCrop.setEnabled(False)
        self.ui.UiPages.RevertCrop.setEnabled(True)

        # Atribuindo Valores
        self.x1 = self.ui.UiPages.CropXStart.value()
        self.x2 = self.ui.UiPages.CropXEnd.value()
        self.y1 = self.ui.UiPages.CropYStart.value()
        self.y2 = self.ui.UiPages.CropYEnd.value()
        
    def UndoCrop(self):
        self.IsCropped = False
        self.ui.UiPages.CropConEnable.setChecked(False)
        self.ui.UiPages.RevertCrop.setEnabled(False)
        self.ui.UiPages.ApplyCrop.setEnabled(True)


    def AspectRatio(self):
        if self.ui.UiPages.KeepRatio.isChecked():
            self.ui.UiPages.CropXEnd.setEnabled(False)
        else:
            self.ui.UiPages.CropXEnd.setEnabled(True)

    def SpecMethod(self):
        self.ChannelSplit = self.ui.UiPages.SpecMethod.currentIndex()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_Window()
    sys.exit(app.exec_())
