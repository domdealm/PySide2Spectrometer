from qt_core import *
from GUI.Pages.ui_mainPage import Ui_AppPages

class MainWindow(object):
    def setup_UI(self,parent):
        if not parent.objectName():
            parent.setObjectName("MainWindow")

        # Parametros iniciais:
        parent.resize(800,610)
        parent.setMinimumSize(800,610)
        parent.setMaximumSize(800,610)

        # Widget principal:
        self.main_frame = QFrame()
        #self.main_frame.setStyleSheet("background-color: #d6dfde")

        # Criando o Layout Principal:
        self.main_layout = QHBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        # Menu esquerdo:
        self.leftMenu = QFrame()
        self.leftMenu.setStyleSheet("background-color: #2b2b2b")
        self.leftMenu.setMaximumWidth(60)
        self.leftMenu.setMinimumWidth(60)

        # Páginas:
        self.pages = QStackedWidget()
        self.UiPages = Ui_AppPages()
        self.UiPages.setupUi(self.pages)

        # Conteúdo:
        self.mainContent = QFrame()
        self.mainContent.setStyleSheet("background-color: #d6dfde")

        # Layout do Conteúdo:
        self.MainContentLayout = QVBoxLayout(self.mainContent)
        self.MainContentLayout.addWidget(self.pages)

        # Layout do menu esquerdo
        self.LeftMenuLayout = QVBoxLayout(self.leftMenu)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        # Botões do menu esquerdo
        self.HomeButton = QPushButton("Início")
        self.HomeButton.setStyleSheet("color: white")
        self.ConfigCam = QPushButton("Config. Cam")
        self.ConfigCam.setStyleSheet("color: white")
        self.ConfigGraph = QPushButton("Config. Graf.")
        self.ConfigGraph.setStyleSheet("color: white")
        self.LMSpacer = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)

        # Adicionando no Layout do menu esquerdo
        self.LeftMenuLayout.addWidget(self.HomeButton)
        self.LeftMenuLayout.addWidget(self.ConfigCam)
        self.LeftMenuLayout.addWidget(self.ConfigGraph)
        self.LeftMenuLayout.addSpacerItem(self.LMSpacer)


        # Adicionando os Widgets:
        self.main_layout.addWidget(self.leftMenu)
        self.main_layout.addWidget(self.mainContent)
        self.pages.setCurrentWidget(self.UiPages.page)

        # Definindo Widget principal:
        parent.setCentralWidget(self.main_frame)
