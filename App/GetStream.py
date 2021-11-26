from qt_core import *
import cv2

class CameraInput:
      
    def RunCam(self):
        self.CamID = 0
        self.VideoSize = QSize(640,480)
        
        # Inicializando o OpenCV:
        self.capture = cv2.VideoCapture(self.CamID)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.VideoSize.width())
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.VideoSize.height())

        # Criando o timer que vai atualizar a imagem:
        self.timer = QTimer()
        self.timer.timeout.connect(self.VideoLabel)
        self.timer.start(30)

    def VideoLabel(self):
        # Método que realiza as conversões para o label
        # Retorna a label : "XXXX = VideoLabel()"
        label = QLabel("No Input.")
        ret, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        image = QImage(frame, frame.shape[1], frame.shape[0],frame.strides[0], QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(image))

        return label

