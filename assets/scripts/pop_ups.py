import fitz
import os
import pywinstyles
import assets.scripts.variables as vary

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *


class PagePreview(QWidget):
    def __init__(self, *args, **kwargs):
        super(PagePreview, self).__init__()
        self.setObjectName('preview')

        self.lbl = QLabel()
        self.lbl_1 = QLabel()
        self.lbl_1.setObjectName('lbl')
        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.lbl, alignment=Qt.AlignCenter)
        self.lay.addWidget(self.lbl_1, alignment=Qt.AlignCenter)

        self.mouseReleaseEvent = lambda x: self.clicked()

    def clicked(self):
        vary.window.jumpToPages(int(self.lbl_1.text()) - 1)

    def setPixMap(self, img):
        self.lbl.setPixmap(img)

    def setNumber(self, num):
        self.lbl_1.setText(f'{num}')


class FilePreview(QWidget):
    def __init__(self, *args, **kwargs):
        super(FilePreview, self).__init__()
        self.setObjectName('files')
        self.number = 0

        self.btn = QPushButton()
        self.btn.setStyleSheet('''
                            QPushButton {
                                max-width: 5px;
                                max-height: 5px;
                                min-width: 5px;
                                min-height: 5px;
                                border-radius: 7px;
                                background: #FF636A;
                            }

                            QPushButton::hover {
                                background-color: #FF2245;
                            }

                            QPushButton::pressed {
                                background-color: #FF636A;
                            }
                        ''')

        self.lbl = QLabel()
        self.lbl_1 = QLabel()
        self.lbl_1.setObjectName('lbl')
        self.lbl_1.setMaximumWidth(90)
        self.lbl_1.setMinimumWidth(90)

        self.lay_1 = QHBoxLayout()
        self.lay_1.setContentsMargins(5, 0, 5, 0)
        self.lay_1.addWidget(self.lbl_1)
        self.lay_1.addWidget(self.btn, 0, Qt.AlignmentFlag.AlignRight)

        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.lbl, alignment=Qt.AlignCenter)
        self.lay.addLayout(self.lay_1)

        try:
            if vary.open:
                self.mouseReleaseEvent = lambda x: vary.window.jumpToFiles(self.number)
            else:
                self.mouseReleaseEvent = lambda x: vary.window.openFiles(self.number)
        except:
            pass
        self.btn.pressed.connect(lambda: vary.window.closeFiles(self.number))

    def setPixMap(self, img):
        self.lbl.setPixmap(img)

    def setNumber(self, num):
        self.lbl_1.setText(f'{num}')


class GoToWidget(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(GoToWidget, self).__init__(parent)
        self.setObjectName('go_to')

        self.lbl = QLabel('Page')
        self.lbl.setStyleSheet('font-size: 15px;')

        self.entry = QSpinBox()

        self.lbl_1 = QLabel()
        self.lbl.setStyleSheet('font-size: 15px;')

        if vary.doc is None:
            self.lbl_1.setText(f' of 0')
            self.entry.setRange(0, 1)
            self.entry.setValue(0)
        else:
            self.lbl_1.setText(f' of {vary.doc.page_count}')
            self.entry.setRange(1, vary.doc.page_count)
            self.entry.setValue(vary.current_page + 1)
            self.entry.valueChanged.connect(self.function)
            self.entry.lineEdit().returnPressed.connect(vary.window.closeUnnecassaryWindows)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.lbl)
        self.layout.addWidget(self.entry)
        self.layout.addWidget(self.lbl_1)
        self.setLayout(self.layout)

    def function(self):
        vary.current_page = self.entry.value() - 1
        vary.nav.jump(vary.current_page, QPoint(), vary.nav.currentZoom())
        vary.window.pgNumLabel.setText(f'Page {vary.current_page + 1} of {vary.doc.page_count}')


class InfoWidget(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(InfoWidget, self).__init__(parent)
        self.setObjectName('info')

        self.lbl = QLabel('')
        if vary.doc is not None:
            text = f'Name: {vary.full_name}\n\n'
            for key, value in vary.doc.metadata.items():
                if key not in ('title', 'subject', 'keywords', 'trapped'):
                    text = f'{text}{key.capitalize()}:   {value}\n\n'
            self.lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            text = 'Currently No File Open'
            self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setText(text)
        self.lbl.setStyleSheet('font-size: 13px;')

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.lbl)
        self.setLayout(self.layout)


class RecentWidget(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(RecentWidget, self).__init__(parent)
        self.setObjectName('recent')

        self.list = QListWidget()
        self.list.setStyleSheet(f'max-height: 250; min-height: 250;')
        self.list.setFocusPolicy(Qt.NoFocus)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in vary.list:
            self.list.addItem(os.path.basename(i))
        self.list.currentRowChanged.connect(self.openRecentFiles)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.list)
        self.setLayout(self.layout)

    def openRecentFiles(self):
        try:
            vary.file_path = vary.files[self.list.currentRow()]
            vary.current_page = 0
            vary.doc = fitz.open(vary.file_path)
            vary.window.loadPdfFile()
            vary.pages_array = []
            vary.files_array = []
            vary.window.addingPagesThread()
            vary.window.addingFilesThread()
        except:
            vary.files.pop(vary.files.index(vary.file_path))
        vary.window.recentPaneToggle()


class TogglePanes(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(TogglePanes, self).__init__(parent)
        self.setObjectName('toggle_pane')

        self.btn_1 = QPushButton()
        self.btn_1.setObjectName('action_btn')
        self.btn_1.setIcon(QIcon(f'assets/images/side_pane_{vary.theme}.png'))
        self.btn_1.clicked.connect(self.function_one)
        self.btn_2 = QPushButton()
        self.btn_2.setObjectName('action_btn')
        self.btn_2.setIcon(QIcon(f'assets/images/file_pane_{vary.theme}.png'))
        self.btn_2.clicked.connect(self.function_two)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.btn_1)
        self.layout.addWidget(self.btn_2)
        self.setLayout(self.layout)

    def function_one(self):
        if vary.window.sideBarWidget.isVisible():
            vary.window.sideBarWidget.setHidden(True)
            vary.settings[0] = 0
        elif vary.window.sideBarWidget.isHidden():
            vary.window.sideBarWidget.setVisible(True)
            vary.settings[0] = 1
        vary.window.paneToggleAction()

    def function_two(self):
        if vary.window.fileBarWidget.isVisible():
            vary.window.fileBarWidget.setHidden(True)
            vary.settings[1] = 0
        elif vary.window.fileBarWidget.isHidden():
            vary.window.fileBarWidget.setVisible(True)
            vary.settings[1] = 1
        vary.window.paneToggleAction()


class MenuPanel(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(MenuPanel, self).__init__(parent)
        self.setObjectName('menu_panel')
        self.resize(QSize(400, 180))

        self.layout = QVBoxLayout(self)

        self.btn_1 = QPushButton()
        self.btn_1.setText('Appearance')
        self.btn_1.clicked.connect(self.function_one)

        self.btn_2 = QPushButton()
        self.btn_2.setText('Document Info...')
        self.btn_2.clicked.connect(self.function_two)

        self.btn_3 = QPushButton()
        self.btn_3.setText('Recent Files')
        self.btn_3.clicked.connect(self.function_three)

        self.btn_4 = QPushButton()
        self.btn_4.setText('About')
        self.btn_4.clicked.connect(self.function_four)

        self.btn_5 = QPushButton()
        self.btn_5.setText('Shortcuts')
        self.btn_5.clicked.connect(self.function_five)

        self.lbl_1 = QLabel('Theme: ')
        self.lbl_1.setObjectName('topic')
        self.checkOne = QPushButton()
        self.checkOne.setObjectName('setBtn')
        self.checkOne.setCheckable(True)
        self.checkOne.setIconSize(QSize(27, 27))
        self.checkOne.setIcon(QIcon(f'assets/images/dark_{vary.theme}.png'))
        self.checkOne.clicked.connect(lambda: self.themeChangeAction('dark'))
        self.checkTwo = QPushButton()
        self.checkTwo.setObjectName('setBtn')
        self.checkTwo.setCheckable(True)
        self.checkTwo.setIconSize(QSize(27, 27))
        self.checkTwo.setIcon(QIcon(f'assets/images/light_{vary.theme}.png'))
        self.checkTwo.clicked.connect(lambda: self.themeChangeAction('light'))
        self.lbl_2 = QLabel('Side Pane: ')
        self.lbl_2.setObjectName('topic')
        self.checkThree = QPushButton()
        self.checkThree.setObjectName('setBtn')
        self.checkThree.setCheckable(True)
        self.checkThree.setIconSize(QSize(27, 27))
        self.checkThree.setIcon(QIcon(f'assets/images/show_{vary.theme}.png'))
        self.checkThree.clicked.connect(lambda: self.toggleInterfaceAction(0))
        self.checkFour = QPushButton()
        self.checkFour.setObjectName('setBtn')
        self.checkFour.setCheckable(True)
        self.checkFour.setIconSize(QSize(27, 27))
        self.checkFour.setIcon(QIcon(f'assets/images/hidden_{vary.theme}.png'))
        self.checkFour.clicked.connect(lambda: self.toggleInterfaceAction(1))
        self.lbl_3 = QLabel('Files Pane: ')
        self.lbl_3.setObjectName('topic')
        self.checkFive = QPushButton()
        self.checkFive.setObjectName('setBtn')
        self.checkFive.setCheckable(True)
        self.checkFive.setIconSize(QSize(27, 27))
        self.checkFive.setIcon(QIcon(f'assets/images/show_{vary.theme}.png'))
        self.checkFive.clicked.connect(lambda: self.toggleInterfaceTwoAction(0))
        self.checkSix = QPushButton()
        self.checkSix.setObjectName('setBtn')
        self.checkSix.setCheckable(True)
        self.checkSix.setIconSize(QSize(27, 27))
        self.checkSix.setIcon(QIcon(f'assets/images/hidden_{vary.theme}.png'))
        self.checkSix.clicked.connect(lambda: self.toggleInterfaceTwoAction(1))
        self.lbl_5 = QLabel('Toolbar: ')
        self.lbl_5.setObjectName('topic')
        self.checkSeven = QPushButton()
        self.checkSeven.setObjectName('setBtn')
        self.checkSeven.setCheckable(True)
        self.checkSeven.setIconSize(QSize(27, 27))
        self.checkSeven.setIcon(QIcon(f'assets/images/show_{vary.theme}.png'))
        self.checkSeven.clicked.connect(lambda: self.toolbarButtonToggle(0))
        self.checkEight = QPushButton()
        self.checkEight.setObjectName('setBtn')
        self.checkEight.setCheckable(True)
        self.checkEight.setIconSize(QSize(27, 27))
        self.checkEight.setIcon(QIcon(f'assets/images/hidden_{vary.theme}.png'))
        self.checkEight.clicked.connect(lambda: self.toolbarButtonToggle(1))

        self.gap = QWidget()
        self.gap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gap_1 = QWidget()
        self.gap_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gap_2 = QWidget()
        self.gap_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if vary.theme == 'dark':
            self.checkOne.setChecked(True)
            self.checkTwo.setChecked(False)
        elif vary.theme == 'light':
            self.checkTwo.setChecked(True)
            self.checkOne.setChecked(False)

        if vary.settings[0] == 1:
            self.checkThree.setChecked(True)
            self.checkFour.setChecked(False)
        elif vary.settings[0] == 0:
            self.checkThree.setChecked(False)
            self.checkFour.setChecked(True)

        if vary.settings[1] == 1:
            self.checkFive.setChecked(True)
            self.checkSix.setChecked(False)
        elif vary.settings[1] == 0:
            self.checkFive.setChecked(False)
            self.checkSix.setChecked(True)

        if vary.settings[2] == 1:
            self.checkSeven.setChecked(True)
            self.checkEight.setChecked(False)
        elif vary.settings[2] == 0:
            self.checkSeven.setChecked(False)
            self.checkEight.setChecked(True)

        self.lbl_4 = QLabel('')
        if vary.doc is not None:
            text = f'Name: {vary.full_name}\n\n'
            for key, value in vary.doc.metadata.items():
                if key not in ('title', 'subject', 'keywords', 'trapped'):
                    text = f'{text}{key.capitalize()}:   {value}\n\n'
            self.lbl_4.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            text = 'Currently No File Open'
            self.lbl_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_4.setText(text)
        self.lbl_4.setStyleSheet('font-size: 13px;')
        self.lbl_4.setVisible(False)

        self.list = QListWidget()
        self.list.setStyleSheet(f'max-height: 200; min-height: 200;')
        self.list.setFocusPolicy(Qt.NoFocus)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in vary.list:
            self.list.addItem(os.path.basename(i))
        self.list.currentRowChanged.connect(self.openRecentFiles)
        self.list.setVisible(False)

        self.logo = QPixmap('assets/images/icon.ico')
        self.logo = self.logo.scaled(QSize(100, 100))

        self.lbl_6 = QLabel()
        self.lbl_6.setPixmap(self.logo)

        self.lbl_7 = QLabel()
        self.lbl_7.setText(' PDF Viewer')
        self.lbl_7.setObjectName('wlc')

        self.lbl_8 = QLabel('&nbsp;&nbsp;<b>Developer</b>: Chamal Induwara')
        self.lbl_8.setStyleSheet('font-size: 15px;')

        self.lbl_9 = QLabel(f'&nbsp;&nbsp;<b>Version</b>: {vary.version}')
        self.lbl_9.setStyleSheet('font-size: 15px;')

        self.lbl_10 = QLabel('&nbsp;&nbsp;<b>Year</b>: 2024')
        self.lbl_10.setStyleSheet('font-size: 15px;')

        self.lbl_11 = QLabel('Zoom In')
        self.lbl_11.setStyleSheet('font-size: 15px;')
        self.lbl_12 = QLabel('+')
        self.lbl_12.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_12.setObjectName('button')

        self.lbl_13 = QLabel('Zoom Out')
        self.lbl_13.setStyleSheet('font-size: 15px;')
        self.lbl_14 = QLabel('-')
        self.lbl_14.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_14.setObjectName('button')

        self.lbl_15 = QLabel('Toggle Panes')
        self.lbl_15.setStyleSheet('font-size: 15px;')
        self.lbl_16 = QLabel('Ctrl')
        self.lbl_16.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_16.setObjectName('button')
        self.lbl_17 = QLabel('S')
        self.lbl_17.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_17.setObjectName('button')

        self.lbl_18 = QLabel('Close a File')
        self.lbl_18.setStyleSheet('font-size: 15px;')
        self.lbl_19 = QLabel('Esc')
        self.lbl_19.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_19.setObjectName('button')

        self.lbl_20 = QLabel('Open Menu')
        self.lbl_20.setStyleSheet('font-size: 15px;')
        self.lbl_21 = QLabel('Ctrl')
        self.lbl_21.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_21.setObjectName('button')
        self.lbl_22 = QLabel('M')
        self.lbl_22.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_22.setObjectName('button')

        self.lbl_23 = QLabel('Document Information')
        self.lbl_23.setStyleSheet('font-size: 15px;')
        self.lbl_24 = QLabel('Ctrl')
        self.lbl_24.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_24.setObjectName('button')
        self.lbl_25 = QLabel('I')
        self.lbl_25.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_25.setObjectName('button')

        self.lbl_26 = QLabel('Recent Files')
        self.lbl_26.setStyleSheet('font-size: 15px;')
        self.lbl_27 = QLabel('Ctrl')
        self.lbl_27.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_27.setObjectName('button')
        self.lbl_28 = QLabel('H')
        self.lbl_28.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_28.setObjectName('button')

        self.lbl_29 = QLabel('PDF View')
        self.lbl_29.setStyleSheet('font-size: 15px;')
        self.lbl_30 = QLabel('Ctrl')
        self.lbl_30.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_30.setObjectName('button')
        self.lbl_31 = QLabel('V')
        self.lbl_31.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_31.setObjectName('button')

        self.lbl_32 = QLabel('Next File')
        self.lbl_32.setStyleSheet('font-size: 15px;')
        self.lbl_33 = QLabel('Ctrl')
        self.lbl_33.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_33.setObjectName('button')
        self.lbl_34 = QLabel('Right')
        self.lbl_34.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_34.setObjectName('button')

        self.lbl_35 = QLabel('Previous File')
        self.lbl_35.setStyleSheet('font-size: 15px;')
        self.lbl_36 = QLabel('Ctrl')
        self.lbl_36.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_36.setObjectName('button')
        self.lbl_37 = QLabel('Left')
        self.lbl_37.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_37.setObjectName('button')

        self.lbl_38 = QLabel('Next Page')
        self.lbl_38.setStyleSheet('font-size: 15px;')
        self.lbl_39 = QLabel('Right')
        self.lbl_39.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_39.setObjectName('button')

        self.lbl_40 = QLabel('Previous Page')
        self.lbl_40.setStyleSheet('font-size: 15px;')
        self.lbl_41 = QLabel('Left')
        self.lbl_41.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_41.setObjectName('button')

        self.grid_lay = QGridLayout()
        self.grid_lay.addWidget(self.lbl_6, 0, 0, 4, 1)
        self.grid_lay.addWidget(self.lbl_7, 0, 1)
        self.grid_lay.addWidget(self.lbl_8, 1, 1)
        self.grid_lay.addWidget(self.lbl_9, 2, 1)
        self.grid_lay.addWidget(self.lbl_10, 3, 1)

        self.short_lay = QGridLayout()
        self.short_lay.addWidget(self.lbl_11, 0, 0)
        self.short_lay.addWidget(self.lbl_12, 0, 2)
        self.short_lay.addWidget(self.lbl_13, 1, 0)
        self.short_lay.addWidget(self.lbl_14, 1, 2)
        self.short_lay.addWidget(self.lbl_15, 2, 0)
        self.short_lay.addWidget(self.lbl_16, 2, 1)
        self.short_lay.addWidget(self.lbl_17, 2, 2)
        self.short_lay.addWidget(self.lbl_18, 3, 0)
        self.short_lay.addWidget(self.lbl_19, 3, 2)
        self.short_lay.addWidget(self.lbl_20, 4, 0)
        self.short_lay.addWidget(self.lbl_21, 4, 1)
        self.short_lay.addWidget(self.lbl_22, 4, 2)
        self.short_lay.addWidget(self.lbl_23, 5, 0)
        self.short_lay.addWidget(self.lbl_24, 5, 1)
        self.short_lay.addWidget(self.lbl_25, 5, 2)
        self.short_lay.addWidget(self.lbl_26, 6, 0)
        self.short_lay.addWidget(self.lbl_27, 6, 1)
        self.short_lay.addWidget(self.lbl_28, 6, 2)
        self.short_lay.addWidget(self.lbl_29, 7, 0)
        self.short_lay.addWidget(self.lbl_30, 7, 1)
        self.short_lay.addWidget(self.lbl_31, 7, 2)
        self.short_lay.addWidget(self.lbl_32, 8, 0)
        self.short_lay.addWidget(self.lbl_33, 8, 1)
        self.short_lay.addWidget(self.lbl_34, 8, 2)
        self.short_lay.addWidget(self.lbl_35, 9, 0)
        self.short_lay.addWidget(self.lbl_36, 9, 1)
        self.short_lay.addWidget(self.lbl_37, 9, 2)
        self.short_lay.addWidget(self.lbl_38, 10, 0)
        self.short_lay.addWidget(self.lbl_39, 10, 2)
        self.short_lay.addWidget(self.lbl_40, 11, 0)
        self.short_lay.addWidget(self.lbl_41, 11, 2)

        self.short_wdj = QWidget()
        self.short_wdj.setLayout(self.short_lay)
        self.short_wdj.setVisible(False)

        self.grid_wdj = QWidget()
        self.grid_wdj.setLayout(self.grid_lay)
        self.grid_wdj.setVisible(False)

        self.appearanceStack = QGridLayout()
        self.appearanceStack.setSpacing(10)
        self.appearanceStack.addWidget(self.gap, 0, 1, 3, 1)
        self.appearanceStack.addWidget(self.gap_1, 0, 3, 3, 1)
        self.appearanceStack.addWidget(self.gap_2, 0, 5, 3, 1)
        self.appearanceStack.addWidget(self.lbl_1, 0, 0)
        self.appearanceStack.addWidget(self.checkOne, 0, 2)
        self.appearanceStack.addWidget(self.checkTwo, 0, 4)
        self.appearanceStack.addWidget(self.lbl_2, 1, 0)
        self.appearanceStack.addWidget(self.checkThree, 1, 2)
        self.appearanceStack.addWidget(self.checkFour, 1, 4)
        self.appearanceStack.addWidget(self.lbl_3, 2, 0)
        self.appearanceStack.addWidget(self.checkFive, 2, 2)
        self.appearanceStack.addWidget(self.checkSix, 2, 4)
        self.appearanceStack.addWidget(self.lbl_5, 3, 0, 1, 6)
        self.appearanceStack.addWidget(self.checkSeven, 3, 2)
        self.appearanceStack.addWidget(self.checkEight, 3, 4)
        self.appearanceWdj = QWidget(self)
        self.appearanceWdj.setLayout(self.appearanceStack)
        self.appearanceWdj.setVisible(False)

        self.layout.addWidget(self.btn_1)
        self.layout.addWidget(self.appearanceWdj)
        self.layout.addWidget(self.btn_2)
        self.layout.addWidget(self.lbl_4)
        self.layout.addWidget(self.btn_3)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.btn_5)
        self.layout.addWidget(self.short_wdj)
        self.layout.addWidget(self.btn_4)
        self.layout.addWidget(self.grid_wdj)

    def function_one(self):
        if self.lbl_4.isVisible():
            self.function_two()
        if self.list.isVisible():
            self.function_three()
        if self.grid_wdj.isVisible():
            self.function_four()
        if self.short_wdj.isVisible():
            self.function_five()
        if self.appearanceWdj.isVisible():
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 370))
            self.anim_1.setEndValue(QSize(400, 180))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.appearanceWdj.setVisible(False)
        else:
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 180))
            self.anim_1.setEndValue(QSize(400, 370))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.appearanceWdj.setVisible(True)

    def function_two(self):
        if self.appearanceWdj.isVisible():
            self.function_one()
        if self.list.isVisible():
            self.function_three()
        if self.grid_wdj.isVisible():
            self.function_four()
        if self.short_wdj.isVisible():
            self.function_five()
        if self.lbl_4.isVisible():
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 440))
            self.anim_1.setEndValue(QSize(400, 180))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.lbl_4.setVisible(False)
        else:
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 180))
            self.anim_1.setEndValue(QSize(400, 440))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.lbl_4.setVisible(True)

    def function_three(self):
        if self.appearanceWdj.isVisible():
            self.function_one()
        if self.lbl_4.isVisible():
            self.function_two()
        if self.grid_wdj.isVisible():
            self.function_four()
        if self.short_wdj.isVisible():
            self.function_five()
        if self.list.isVisible():
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 400))
            self.anim_1.setEndValue(QSize(400, 180))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.list.setVisible(False)
        else:
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 180))
            self.anim_1.setEndValue(QSize(400, 400))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.list.setVisible(True)

    def function_four(self):
        if self.appearanceWdj.isVisible():
            self.function_one()
        if self.lbl_4.isVisible():
            self.function_two()
        if self.list.isVisible():
            self.function_three()
        if self.short_wdj.isVisible():
            self.function_five()
        if self.grid_wdj.isVisible():
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 330))
            self.anim_1.setEndValue(QSize(400, 180))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.grid_wdj.setVisible(False)
        else:
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 180))
            self.anim_1.setEndValue(QSize(400, 330))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.grid_wdj.setVisible(True)

    def function_five(self):
        if self.appearanceWdj.isVisible():
            self.function_one()
        if self.lbl_4.isVisible():
            self.function_two()
        if self.list.isVisible():
            self.function_three()
        if self.grid_wdj.isVisible():
            self.function_four()
        if self.short_wdj.isVisible():
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 540))
            self.anim_1.setEndValue(QSize(400, 180))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.short_wdj.setVisible(False)
        else:
            self.anim_1 = QPropertyAnimation(self, b'size')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QSize(400, 180))
            self.anim_1.setEndValue(QSize(400, 540))
            self.anim_1.setDuration(200)
            self.anim_1.start()
            self.short_wdj.setVisible(True)

    def toolbarButtonToggle(self, event):
        if event == 0:
            vary.window.additionalToolBar.setVisible(True)
            self.checkSeven.setChecked(True)
            self.checkEight.setChecked(False)
            vary.settings[2] = 1
        elif event == 1:
            vary.window.additionalToolBar.setVisible(False)
            self.checkSeven.setChecked(False)
            self.checkEight.setChecked(True)
            vary.settings[2] = 0

    def openRecentFiles(self):
        try:
            vary.file_path = vary.files[self.list.currentRow()]
            vary.current_page = 0
            vary.doc = fitz.open(vary.file_path)
            vary.window.loadPdfFile()
            vary.pages_array = []
            vary.files_array = []
            vary.window.addingPagesThread()
            vary.window.addingFilesThread()
        except:
            vary.files.pop(vary.files.index(vary.file_path))
        text = f'Name: {vary.full_name}\n\n'
        for key, value in vary.doc.metadata.items():
            if key not in ('title', 'subject', 'keywords', 'trapped'):
                text = f'{text}{key.capitalize()}:   {value}\n\n'
        self.lbl_4.setText(text)
        vary.window.toggleMenu()

    def themeChangeAction(self, event):
        vary.theme = event
        palette = vary.window.pdfView.palette()
        if vary.theme == 'dark':
            vary.window.sideBar.setStyleSheet('background: #303030;')
            vary.window.fileBar.setStyleSheet('background: #303030;')
            self.checkOne.setChecked(True)
            self.checkTwo.setChecked(False)
            palette.setBrush(vary.window.pdfView.palette().currentColorGroup(), vary.window.pdfView.palette().ColorRole.Dark,
                             QColor('#3a3a3a'))

        elif vary.theme == 'light':
            vary.window.sideBar.setStyleSheet('background: #F1EDEC;')
            vary.window.fileBar.setStyleSheet('background: #F1EDEC;')
            self.checkTwo.setChecked(True)
            self.checkOne.setChecked(False)
            palette.setBrush(vary.window.pdfView.palette().currentColorGroup(), vary.window.pdfView.palette().ColorRole.Light,
                             QColor('#F6F0F0'))

        vary.window.pdfView.setPalette(palette)

        pywinstyles.apply_style(vary.window, vary.theme)
        txt = open(f'assets/style/{vary.theme}.qss', 'r').read()
        vary.app.setStyleSheet(txt)

        vary.window.fullScreenAction.setIcon(QIcon(f'assets/images/pdf_view_{vary.theme}.png'))
        vary.window.zoomInAction.setIcon(QIcon(f'assets/images/zoom_in_{vary.theme}.png'))
        vary.window.zoomOutAction.setIcon(QIcon(f'assets/images/zoom_out_{vary.theme}.png'))
        vary.window.infoAction.setIcon(QIcon(f'assets/images/info_{vary.theme}.png'))
        vary.window.recentAction.setIcon(QIcon(f'assets/images/recent_{vary.theme}.png'))
        vary.window.sidePaneToggle.setIcon(QIcon(f'assets/images/side_pane_{vary.theme}.png'))
        vary.window.settingAction.setIcon(QIcon(f'assets/images/menu_{vary.theme}.png'))
        vary.window.nextFile.setIcon(QIcon(f'assets/images/next_{vary.theme}.png'))
        vary.window.prevFile.setIcon(QIcon(f'assets/images/prev_{vary.theme}.png'))
        vary.window.nextPage.setIcon(QIcon(f'assets/images/next_pg_{vary.theme}.png'))
        vary.window.prevPage.setIcon(QIcon(f'assets/images/prev_pg_{vary.theme}.png'))

        vary.window.pix = QPixmap(f'assets/images/drag_{vary.theme}.png')
        vary.window.pix = vary.window.pix.scaled(QSize(100, 100))
        vary.window.img.setPixmap(vary.window.pix)

        try:
            vary.files_array[vary.current_file].lbl_1.setStyleSheet('''
                                            background: #3574F0;
                                            border-radius: 5px;
                                            padding: 1px;
                                            ''')
            vary.files_array[vary.current_file].lbl.setStyleSheet('''
                                            background: #3574F0;
                                            border-radius: 5px;
                                            padding: 4px;
                                            ''')

            array = []
            for i in vary.files_array:
                if i != vary.files_array[vary.current_file]:
                    array.append(i)
            for i in array:
                if vary.theme == 'dark':
                    i.lbl_1.setStyleSheet('background: #303030;')
                    i.lbl.setStyleSheet('background: #303030;')
                else:
                    i.lbl_1.setStyleSheet('background: #F1EDEC;')
                    i.lbl.setStyleSheet('background: #F1EDEC;')

            vary.pages_array[vary.current_page].lbl_1.setStyleSheet('''
                                    background: #3574F0;
                                    border-radius: 5px;
                                    padding: 1px;
                                    ''')
            vary.pages_array[vary.current_page].lbl.setStyleSheet('''
                                    background: #3574F0;
                                    border-radius: 5px;
                                    padding: 4px;
                                    ''')
            array = []
            for i in vary.pages_array:
                if i != vary.pages_array[vary.current_page]:
                    array.append(i)
            for i in array:
                if vary.theme == 'dark':
                    i.lbl_1.setStyleSheet('background: #303030;')
                    i.lbl.setStyleSheet('background: #303030;')
                else:
                    i.lbl_1.setStyleSheet('background: #F1EDEC;')
                    i.lbl.setStyleSheet('background: #F1EDEC;')
        except:
            pass

        self.checkOne.setIcon(QIcon(f'assets/images/dark_{vary.theme}.png'))
        self.checkTwo.setIcon(QIcon(f'assets/images/light_{vary.theme}.png'))
        self.checkThree.setIcon(QIcon(f'assets/images/show_{vary.theme}.png'))
        self.checkFour.setIcon(QIcon(f'assets/images/hidden_{vary.theme}.png'))
        self.checkFive.setIcon(QIcon(f'assets/images/show_{vary.theme}.png'))
        self.checkSix.setIcon(QIcon(f'assets/images/hidden_{vary.theme}.png'))
        self.checkSeven.setIcon(QIcon(f'assets/images/show_{vary.theme}.png'))
        self.checkEight.setIcon(QIcon(f'assets/images/hidden_{vary.theme}.png'))

    def toggleInterfaceAction(self, event):
        if event == 0:
            self.checkThree.setChecked(True)
            self.checkFour.setChecked(False)
            vary.window.sideBarWidget.setVisible(True)
        elif event == 1:
            self.checkThree.setChecked(False)
            self.checkFour.setChecked(True)
            vary.window.sideBarWidget.setVisible(False)

        vary.settings[0] = abs(event - 1)

    def toggleInterfaceTwoAction(self, event):
        if event == 0:
            self.checkFive.setChecked(True)
            self.checkSix.setChecked(False)
            vary.window.fileBarWidget.setVisible(True)
        elif event == 1:
            self.checkFive.setChecked(False)
            self.checkSix.setChecked(True)
            vary.window.fileBarWidget.setVisible(False)

        vary.settings[1] = abs(event - 1)


class ListItem(QWidget):
    def __init__(self, *args, **kwargs):
        super(ListItem, self).__init__()

        self.number = 0

        self.setStyleSheet('''
            max-width: 390px;
            max-height: 20px;
            min-width: 390px;
            min-height: 20px;
        ''')

        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.btn = QPushButton()
        self.btn.setStyleSheet('''
            QPushButton {
                max-width: 5px;
                max-height: 5px;
                min-width: 5px;
                min-height: 5px;
                border-radius: 7px;
            }

            QPushButton::hover {
                background-color: #FF2245;
            }

            QPushButton::pressed {
                background-color: #FF636A;
            }
        ''')

        self.lbl.setStyleSheet('''
            max-width: 360px;
            max-height: 20px;
            min-width: 360px;
            min-height: 20px;
        ''')

        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(5, 0, 5, 0)
        self.lay.addWidget(self.lbl)
        self.lay.addWidget(self.btn, 0, Qt.AlignmentFlag.AlignRight)

        self.btn.pressed.connect(lambda: vary.window.closeBtnAction(self.number))


class ViewPanel(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(ViewPanel, self).__init__(parent)
        self.setObjectName('view_panel')
        vary.view = self

        self.btn_one = QPushButton()
        self.btn_one.setIconSize(QSize(20, 20))
        self.btn_one.setObjectName('action_btn')
        self.btn_one.setToolTip('Fit to Page')
        self.btn_one.setIcon(QIcon(f'assets/images/fit_page_{vary.theme}.png'))
        self.btn_one.pressed.connect(lambda: vary.window.pdfViewChanger(1))

        self.btn_two = QPushButton()
        self.btn_two.setIconSize(QSize(20, 20))
        self.btn_two.setObjectName('action_btn')
        self.btn_two.setToolTip('Fit to Width')
        self.btn_two.setIcon(QIcon(f'assets/images/fit_width_{vary.theme}.png'))
        self.btn_two.pressed.connect(lambda: vary.window.pdfViewChanger(2))

        self.btn_three = QPushButton()
        self.btn_three.setIconSize(QSize(20, 20))
        self.btn_three.setObjectName('action_btn')
        self.btn_three.setToolTip('Single Page')
        self.btn_three.setIcon(QIcon(f'assets/images/single_{vary.theme}.png'))
        self.btn_three.pressed.connect(lambda: vary.window.pdfViewChanger(3))

        self.btn_four = QPushButton()
        self.btn_four.setIconSize(QSize(20, 20))
        self.btn_four.setObjectName('action_btn')
        self.btn_four.setToolTip('Multi Page')
        self.btn_four.setIcon(QIcon(f'assets/images/multi_{vary.theme}.png'))
        self.btn_four.pressed.connect(lambda: vary.window.pdfViewChanger(4))

        self.btn_five = QPushButton()
        self.btn_five.setIconSize(QSize(20, 20))
        self.btn_five.setObjectName('action_btn')
        self.btn_five.setToolTip('Toggle Full Screen')
        self.btn_five.setIcon(QIcon(f'assets/images/full_screen_{vary.theme}.png'))
        self.btn_five.pressed.connect(lambda: vary.window.pdfViewChanger(5))

        self.btn_six = QPushButton()
        self.btn_six.setIconSize(QSize(20, 20))
        self.btn_six.setObjectName('action_btn')
        self.btn_six.setToolTip('Fit Normal')
        self.btn_six.setIcon(QIcon(f'assets/images/pdf_view_{vary.theme}.png'))
        self.btn_six.pressed.connect(lambda: vary.window.pdfViewChanger(6))

        self.lay = QHBoxLayout()
        self.lay.addWidget(self.btn_one)
        self.lay.addWidget(self.btn_two)
        self.lay.addWidget(self.btn_six)
        self.lay.addWidget(self.btn_three)
        self.lay.addWidget(self.btn_four)
        self.lay.addWidget(self.btn_five)

        self.setLayout(self.lay)
