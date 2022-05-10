from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1132, 644)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setStyleSheet("* {\n"
                                 "    border: none;\n"
                                 "    background-color:transparent;\n"
                                 "    background: transparent;\n"
                                 "    padding: 0;\n"
                                 "    margin:0;\n"
                                 "    color:#fff;\n"
                                 "}\n"
                                 "\n"
                                 "#centralwidget {\n"
                                 "    background-color: #1f232a;\n"
                                 "}\n"
                                 "\n"
                                 "#leftToolsSubContainer {\n"
                                 "    background-color: #16191d;\n"
                                 "}\n"
                                 "\n"
                                 "\n"
                                 "#leftToolsSubContainer QPushButton {\n"
                                 "    text-align: left;\n"
                                 "    padding-left:10px;\n"
                                 "    padding-top:4px;\n"
                                 "    padding-bottom:4px;\n"
                                 "    margin-top:2px;\n"
                                 "    margin-bottom:2px;\n"
                                 "    border-top-left-radius: 10px;\n"
                                 "    border-bottom-left-radius: 10px;\n"
                                 "}\n"
                                 "#leftToolsSubContainer QPushButton:hover {\n"
                                 "background-color: #55aaff;\n"
                                 "}\n"
                                 "\n"
                                 "\n"
                                 "#centerToolsContainer {\n"
                                 "    background-color: #2c313c;\n"
                                 "}\n"
                                 "\n"
                                 "#frame_4 {\n"
                                 "    background-color: rgb(36, 40, 49);\n"
                                 "}\n"
                                 "\n"
                                 "#popupNotificationContainer {\n"
                                 "    background-color: #16191d;\n"
                                 "    border-radius: 10px;\n"
                                 "}\n"
                                 "\n"
                                 "#headerContainer {\n"
                                 "    background-color: #2c313c;\n"
                                 "}\n"
                                 "\n"
                                 "QTabWidget::tab-bar {\n"
                                 "   border: 1px solid gray;\n"
                                 "}\n"
                                 "\n"
                                 "QTabWidget::pane { \n"
                                 "   border: none;\n"
                                 "}\n"
                                 "QTabBar::tab {\n"
                                 "  background:  #16191d;\n"
                                 "  color: white;\n"
                                 "  padding: 10px;\n"
                                 " }\n"
                                 "\n"
                                 " QTabBar::tab:selected {\n"
                                 "  background: #2c313c;\n"
                                 " }\n"
                                 "QTabBar::close-button {\n"
                                 "    image: url(:/icons/icons/x-circle.svg);\n"
                                 "}\n"
                                 "\n"
                                 " QTabBar::close-button:hover {\n"
                                 "    image: url(:/icons/icons/x-circle(1).svg);\n"
                                 "}\n"
                                 "")
        MainWindow.setAnimated(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftToolsContainer = QtWidgets.QWidget(self.centralwidget)
        self.leftToolsContainer.setObjectName("leftToolsContainer")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.leftToolsContainer)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.leftToolsSubContainer = QtWidgets.QWidget(self.leftToolsContainer)
        self.leftToolsSubContainer.setMaximumSize(QtCore.QSize(55, 16777215))
        self.leftToolsSubContainer.setObjectName("leftToolsSubContainer")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.leftToolsSubContainer)
        self.verticalLayout_2.setContentsMargins(5, 0, 0, 0)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(self.leftToolsSubContainer)
        self.frame.setMinimumSize(QtCore.QSize(200, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setContentsMargins(0, 10, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.openToolsButton = QtWidgets.QPushButton(self.frame)
        self.openToolsButton.setMinimumSize(QtCore.QSize(50, 0))
        self.openToolsButton.setStyleSheet("")
        self.openToolsButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/align-justify.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openToolsButton.setIcon(icon)
        self.openToolsButton.setIconSize(QtCore.QSize(24, 24))
        self.openToolsButton.setObjectName("openToolsButton")
        self.verticalLayout_3.addWidget(self.openToolsButton)
        self.verticalLayout_2.addWidget(self.frame, 0, QtCore.Qt.AlignTop)
        self.frame_2 = QtWidgets.QFrame(self.leftToolsSubContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_2.setStyleSheet("")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setContentsMargins(0, 10, 0, 20)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.allFogNodesButton = QtWidgets.QPushButton(self.frame_2)
        self.allFogNodesButton.setMinimumSize(QtCore.QSize(50, 0))
        self.allFogNodesButton.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/layers.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.allFogNodesButton.setIcon(icon1)
        self.allFogNodesButton.setIconSize(QtCore.QSize(24, 24))
        self.allFogNodesButton.setObjectName("allFogNodesButton")
        self.verticalLayout_4.addWidget(self.allFogNodesButton)
        self.allStoragesButton = QtWidgets.QPushButton(self.frame_2)
        self.allStoragesButton.setMinimumSize(QtCore.QSize(50, 0))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/grid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.allStoragesButton.setIcon(icon2)
        self.allStoragesButton.setIconSize(QtCore.QSize(24, 24))
        self.allStoragesButton.setObjectName("allStoragesButton")
        self.verticalLayout_4.addWidget(self.allStoragesButton)
        self.openPoolButton = QtWidgets.QPushButton(self.frame_2)
        self.openPoolButton.setMinimumSize(QtCore.QSize(50, 0))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/icons/globe.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openPoolButton.setIcon(icon3)
        self.openPoolButton.setIconSize(QtCore.QSize(24, 24))
        self.openPoolButton.setObjectName("openPoolButton")
        self.verticalLayout_4.addWidget(self.openPoolButton)
        self.verticalLayout_2.addWidget(self.frame_2, 0, QtCore.Qt.AlignTop)
        self.frame_9 = QtWidgets.QFrame(self.leftToolsSubContainer)
        self.frame_9.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.frame_9)
        self.verticalLayout_11.setContentsMargins(0, 20, 0, 0)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.addFogNodeButton = QtWidgets.QPushButton(self.frame_9)
        self.addFogNodeButton.setMinimumSize(QtCore.QSize(50, 0))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/icons/package.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addFogNodeButton.setIcon(icon4)
        self.addFogNodeButton.setIconSize(QtCore.QSize(24, 24))
        self.addFogNodeButton.setObjectName("addFogNodeButton")
        self.verticalLayout_11.addWidget(self.addFogNodeButton)
        self.createPoolButton = QtWidgets.QPushButton(self.frame_9)
        self.createPoolButton.setMinimumSize(QtCore.QSize(50, 0))
        self.createPoolButton.setIcon(icon3)
        self.createPoolButton.setIconSize(QtCore.QSize(24, 24))
        self.createPoolButton.setObjectName("createPoolButton")
        self.verticalLayout_11.addWidget(self.createPoolButton)
        self.createFolderButton = QtWidgets.QPushButton(self.frame_9)
        self.createFolderButton.setMinimumSize(QtCore.QSize(50, 0))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/icons/folder-plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.createFolderButton.setIcon(icon5)
        self.createFolderButton.setIconSize(QtCore.QSize(24, 24))
        self.createFolderButton.setObjectName("createFolderButton")
        self.verticalLayout_11.addWidget(self.createFolderButton)
        self.openClientStorageButton = QtWidgets.QPushButton(self.frame_9)
        self.openClientStorageButton.setMinimumSize(QtCore.QSize(50, 0))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/icons/inbox.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openClientStorageButton.setIcon(icon6)
        self.openClientStorageButton.setIconSize(QtCore.QSize(24, 24))
        self.openClientStorageButton.setObjectName("openClientStorageButton")
        self.verticalLayout_11.addWidget(self.openClientStorageButton)
        self.sendFileButton = QtWidgets.QPushButton(self.frame_9)
        self.sendFileButton.setMinimumSize(QtCore.QSize(50, 0))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/icons/file-plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sendFileButton.setIcon(icon7)
        self.sendFileButton.setIconSize(QtCore.QSize(24, 24))
        self.sendFileButton.setObjectName("sendFileButton")
        self.verticalLayout_11.addWidget(self.sendFileButton)
        self.addNSButton = QtWidgets.QPushButton(self.frame_9)
        self.addNSButton.setMinimumSize(QtCore.QSize(50, 0))
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/icons/user-plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addNSButton.setIcon(icon8)
        self.addNSButton.setIconSize(QtCore.QSize(24, 24))
        self.addNSButton.setObjectName("addNSButton")
        self.verticalLayout_11.addWidget(self.addNSButton)
        self.sendByteExButton = QtWidgets.QPushButton(self.frame_9)
        self.sendByteExButton.setMinimumSize(QtCore.QSize(50, 0))
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/icons/send.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sendByteExButton.setIcon(icon9)
        self.sendByteExButton.setIconSize(QtCore.QSize(24, 24))
        self.sendByteExButton.setObjectName("sendByteExButton")
        self.verticalLayout_11.addWidget(self.sendByteExButton)
        self.verticalLayout_2.addWidget(self.frame_9, 0, QtCore.Qt.AlignTop)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.frame_3 = QtWidgets.QFrame(self.leftToolsSubContainer)
        self.frame_3.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_5.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.settingsButton = QtWidgets.QPushButton(self.frame_3)
        self.settingsButton.setMinimumSize(QtCore.QSize(50, 0))
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/icons/info.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsButton.setIcon(icon10)
        self.settingsButton.setIconSize(QtCore.QSize(24, 24))
        self.settingsButton.setObjectName("settingsButton")
        self.verticalLayout_5.addWidget(self.settingsButton)
        self.informationButton = QtWidgets.QPushButton(self.frame_3)
        self.informationButton.setMinimumSize(QtCore.QSize(50, 0))
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icons/icons/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.informationButton.setIcon(icon11)
        self.informationButton.setIconSize(QtCore.QSize(24, 24))
        self.informationButton.setObjectName("informationButton")
        self.verticalLayout_5.addWidget(self.informationButton)
        self.verticalLayout_2.addWidget(self.frame_3, 0, QtCore.Qt.AlignBottom)
        self.verticalLayout.addWidget(self.leftToolsSubContainer, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.leftToolsContainer, 0, QtCore.Qt.AlignLeft)
        self.centerToolsContainer = QtWidgets.QWidget(self.centralwidget)
        self.centerToolsContainer.setMinimumSize(QtCore.QSize(0, 0))
        self.centerToolsContainer.setMaximumSize(QtCore.QSize(0, 16777215))
        self.centerToolsContainer.setObjectName("centerToolsContainer")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centerToolsContainer)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_4 = QtWidgets.QFrame(self.centerToolsContainer)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setContentsMargins(0, 11, 5, 7)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.closeCenterToolsButton = QtWidgets.QPushButton(self.frame_4)
        self.closeCenterToolsButton.setText("")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/icons/icons/x-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeCenterToolsButton.setIcon(icon12)
        self.closeCenterToolsButton.setIconSize(QtCore.QSize(24, 24))
        self.closeCenterToolsButton.setObjectName("closeCenterToolsButton")
        self.horizontalLayout_3.addWidget(self.closeCenterToolsButton, 0, QtCore.Qt.AlignRight)
        self.verticalLayout_6.addWidget(self.frame_4, 0, QtCore.Qt.AlignTop)
        self.frame_5 = QtWidgets.QFrame(self.centerToolsContainer)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.frame_5)
        self.stackedWidget.setObjectName("stackedWidget")
        self.pageInformation = QtWidgets.QWidget()
        self.pageInformation.setObjectName("pageInformation")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.pageInformation)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_3 = QtWidgets.QLabel(self.pageInformation)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_7.addWidget(self.label_3)
        self.stackedWidget.addWidget(self.pageInformation)
        self.pageSettings = QtWidgets.QWidget()
        self.pageSettings.setObjectName("pageSettings")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.pageSettings)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_2 = QtWidgets.QLabel(self.pageSettings)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_8.addWidget(self.label_2, 0, QtCore.Qt.AlignTop)
        self.frame_10 = QtWidgets.QFrame(self.pageSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_10.sizePolicy().hasHeightForWidth())
        self.frame_10.setSizePolicy(sizePolicy)
        self.frame_10.setStyleSheet("\n"
                                    "/* LINE EDIT */\n"
                                    "QLineEdit {\n"
                                    "    background-color: rgba(39, 44, 54, 150);\n"
                                    "    border-radius: 10px;\n"
                                    "    border: 2px solid rgb(38, 78, 117);\n"
                                    "    padding-left: 10px;\n"
                                    "}\n"
                                    "QLineEdit:hover {\n"
                                    "    border: 2px solid #55aaff;\n"
                                    "}\n"
                                    "QLineEdit:focus {\n"
                                    "    border: 2px solid rgb(91, 101, 124);\n"
                                    "}")
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.frame_10)
        self.verticalLayout_12.setContentsMargins(0, 12, 0, 0)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 5, 0, -1)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.rootIPlineEdit = QtWidgets.QLineEdit(self.frame_10)
        self.rootIPlineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.rootIPlineEdit.setObjectName("rootIPlineEdit")
        self.gridLayout.addWidget(self.rootIPlineEdit, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame_10)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_10)
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 4, 0, 1, 1)
        self.poolPortlineEdit = QtWidgets.QLineEdit(self.frame_10)
        self.poolPortlineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.poolPortlineEdit.setObjectName("poolPortlineEdit")
        self.gridLayout.addWidget(self.poolPortlineEdit, 2, 1, 1, 1)
        self.CMPortlineEdit = QtWidgets.QLineEdit(self.frame_10)
        self.CMPortlineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.CMPortlineEdit.setObjectName("CMPortlineEdit")
        self.gridLayout.addWidget(self.CMPortlineEdit, 3, 1, 1, 1)
        self.FNPortlineEdit = QtWidgets.QLineEdit(self.frame_10)
        self.FNPortlineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.FNPortlineEdit.setObjectName("FNPortlineEdit")
        self.gridLayout.addWidget(self.FNPortlineEdit, 4, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.frame_10)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.frame_10)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(False)
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        self.label_6.setFont(font)
        self.label_6.setAutoFillBackground(False)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)
        self.submitButton = QtWidgets.QPushButton(self.frame_10)
        self.submitButton.setMinimumSize(QtCore.QSize(0, 0))
        self.submitButton.setStyleSheet("QPushButton {\n"
                                        "    border-radius:5px;\n"
                                        "    padding: 1px;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: #55aaff;\n"
                                        "}")
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/icons/icons/check-square.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.submitButton.setIcon(icon13)
        self.submitButton.setIconSize(QtCore.QSize(24, 24))
        self.submitButton.setObjectName("submitButton")
        self.gridLayout.addWidget(self.submitButton, 6, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.frame_10)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.changeTopicButton = QtWidgets.QPushButton(self.frame_10)
        self.changeTopicButton.setMaximumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.changeTopicButton.setFont(font)
        self.changeTopicButton.setStyleSheet("QPushButton {\n"
                                             "    background-repeat:none;\n"
                                             "    background-position: center;\n"
                                             "    background-image: url(:/icons/icons/sun.svg);\n"
                                             "}\n"
                                             "QPushButton:hover {\n"
                                             "    background-image: url(:/icons/icons/sun(1).svg);\n"
                                             "}")
        self.changeTopicButton.setText("")
        self.changeTopicButton.setObjectName("changeTopicButton")
        self.gridLayout.addWidget(self.changeTopicButton, 0, 1, 1, 1)
        self.verticalLayout_12.addLayout(self.gridLayout)
        self.verticalLayout_8.addWidget(self.frame_10)
        self.stackedWidget.addWidget(self.pageSettings)
        self.horizontalLayout_2.addWidget(self.stackedWidget)
        self.verticalLayout_6.addWidget(self.frame_5)
        self.horizontalLayout.addWidget(self.centerToolsContainer, 0, QtCore.Qt.AlignLeft)
        self.mainBodyContainer = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainBodyContainer.sizePolicy().hasHeightForWidth())
        self.mainBodyContainer.setSizePolicy(sizePolicy)
        self.mainBodyContainer.setStyleSheet("")
        self.mainBodyContainer.setObjectName("mainBodyContainer")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.mainBodyContainer)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.headerContainer = QtWidgets.QWidget(self.mainBodyContainer)
        self.headerContainer.setStyleSheet("background-color: #2c313c;")
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout_5.setContentsMargins(0, 5, 0, 5)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.frame_8 = QtWidgets.QFrame(self.headerContainer)
        self.frame_8.setStyleSheet("background-color: #2c313c;")
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_8)
        self.horizontalLayout_6.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(5)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_5 = QtWidgets.QLabel(self.frame_8)
        self.label_5.setMaximumSize(QtCore.QSize(30, 30))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_6.addWidget(self.label_5)
        self.label_4 = QtWidgets.QLabel(self.frame_8)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.horizontalLayout_5.addWidget(self.frame_8, 0, QtCore.Qt.AlignLeft)
        self.frame_7 = QtWidgets.QFrame(self.headerContainer)
        self.frame_7.setToolTip("")
        self.frame_7.setStyleSheet("background-color: #2c313c;")
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setContentsMargins(0, 0, 10, 0)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.minimizeButton = QtWidgets.QPushButton(self.frame_7)
        self.minimizeButton.setText("")
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/icons/icons/minus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimizeButton.setIcon(icon14)
        self.minimizeButton.setIconSize(QtCore.QSize(16, 16))
        self.minimizeButton.setObjectName("minimizeButton")
        self.horizontalLayout_4.addWidget(self.minimizeButton)
        self.restoreButton = QtWidgets.QPushButton(self.frame_7)
        self.restoreButton.setStyleSheet("")
        self.restoreButton.setText("")
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/icons/icons/square.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.restoreButton.setIcon(icon15)
        self.restoreButton.setIconSize(QtCore.QSize(16, 16))
        self.restoreButton.setObjectName("restoreButton")
        self.horizontalLayout_4.addWidget(self.restoreButton)
        self.closeButton = QtWidgets.QPushButton(self.frame_7)
        self.closeButton.setStyleSheet("QPushButton {\n"
                                       "    border-radius:5px;\n"
                                       "    padding: 1px;\n"
                                       "}\n"
                                       "QPushButton:hover {\n"
                                       "    background-color: rgb(255, 38, 41);\n"
                                       "}")
        self.closeButton.setText("")
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/icons/icons/x.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon16)
        self.closeButton.setIconSize(QtCore.QSize(16, 16))
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout_4.addWidget(self.closeButton)
        self.horizontalLayout_5.addWidget(self.frame_7, 0, QtCore.Qt.AlignRight)
        self.verticalLayout_9.addWidget(self.headerContainer, 0, QtCore.Qt.AlignTop)
        self.widget = QtWidgets.QWidget(self.mainBodyContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.tabWidget = QtWidgets.QTabWidget(self.widget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout_10.addWidget(self.tabWidget)
        self.verticalLayout_9.addWidget(self.widget)
        self.horizontalLayout.addWidget(self.mainBodyContainer)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.openToolsButton.setToolTip(_translate("MainWindow", "Open tool menu"))
        self.allFogNodesButton.setToolTip(_translate("MainWindow", "Open the fog nodes management tab"))
        self.allFogNodesButton.setText(_translate("MainWindow", "    All Fog Nodes"))
        self.allStoragesButton.setToolTip(_translate("MainWindow", "Open a window with all client storages"))
        self.allStoragesButton.setText(_translate("MainWindow", "    All Storages"))
        self.openPoolButton.setToolTip(_translate("MainWindow", "Open pool management tab"))
        self.openPoolButton.setText(_translate("MainWindow", "    Open Pool"))
        self.addFogNodeButton.setToolTip(_translate("MainWindow", "Create a new fog node"))
        self.addFogNodeButton.setText(_translate("MainWindow", "    Add Foge Node"))
        self.createPoolButton.setToolTip(_translate("MainWindow", "Create a pool"))
        self.createPoolButton.setText(_translate("MainWindow", "    Create Pool"))
        self.createFolderButton.setToolTip(_translate("MainWindow", "Create folder in storage"))
        self.createFolderButton.setText(_translate("MainWindow", "    Create Folder"))
        self.openClientStorageButton.setToolTip(_translate("MainWindow", "Open client storage"))
        self.openClientStorageButton.setText(_translate("MainWindow", "    Create Client Storage"))
        self.sendFileButton.setToolTip(_translate("MainWindow", "Send new file in storage"))
        self.sendFileButton.setText(_translate("MainWindow", "    Send File"))
        self.addNSButton.setToolTip(_translate("MainWindow", "Create new name client storage"))
        self.addNSButton.setText(_translate("MainWindow", "    Add NS"))
        self.sendByteExButton.setToolTip(_translate("MainWindow", "Send byteEx"))
        self.sendByteExButton.setText(_translate("MainWindow", "    Send ByteEx"))
        self.settingsButton.setToolTip(_translate("MainWindow", "Open information page"))
        self.settingsButton.setText(_translate("MainWindow", "    Information"))
        self.informationButton.setToolTip(_translate("MainWindow", "Open settings page"))
        self.informationButton.setText(_translate("MainWindow", "    Settings"))
        self.label_3.setText(_translate("MainWindow", "Information"))
        self.label_2.setText(_translate("MainWindow", "Settings   "))
        self.label_7.setText(_translate("MainWindow", "Set CM port"))
        self.label_9.setText(_translate("MainWindow", "Set FN port"))
        self.label_8.setText(_translate("MainWindow", "Set POOL port"))
        self.label_6.setText(_translate("MainWindow", "Change the topic theme"))
        self.submitButton.setText(_translate("MainWindow", "Submit"))
        self.label.setText(_translate("MainWindow", "Set Root IP"))
        self.label_5.setToolTip(_translate("MainWindow", "We love our users ♡"))
        self.label_4.setToolTip(_translate("MainWindow", "We love our users ♡"))
        self.label_4.setText(_translate("MainWindow", "Decloud"))
        self.minimizeButton.setToolTip(_translate("MainWindow", "Minimize window"))
        self.restoreButton.setToolTip(_translate("MainWindow", "Restore window"))
        self.closeButton.setToolTip(_translate("MainWindow", "Close window"))


class Ui_AllClientStoragesDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(641, 239)
        Dialog.setStyleSheet("* {\n"
                             "    border: none;\n"
                             "    background-color:transparent;\n"
                             "    background: transparent;\n"
                             "    padding: 0;\n"
                             "    margin:0;\n"
                             "    color:#fff;\n"
                             "}\n"
                             "\n"
                             "#bodyContainer {\n"
                             "    background-color: #16191d;\n"
                             "    border-bottom-left-radius: 25px;\n"
                             "    border-bottom-right-radius: 25px;\n"
                             "}\n"
                             "#headerContainer {\n"
                             "    background-color: #16191d;\n"
                             "}\n"
                             "\n"
                             "QListWidget {    \n"
                             "    background-color: rgba(39, 44, 54, 150);\n"
                             "    padding: 10px;\n"
                             "    border-radius: 20px;\n"
                             "    gridline-color: rgb(44, 49, 60);\n"
                             "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                             "}\n"
                             "QListWidget::item{\n"
                             "    border-color: rgb(44, 49, 60);\n"
                             "    padding-left: 5px;\n"
                             "    padding-right: 5px;\n"
                             "    gridline-color: rgb(44, 49, 60);\n"
                             "}\n"
                             "QListWidget::item:hover{\n"
                             "    background-color: rgba(85, 170, 255, 200);\n"
                             "    border-top-left-radius: 20px;\n"
                             "    \n"
                             "}\n"
                             "QScrollBar:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    height: 14px;\n"
                             "    margin: 0px 21px 0 21px;\n"
                             "    border-radius: 0px;\n"
                             "}\n"
                             " QScrollBar:vertical {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    width: 14px;\n"
                             "    margin: 21px 0 21px 0;\n"
                             "    border-radius: 0px;\n"
                             " }\n"
                             "QHeaderView::section{\n"
                             "    Background-color: rgb(39, 44, 54);\n"
                             "    max-width: 30px;\n"
                             "    border: 1px solid rgb(44, 49, 60);\n"
                             "    border-style: none;\n"
                             "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                             "    border-right: 1px solid rgb(44, 49, 60);\n"
                             "}\n"
                             "QListWidget::horizontalHeader {    \n"
                             "    background-color: rgb(81, 255, 0);\n"
                             "}\n"
                             "QHeaderView::section:horizontal\n"
                             "{\n"
                             "    border: 1px solid rgb(32, 34, 42);\n"
                             "    background-color: rgb(27, 29, 35);\n"
                             "    padding: 3px;\n"
                             "    border-top-left-radius: 7px;\n"
                             "    border-top-right-radius: 7px;\n"
                             "}\n"
                             "QHeaderView::section:vertical\n"
                             "{\n"
                             "    border: 1px solid rgb(44, 49, 60);\n"
                             "}\n"
                             "\n"
                             "\n"
                             "/* SCROLL BARS */\n"
                             "QScrollBar:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    height: 14px;\n"
                             "    margin: 0px 21px 0 21px;\n"
                             "    border-radius: 0px;\n"
                             "}\n"
                             "QScrollBar::handle:horizontal {\n"
                             "    background: rgb(85, 170, 255);\n"
                             "    min-width: 25px;\n"
                             "    border-radius: 7px\n"
                             "}\n"
                             "QScrollBar::add-line:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "    width: 20px;\n"
                             "    border-top-right-radius: 7px;\n"
                             "    border-bottom-right-radius: 7px;\n"
                             "    subcontrol-position: right;\n"
                             "    subcontrol-origin: margin;\n"
                             "}\n"
                             "QScrollBar::sub-line:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "    width: 20px;\n"
                             "    border-top-left-radius: 7px;\n"
                             "    border-bottom-left-radius: 7px;\n"
                             "    subcontrol-position: left;\n"
                             "    subcontrol-origin: margin;\n"
                             "}\n"
                             "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
                             "{\n"
                             "     background: none;\n"
                             "}\n"
                             "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
                             "{\n"
                             "     background: none;\n"
                             "}\n"
                             " QScrollBar:vertical {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    width: 14px;\n"
                             "    margin: 21px 0 21px 0;\n"
                             "    border-radius: 0px;\n"
                             " }\n"
                             " QScrollBar::handle:vertical {    \n"
                             "    background: rgb(85, 170, 255);\n"
                             "    min-height: 25px;\n"
                             "    border-radius: 7px\n"
                             " }\n"
                             " QScrollBar::add-line:vertical {\n"
                             "     border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "     height: 20px;\n"
                             "    border-bottom-left-radius: 7px;\n"
                             "    border-bottom-right-radius: 7px;\n"
                             "     subcontrol-position: bottom;\n"
                             "     subcontrol-origin: margin;\n"
                             " }\n"
                             " QScrollBar::sub-line:vertical {\n"
                             "    border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "     height: 20px;\n"
                             "    border-top-left-radius: 7px;\n"
                             "    border-top-right-radius: 7px;\n"
                             "     subcontrol-position: top;\n"
                             "     subcontrol-origin: margin;\n"
                             " }\n"
                             " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
                             "     background: none;\n"
                             " }\n"
                             "\n"
                             " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
                             "     background: none;\n"
                             " }")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerContainer = QtWidgets.QFrame(Dialog)
        self.headerContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.headerContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout.setContentsMargins(15, 20, 14, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.headerContainer)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setMaximumSize(QtCore.QSize(30, 30))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setWordWrap(False)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout.addWidget(self.frame_3)
        self.verticalLayout.addWidget(self.headerContainer, 0, QtCore.Qt.AlignTop)
        self.bodyContainer = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bodyContainer.sizePolicy().hasHeightForWidth())
        self.bodyContainer.setSizePolicy(sizePolicy)
        self.bodyContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bodyContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bodyContainer.setObjectName("bodyContainer")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.bodyContainer)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_2 = QtWidgets.QFrame(self.bodyContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.listWidget = QtWidgets.QListWidget(self.frame_2)
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayout_5.addWidget(self.listWidget)
        self.horizontalLayout_4.addWidget(self.frame_2)
        self.frame = QtWidgets.QFrame(self.bodyContainer)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(17)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.okButton = QtWidgets.QPushButton(self.frame)
        self.okButton.setMinimumSize(QtCore.QSize(0, 0))
        self.okButton.setStyleSheet("QPushButton {\n"
                                    "    border-radius:5px;\n"
                                    "    padding: 1px;\n"
                                    "}\n"
                                    "QPushButton:hover {\n"
                                    "    background-color: rgb(22, 216, 87);\n"
                                    "}")
        self.okButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setIconSize(QtCore.QSize(24, 24))
        self.okButton.setObjectName("okButton")
        self.verticalLayout_2.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 0))
        self.cancelButton.setStyleSheet("QPushButton {\n"
                                        "    border-radius:5px;\n"
                                        "    padding: 1px;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(255, 38, 41);\n"
                                        "}")
        self.cancelButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/x.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setIconSize(QtCore.QSize(24, 24))
        self.cancelButton.setObjectName("cancelButton")
        self.verticalLayout_2.addWidget(self.cancelButton)
        spacerItem = QtWidgets.QSpacerItem(20, 93, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_4.addWidget(self.frame, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.bodyContainer)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Decloud All Client Storages"))


class Ui_SendByteExDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(477, 241)
        Dialog.setStyleSheet("* {\n"
                             "    border: none;\n"
                             "    background-color:transparent;\n"
                             "    background: transparent;\n"
                             "    padding: 0;\n"
                             "    margin:0;\n"
                             "    color:#fff;\n"
                             "}\n"
                             "\n"
                             "#bodyContainer {\n"
                             "    background-color: #16191d;\n"
                             "    border-bottom-left-radius: 20px;\n"
                             "    border-bottom-right-radius: 20px;\n"
                             "}\n"
                             "#headerContainer {\n"
                             "    background-color: #16191d;\n"
                             "}\n"
                             "/* LINE EDIT */\n"
                             "QLineEdit {\n"
                             "    background-color: rgba(39, 44, 54, 150);\n"
                             "    border-radius: 10px;\n"
                             "    border: 2px solid rgb(38, 78, 117);\n"
                             "    padding-left: 10px;\n"
                             "}\n"
                             "QLineEdit:hover {\n"
                             "    border: 2px solid #55aaff;\n"
                             "}\n"
                             "QLineEdit:focus {\n"
                             "    border: 2px solid rgb(91, 101, 124);\n"
                             "}\n"
                             "")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerContainer = QtWidgets.QFrame(Dialog)
        self.headerContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.headerContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout.setContentsMargins(15, 20, 14, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.headerContainer)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setMaximumSize(QtCore.QSize(30, 30))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setWordWrap(False)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout.addWidget(self.frame_3, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout.addWidget(self.headerContainer, 0, QtCore.Qt.AlignTop)
        self.bodyContainer = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bodyContainer.sizePolicy().hasHeightForWidth())
        self.bodyContainer.setSizePolicy(sizePolicy)
        self.bodyContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bodyContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bodyContainer.setObjectName("bodyContainer")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.bodyContainer)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_2 = QtWidgets.QFrame(self.bodyContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, 0, -1)
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.senderLineEdit = QtWidgets.QLineEdit(self.frame_2)
        self.senderLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.senderLineEdit.setObjectName("senderLineEdit")
        self.gridLayout.addWidget(self.senderLineEdit, 0, 1, 1, 1)
        self.ownerLineEdit = QtWidgets.QLineEdit(self.frame_2)
        self.ownerLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.ownerLineEdit.setObjectName("ownerLineEdit")
        self.gridLayout.addWidget(self.ownerLineEdit, 1, 1, 1, 1)
        self.amountLineEdit = QtWidgets.QLineEdit(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amountLineEdit.sizePolicy().hasHeightForWidth())
        self.amountLineEdit.setSizePolicy(sizePolicy)
        self.amountLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.amountLineEdit.setObjectName("amountLineEdit")
        self.gridLayout.addWidget(self.amountLineEdit, 2, 1, 1, 1)
        self.horizontalLayout_5.addLayout(self.gridLayout)
        self.horizontalLayout_4.addWidget(self.frame_2)
        self.frame = QtWidgets.QFrame(self.bodyContainer)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(17)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.okButton = QtWidgets.QPushButton(self.frame)
        self.okButton.setMinimumSize(QtCore.QSize(0, 0))
        self.okButton.setStyleSheet("QPushButton {\n"
                                    "    border-radius:5px;\n"
                                    "    padding: 1px;\n"
                                    "}\n"
                                    "QPushButton:hover {\n"
                                    "    background-color: rgb(22, 216, 87);\n"
                                    "}")
        self.okButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setIconSize(QtCore.QSize(24, 24))
        self.okButton.setObjectName("okButton")
        self.verticalLayout_2.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 0))
        self.cancelButton.setStyleSheet("QPushButton {\n"
                                        "    border-radius:5px;\n"
                                        "    padding: 1px;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(255, 38, 41);\n"
                                        "}")
        self.cancelButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/x.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setIconSize(QtCore.QSize(24, 24))
        self.cancelButton.setObjectName("cancelButton")
        self.verticalLayout_2.addWidget(self.cancelButton)
        spacerItem = QtWidgets.QSpacerItem(20, 93, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_4.addWidget(self.frame, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.bodyContainer)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Decloud Send ByteEx"))
        self.label_5.setText(_translate("Dialog", "Amount"))
        self.label_4.setText(_translate("Dialog", "Owner"))
        self.label_3.setText(_translate("Dialog", "Sender"))


class Ui_CreateFolderDialog(object):
    class NameLineEdit(QLineEdit):
        from PyQt5.QtCore import pyqtSignal
        enterPress = pyqtSignal()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def keyPressEvent(self, event):
            super().keyPressEvent(event)
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                self.enterPress.emit()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(379, 180)
        Dialog.setWindowTitle("Dialog")
        Dialog.setStyleSheet("* {\n"
                             "    border: none;\n"
                             "    background-color:transparent;\n"
                             "    background: transparent;\n"
                             "    padding: 0;\n"
                             "    margin:0;\n"
                             "    color:#fff;\n"
                             "}\n"
                             "\n"
                             "#bodyContainer {\n"
                             "    background-color: #16191d;\n"
                             "    border-bottom-left-radius: 20px;\n"
                             "    border-bottom-right-radius: 20px;\n"
                             "}\n"
                             "#headerContainer {\n"
                             "    background-color: #16191d;\n"
                             "}\n"
                             "\n"
                             "/* LINE EDIT */\n"
                             "QLineEdit {\n"
                             "    background-color: rgba(39, 44, 54, 150);\n"
                             "    border-radius: 10px;\n"
                             "    border: 2px solid rgb(38, 78, 117);\n"
                             "    padding-left: 10px;\n"
                             "}\n"
                             "QLineEdit:hover {\n"
                             "    border: 2px solid #55aaff;\n"
                             "}\n"
                             "QLineEdit:focus {\n"
                             "    border: 2px solid rgb(91, 101, 124);\n"
                             "}\n"
                             "")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerContainer = QtWidgets.QFrame(Dialog)
        self.headerContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.headerContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout.setContentsMargins(15, 20, 14, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.headerContainer)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setMaximumSize(QtCore.QSize(30, 30))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setWordWrap(False)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout.addWidget(self.frame_3)
        self.verticalLayout.addWidget(self.headerContainer)
        self.bodyContainer = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bodyContainer.sizePolicy().hasHeightForWidth())
        self.bodyContainer.setSizePolicy(sizePolicy)
        self.bodyContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bodyContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bodyContainer.setObjectName("bodyContainer")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.bodyContainer)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_2 = QtWidgets.QFrame(self.bodyContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.nameFolderLineEdit = self.NameLineEdit(self.frame_2)
        self.nameFolderLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.nameFolderLineEdit.setObjectName("nameFolderLineEdit")
        self.horizontalLayout_5.addWidget(self.nameFolderLineEdit)
        self.horizontalLayout_4.addWidget(self.frame_2)
        self.frame = QtWidgets.QFrame(self.bodyContainer)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(17)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.okButton = QtWidgets.QPushButton(self.frame)
        self.okButton.setMinimumSize(QtCore.QSize(0, 0))
        self.okButton.setStyleSheet("QPushButton {\n"
                                    "    border-radius:5px;\n"
                                    "    padding: 1px;\n"
                                    "}\n"
                                    "QPushButton:hover {\n"
                                    "    background-color: rgb(22, 216, 87);\n"
                                    "}")
        self.okButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setIconSize(QtCore.QSize(24, 24))
        self.okButton.setObjectName("okButton")
        self.verticalLayout_2.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 0))
        self.cancelButton.setStyleSheet("QPushButton {\n"
                                        "    border-radius:5px;\n"
                                        "    padding: 1px;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(255, 38, 41);\n"
                                        "}")
        self.cancelButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/x.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setIconSize(QtCore.QSize(24, 24))
        self.cancelButton.setObjectName("cancelButton")
        self.verticalLayout_2.addWidget(self.cancelButton)
        spacerItem = QtWidgets.QSpacerItem(20, 93, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_4.addWidget(self.frame, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.bodyContainer)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Dialog", "Decloud Create Folder"))
        self.label_3.setText(_translate("Dialog", "Name"))

class Ui_AddNSDialog(object):
    class NameLineEdit(QLineEdit):
        from PyQt5.QtCore import pyqtSignal
        enterPress = pyqtSignal()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def keyPressEvent(self, event):
            super().keyPressEvent(event)
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                self.enterPress.emit()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(394, 180)
        Dialog.setWindowTitle("Dialog")
        Dialog.setStyleSheet("* {\n"
                             "    border: none;\n"
                             "    background-color:transparent;\n"
                             "    background: transparent;\n"
                             "    padding: 0;\n"
                             "    margin:0;\n"
                             "    color:#fff;\n"
                             "}\n"
                             "\n"
                             "#bodyContainer {\n"
                             "    background-color: #16191d;\n"
                             "    border-bottom-left-radius: 20px;\n"
                             "    border-bottom-right-radius: 20px;\n"
                             "}\n"
                             "#headerContainer {\n"
                             "    background-color: #16191d;\n"
                             "}\n"
                             "\n"
                             "/* LINE EDIT */\n"
                             "QLineEdit {\n"
                             "    background-color: rgba(39, 44, 54, 150);\n"
                             "    border-radius: 10px;\n"
                             "    border: 2px solid rgb(38, 78, 117);\n"
                             "    padding-left: 10px;\n"
                             "}\n"
                             "QLineEdit:hover {\n"
                             "    border: 2px solid #55aaff;\n"
                             "}\n"
                             "QLineEdit:focus {\n"
                             "    border: 2px solid rgb(91, 101, 124);\n"
                             "}\n"
                             "")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerContainer = QtWidgets.QFrame(Dialog)
        self.headerContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.headerContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout.setContentsMargins(15, 20, 14, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.headerContainer)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setMaximumSize(QtCore.QSize(30, 30))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setWordWrap(False)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout.addWidget(self.frame_3, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout.addWidget(self.headerContainer)
        self.bodyContainer = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bodyContainer.sizePolicy().hasHeightForWidth())
        self.bodyContainer.setSizePolicy(sizePolicy)
        self.bodyContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bodyContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bodyContainer.setObjectName("bodyContainer")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.bodyContainer)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_2 = QtWidgets.QFrame(self.bodyContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.nameLineEdit = self.NameLineEdit(self.frame_2)
        self.nameLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.horizontalLayout_5.addWidget(self.nameLineEdit)
        self.horizontalLayout_4.addWidget(self.frame_2)
        self.frame = QtWidgets.QFrame(self.bodyContainer)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(17)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.okButton = QtWidgets.QPushButton(self.frame)
        self.okButton.setMinimumSize(QtCore.QSize(0, 0))
        self.okButton.setStyleSheet("QPushButton {\n"
                                    "    border-radius:5px;\n"
                                    "    padding: 1px;\n"
                                    "}\n"
                                    "QPushButton:hover {\n"
                                    "    background-color: rgb(22, 216, 87);\n"
                                    "}")
        self.okButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setIconSize(QtCore.QSize(24, 24))
        self.okButton.setObjectName("okButton")
        self.verticalLayout_2.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 0))
        self.cancelButton.setStyleSheet("QPushButton {\n"
                                        "    border-radius:5px;\n"
                                        "    padding: 1px;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(255, 38, 41);\n"
                                        "}")
        self.cancelButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/x.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setIconSize(QtCore.QSize(24, 24))
        self.cancelButton.setObjectName("cancelButton")
        self.verticalLayout_2.addWidget(self.cancelButton)
        spacerItem = QtWidgets.QSpacerItem(20, 93, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_4.addWidget(self.frame, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.bodyContainer)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Dialog", "Decloud New Name Storage"))
        self.label_4.setText(_translate("Dialog", "TextLabel"))


class Ui_InfoBlockDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(985, 623)
        Dialog.setWindowTitle("Dialog")
        Dialog.setStyleSheet("* {\n"
                             "    border: none;\n"
                             "    background-color:transparent;\n"
                             "    background: transparent;\n"
                             "    padding: 0;\n"
                             "    margin:0;\n"
                             "    color:#fff;\n"
                             "}\n"
                             "\n"
                             "#bodyContainer {\n"
                             "    background-color: #16191d;\n"
                             "    border-bottom-left-radius: 20px;\n"
                             "    border-bottom-right-radius: 20px;\n"
                             "}\n"
                             "#headerContainer {\n"
                             "    background-color: #16191d;\n"
                             "}\n"
                             "\n"
                             "QTableWidget {    \n"
                             "    background-color: rgb(39, 44, 54);\n"
                             "    padding: 10px;\n"
                             "    border-radius: 5px;\n"
                             "    gridline-color: rgb(44, 49, 60);\n"
                             "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                             "}\n"
                             "QTableWidget::item{\n"
                             "    border-color: rgb(44, 49, 60);\n"
                             "    padding-left: 5px;\n"
                             "    padding-right: 5px;\n"
                             "    gridline-color: rgb(44, 49, 60);\n"
                             "}\n"
                             "QTableWidget::item:selected{\n"
                             "    background-color: #55aaff;\n"
                             "}\n"
                             "QScrollBar:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    height: 14px;\n"
                             "    margin: 0px 21px 0 21px;\n"
                             "    border-radius: 0px;\n"
                             "}\n"
                             " QScrollBar:vertical {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    width: 14px;\n"
                             "    margin: 21px 0 21px 0;\n"
                             "    border-radius: 0px;\n"
                             " }\n"
                             "QHeaderView::section{\n"
                             "    Background-color: rgb(39, 44, 54);\n"
                             "    max-width: 30px;\n"
                             "    border: 1px solid rgb(44, 49, 60);\n"
                             "    border-style: none;\n"
                             "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                             "    border-right: 1px solid rgb(44, 49, 60);\n"
                             "}\n"
                             "QTableWidget::horizontalHeader {    \n"
                             "    background-color: rgb(81, 255, 0);\n"
                             "}\n"
                             "QHeaderView::section:horizontal\n"
                             "{\n"
                             "    border: 1px solid rgb(32, 34, 42);\n"
                             "    background-color: rgb(27, 29, 35);\n"
                             "    padding: 3px;\n"
                             "    border-top-left-radius: 7px;\n"
                             "    border-top-right-radius: 7px;\n"
                             "}\n"
                             "QHeaderView::section:vertical\n"
                             "{\n"
                             "    border: 1px solid rgb(44, 49, 60);\n"
                             "}\n"
                             "\n"
                             "/* SCROLL BARS */\n"
                             "QScrollBar:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    height: 14px;\n"
                             "    margin: 0px 21px 0 21px;\n"
                             "    border-radius: 0px;\n"
                             "}\n"
                             "QScrollBar::handle:horizontal {\n"
                             "    background: #55aaff;;\n"
                             "    min-width: 25px;\n"
                             "    border-radius: 7px\n"
                             "}\n"
                             "QScrollBar::add-line:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "    width: 20px;\n"
                             "    border-top-right-radius: 7px;\n"
                             "    border-bottom-right-radius: 7px;\n"
                             "    subcontrol-position: right;\n"
                             "    subcontrol-origin: margin;\n"
                             "}\n"
                             "QScrollBar::sub-line:horizontal {\n"
                             "    border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "    width: 20px;\n"
                             "    border-top-left-radius: 7px;\n"
                             "    border-bottom-left-radius: 7px;\n"
                             "    subcontrol-position: left;\n"
                             "    subcontrol-origin: margin;\n"
                             "}\n"
                             "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
                             "{\n"
                             "     background: none;\n"
                             "}\n"
                             "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
                             "{\n"
                             "     background: none;\n"
                             "}\n"
                             " QScrollBar:vertical {\n"
                             "    border: none;\n"
                             "    background: rgb(52, 59, 72);\n"
                             "    width: 14px;\n"
                             "    margin: 21px 0 21px 0;\n"
                             "    border-radius: 0px;\n"
                             " }\n"
                             " QScrollBar::handle:vertical {    \n"
                             "    background:#55aaff;;\n"
                             "    min-height: 25px;\n"
                             "    border-radius: 7px\n"
                             " }\n"
                             " QScrollBar::add-line:vertical {\n"
                             "     border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "     height: 20px;\n"
                             "    border-bottom-left-radius: 7px;\n"
                             "    border-bottom-right-radius: 7px;\n"
                             "     subcontrol-position: bottom;\n"
                             "     subcontrol-origin: margin;\n"
                             " }\n"
                             " QScrollBar::sub-line:vertical {\n"
                             "    border: none;\n"
                             "    background: rgb(55, 63, 77);\n"
                             "     height: 20px;\n"
                             "    border-top-left-radius: 7px;\n"
                             "    border-top-right-radius: 7px;\n"
                             "     subcontrol-position: top;\n"
                             "     subcontrol-origin: margin;\n"
                             " }\n"
                             " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
                             "     background: none;\n"
                             " }\n"
                             "\n"
                             " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
                             "     background: none;\n"
                             " }")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerContainer = QtWidgets.QFrame(Dialog)
        self.headerContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.headerContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout.setContentsMargins(15, 20, 14, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.headerContainer)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setMaximumSize(QtCore.QSize(30, 30))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setWordWrap(False)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout.addWidget(self.frame_3, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout.addWidget(self.headerContainer)
        self.bodyContainer = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bodyContainer.sizePolicy().hasHeightForWidth())
        self.bodyContainer.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.bodyContainer.setFont(font)
        self.bodyContainer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bodyContainer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bodyContainer.setObjectName("bodyContainer")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.bodyContainer)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_4 = QtWidgets.QFrame(self.bodyContainer)
        self.frame_4.setStyleSheet("#frame_4 {\n"
                                   "    background-color: #2c313c;\n"
                                   "}\n"
                                   "\n"
                                   "")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_3.setContentsMargins(-1, -1, 11, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_2 = QtWidgets.QFrame(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setStyleSheet("")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_3.addWidget(self.frame_2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(19, 11, 19, 19)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_5 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_5.setFont(font)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_7.setFont(font)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 4, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setWordWrap(True)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 7, 2, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_9.setFont(font)
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 7, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setWordWrap(True)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 4, 2, 1, 1)
        self.RecipientPoolAddressLabel = QtWidgets.QLabel(self.frame_4)
        self.RecipientPoolAddressLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.RecipientPoolAddressLabel.setFont(font)
        self.RecipientPoolAddressLabel.setText("")
        self.RecipientPoolAddressLabel.setWordWrap(True)
        self.RecipientPoolAddressLabel.setObjectName("RecipientPoolAddressLabel")
        self.gridLayout_2.addWidget(self.RecipientPoolAddressLabel, 4, 1, 1, 1)
        self.RecipientFogNodeAddressLabel = QtWidgets.QLabel(self.frame_4)
        self.RecipientFogNodeAddressLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.RecipientFogNodeAddressLabel.setFont(font)
        self.RecipientFogNodeAddressLabel.setText("")
        self.RecipientFogNodeAddressLabel.setWordWrap(True)
        self.RecipientFogNodeAddressLabel.setObjectName("RecipientFogNodeAddressLabel")
        self.gridLayout_2.addWidget(self.RecipientFogNodeAddressLabel, 7, 1, 1, 1)
        self.RecipientPoolAmountLabel = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.RecipientPoolAmountLabel.setFont(font)
        self.RecipientPoolAmountLabel.setText("")
        self.RecipientPoolAmountLabel.setWordWrap(True)
        self.RecipientPoolAmountLabel.setObjectName("RecipientPoolAmountLabel")
        self.gridLayout_2.addWidget(self.RecipientPoolAmountLabel, 4, 3, 1, 2)
        self.DateLabel = QtWidgets.QLabel(self.frame_4)
        self.DateLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.DateLabel.setFont(font)
        self.DateLabel.setText("")
        self.DateLabel.setWordWrap(True)
        self.DateLabel.setObjectName("DateLabel")
        self.gridLayout_2.addWidget(self.DateLabel, 2, 1, 1, 4)
        self.RecipientFogNodeAmountsLabel = QtWidgets.QLabel(self.frame_4)
        self.RecipientFogNodeAmountsLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.RecipientFogNodeAmountsLabel.setFont(font)
        self.RecipientFogNodeAmountsLabel.setText("")
        self.RecipientFogNodeAmountsLabel.setWordWrap(True)
        self.RecipientFogNodeAmountsLabel.setObjectName("RecipientFogNodeAmountsLabel")
        self.gridLayout_2.addWidget(self.RecipientFogNodeAmountsLabel, 7, 3, 1, 2)
        self.label_4 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.NumberBlockLabel = QtWidgets.QLabel(self.frame_4)
        self.NumberBlockLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.NumberBlockLabel.setFont(font)
        self.NumberBlockLabel.setText("")
        self.NumberBlockLabel.setWordWrap(True)
        self.NumberBlockLabel.setObjectName("NumberBlockLabel")
        self.gridLayout_2.addWidget(self.NumberBlockLabel, 0, 1, 1, 4)
        self.HashBlockLabel = QtWidgets.QLabel(self.frame_4)
        self.HashBlockLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.HashBlockLabel.setFont(font)
        self.HashBlockLabel.setText("")
        self.HashBlockLabel.setObjectName("HashBlockLabel")
        self.gridLayout_2.addWidget(self.HashBlockLabel, 1, 1, 1, 4)
        self.gridLayout_2.setColumnStretch(0, 3)
        self.gridLayout_2.setColumnStretch(1, 5)
        self.gridLayout_2.setColumnStretch(2, 1)
        self.gridLayout_2.setColumnStretch(3, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.TransactionTableWidget = QtWidgets.QTableWidget(self.frame_4)
        self.TransactionTableWidget.setStyleSheet("")
        self.TransactionTableWidget.setObjectName("TransactionTableWidget")
        self.TransactionTableWidget.setColumnCount(0)
        self.TransactionTableWidget.setRowCount(0)
        self.verticalLayout_3.addWidget(self.TransactionTableWidget)
        self.horizontalLayout_4.addWidget(self.frame_4)
        self.frame = QtWidgets.QFrame(self.bodyContainer)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(17)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.okButton = QtWidgets.QPushButton(self.frame)
        self.okButton.setMinimumSize(QtCore.QSize(0, 0))
        self.okButton.setStyleSheet("QPushButton {\n"
                                    "    border-radius:5px;\n"
                                    "    padding: 1px;\n"
                                    "}\n"
                                    "QPushButton:hover {\n"
                                    "    background-color: rgb(22, 216, 87);\n"
                                    "}")
        self.okButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setIconSize(QtCore.QSize(24, 24))
        self.okButton.setObjectName("okButton")
        self.verticalLayout_2.addWidget(self.okButton)
        spacerItem = QtWidgets.QSpacerItem(20, 93, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_4.addWidget(self.frame, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.bodyContainer)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Dialog", "Decloud Info Block"))
        self.label_5.setText(_translate("Dialog", "Date create block:"))
        self.label_7.setText(_translate("Dialog", "Recipient Pool address:"))
        self.label_11.setText(_translate("Dialog", "Amount:"))
        self.label_9.setText(_translate("Dialog", "Recipient Fog Node address:"))
        self.label_3.setText(_translate("Dialog", "№ block:"))
        self.label_12.setText(_translate("Dialog", "Amount:"))
        self.label_4.setText(_translate("Dialog", "Hash block"))
import resources_rc

