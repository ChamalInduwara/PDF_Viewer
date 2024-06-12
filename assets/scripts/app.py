import sys
import fitz
import os
import time
import winreg
import pywinstyles
import assets.scripts.variables as vary
import assets.scripts.pop_ups as pop

from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPdf import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *


class AddingPreviews(QObject):
    finished = Signal()
    progress = Signal(int)

    def run(self):
        for i in range(vary.doc.page_count):
            time.sleep(0.005)
            try:
                self.progress.emit(i)
            except Exception as e:
                print(e)

        self.finished.emit()


class AddingFiles(QObject):
    finished = Signal()
    progress = Signal(int)

    def run(self):
        for i in range(len(vary.file_paths)):
            time.sleep(0.005)
            try:
                self.progress.emit(i)
            except Exception as e:
                print(e)

        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        vary.window = self
        self.setWindowTitle('PDF Viewer')
        self.setWindowIcon(QIcon('assets/images/icon.ico'))
        self.setGeometry(vary.x, 50, vary.width, vary.height)
        self.setAcceptDrops(True)
        self.container = QWidget(self)
        self.setWidgets()
        self.last_x, self.last_y = None, None

    def setWidgets(self):
        self.toolBar = QToolBar()
        self.toolBar.setIconSize(QSize(20, 20))
        self.toolBar.setMovable(False)
        self.addToolBar(self.toolBar)

        self.additionalToolBar = QToolBar()
        self.additionalToolBar.setIconSize(QSize(15, 15))
        self.additionalToolBar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.additionalToolBar)

        self.gap_Wdj_1 = QWidget()
        self.gap_Wdj_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gap_Wdj_6 = QWidget()
        self.gap_Wdj_6.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gap_Wdj_7 = QLabel('    ')

        self.zoomInAction = QAction(QIcon(f'assets/images/zoom_in_{vary.theme}.png'), 'Zoom In')
        self.zoomInAction.setShortcut(QKeySequence('+'))
        self.zoomInAction.triggered.connect(lambda: self.zoomAction(0))

        self.zoomOutAction = QAction(QIcon(f'assets/images/zoom_out_{vary.theme}.png'), 'Zoom Out')
        self.zoomOutAction.setShortcut(QKeySequence('-'))
        self.zoomOutAction.triggered.connect(lambda: self.zoomAction(1))

        self.fileName = QLabel()
        self.fileName.setObjectName('title')
        self.fileName.setText('PDF Viewer')

        self.pgNumLabel = QLabel()
        self.pgNumLabel.setObjectName('pageNum')
        self.pgNumLabel.setText('Page 0 of 0')
        self.pgNumLabel.mouseReleaseEvent = lambda x: self.goToPageAction()

        self.wdj_lay = QVBoxLayout()
        self.wdj_lay.addWidget(self.fileName)
        self.wdj_lay.addWidget(self.pgNumLabel)

        self.wdj = QWidget(self)
        self.wdj.setLayout(self.wdj_lay)

        self.sidePaneToggle = QAction(QIcon(f'assets/images/side_pane_{vary.theme}.png'), 'Toggle panes')
        self.sidePaneToggle.setShortcut(QKeySequence('ctrl+s'))
        self.sidePaneToggle.triggered.connect(self.paneToggleAction)

        self.closeAction = QAction(QIcon(f'assets/images/close.png'), 'Close Current File')
        self.closeAction.setShortcut(QKeySequence('esc'))
        self.closeAction.triggered.connect(lambda: self.closeFiles(vary.current_file))

        self.progressBar = QProgressBar(self)
        self.progressBar.setTextVisible(False)

        self.settingAction = QAction(QIcon(f'assets/images/menu_{vary.theme}.png'), 'Open Menu')
        self.settingAction.setShortcut(QKeySequence('ctrl+m'))
        self.settingAction.triggered.connect(self.toggleMenu)

        self.infoAction = QAction(QIcon(f'assets/images/info_{vary.theme}.png'), 'Document Information')
        self.infoAction.setShortcut(QKeySequence('ctrl+i'))
        self.infoAction.triggered.connect(self.infoPaneToggle)

        self.recentAction = QAction(QIcon(f'assets/images/recent_{vary.theme}.png'), 'Recent Files')
        self.recentAction.setShortcut(QKeySequence('ctrl+h'))
        self.recentAction.triggered.connect(self.recentPaneToggle)

        self.fullScreenAction = QAction(QIcon(f'assets/images/pdf_view_{vary.theme}.png'), 'PDF View')
        self.fullScreenAction.setShortcut(QKeySequence('ctrl+v'))
        self.fullScreenAction.triggered.connect(self.pdfViewActionHandler)

        self.nextFile = QAction(QIcon(f'assets/images/next_{vary.theme}.png'), 'Next File')
        self.nextFile.setShortcut(QKeySequence('ctrl + right'))
        self.nextFile.triggered.connect(lambda: self.nextPrevAction(0))

        self.nextPage = QAction(QIcon(f'assets/images/next_pg_{vary.theme}.png'), 'Next Page')
        self.nextPage.setShortcut(QKeySequence('right'))
        self.nextPage.triggered.connect(lambda: self.nextPrevPgAction(0))

        self.prevFile = QAction(QIcon(f'assets/images/prev_{vary.theme}.png'), 'Previous File')
        self.prevFile.setShortcut(QKeySequence('ctrl + left'))
        self.prevFile.triggered.connect(lambda: self.nextPrevAction(1))

        self.prevPage = QAction(QIcon(f'assets/images/prev_pg_{vary.theme}.png'), 'Previous Page')
        self.prevPage.setShortcut(QKeySequence('left'))
        self.prevPage.triggered.connect(lambda: self.nextPrevPgAction(1))

        self.toolBar.addAction(self.sidePaneToggle)
        self.toolBar.addWidget(self.wdj)
        self.toolBar.addWidget(self.gap_Wdj_1)
        self.toolBar.addAction(self.infoAction)
        self.toolBar.addAction(self.zoomInAction)
        self.toolBar.addAction(self.zoomOutAction)
        self.toolBar.addAction(self.settingAction)

        self.additionalToolBar.addWidget(self.gap_Wdj_7)
        self.additionalToolBar.addWidget(self.progressBar)
        self.additionalToolBar.addWidget(self.gap_Wdj_6)
        self.additionalToolBar.addAction(self.prevFile)
        self.additionalToolBar.addAction(self.prevPage)
        self.additionalToolBar.addAction(self.nextPage)
        self.additionalToolBar.addAction(self.nextFile)
        self.additionalToolBar.addAction(self.closeAction)
        self.additionalToolBar.addAction(self.recentAction)
        self.additionalToolBar.addAction(self.fullScreenAction)

        self.sideBarWidget = QWidget(self)
        self.sideBarWidget.setObjectName('widget')
        self.widget_one_lay = QVBoxLayout()

        self.lbl_one = QLabel('Pages')
        self.lbl_one.setObjectName('topic_lbl')
        self.lbl_one.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sideBar = QScrollArea(self)
        self.sideBar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sideBar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sideBar.setObjectName('preview_lay')
        self.sideBarScroll = self.sideBar.verticalScrollBar()

        self.widget_one_lay.addWidget(self.lbl_one)
        self.widget_one_lay.addWidget(self.sideBar)
        self.sideBarWidget.setLayout(self.widget_one_lay)

        self.fileBarWidget = QWidget(self)
        self.fileBarWidget.setObjectName('widget')
        self.widget_two_lay = QVBoxLayout()

        self.lbl_two = QLabel('Files')
        self.lbl_two.setObjectName('topic_lbl')
        self.lbl_two.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.fileBar = QScrollArea(self)
        self.fileBar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fileBar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fileBar.setObjectName('preview_lay')
        self.fileBarScroll = self.fileBar.verticalScrollBar()

        self.widget_two_lay.addWidget(self.lbl_two)
        self.widget_two_lay.addWidget(self.fileBar)
        self.fileBarWidget.setLayout(self.widget_two_lay)

        list = [
            self.sideBarWidget, self.fileBarWidget, self.additionalToolBar
        ]

        for i in range(len(vary.settings)):
            if vary.settings[i] == 0:
                list[i].setVisible(False)
            elif vary.settings[i] == 1:
                list[i].setVisible(True)

        if vary.theme == 'dark':
            self.sideBar.setStyleSheet('background: #303030;')
            self.fileBar.setStyleSheet('background: #303030;')

        elif vary.theme == 'light':
            self.fileBar.setStyleSheet('background: #F1EDEC;')
            self.sideBar.setStyleSheet('background: #F1EDEC;')

        self.document = QPdfDocument(self)
        self.pdfView = QPdfView(self)
        self.pdfView.setDocument(self.document)
        self.pdfView.setPageMode(QPdfView.PageMode.MultiPage)
        num = self.pdfView.zoomFactor() * 1.01
        self.pdfView.setZoomFactor(num)
        palette = self.pdfView.palette()
        if vary.theme == 'dark':
            palette.setBrush(self.pdfView.palette().currentColorGroup(), self.pdfView.palette().ColorRole.Dark,
                             QColor('#3a3a3a'))
        else:
            palette.setBrush(self.pdfView.palette().currentColorGroup(), self.pdfView.palette().ColorRole.Light,
                             QColor('#f2f2f2'))
        self.pdfView.setStyleSheet('border: 0px;')
        self.pdfView.setPalette(palette)
        self.pdfView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pdfView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.sideBarWidget)
        self.layout.addWidget(self.pdfView)
        self.layout.addWidget(self.fileBarWidget)

        self.pdf_wdj = QWidget()
        self.pdf_wdj.setLayout(self.layout)

        self.title = QLabel('Welcome')
        self.title.setObjectName('wlc')
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel('Recently Opened Files')
        self.label.setObjectName('title')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pix = QPixmap(f'assets/images/drag_{vary.theme}.png')
        self.pix = self.pix.scaled(QSize(100, 100))

        self.img = QLabel()
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img.mouseReleaseEvent = lambda x: self.openFileAction()
        self.img.setPixmap(self.pix)

        self.lbl = QLabel('<b>Drag</b> Files or <b>Click</b> to Open New File')
        self.lbl.mouseReleaseEvent = lambda x: self.openFileAction()
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet('font-size: 15px;')

        self.lbl_1 = QLabel('     Clear Recent')
        self.lbl_1.mouseReleaseEvent = lambda x: self.clearRecent()

        self.recentWdj = QListWidget()
        self.recentWdj.setObjectName('list')
        self.recentWdj.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recentWdj.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recentWdj.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.recentWdj.setStyleSheet(
            'min-width: 400px; max-width: 400px; min-height: 350px; max-height: 350px;'
        )
        for i in range(len(vary.files)):
            list_wdj = pop.ListItem()
            list_wdj.number = i
            txt = f'<b>{os.path.basename(vary.files[i]).replace(".pdf", "")}</b> - {vary.files[i].replace(f"/{os.path.basename(vary.files[i])}", "")}'
            list_wdj.lbl.setText(txt)
            item = QListWidgetItem()
            vary.list_array.append(item)
            self.recentWdj.addItem(item)
            self.recentWdj.setItemWidget(item, list_wdj)
        self.recentWdj.currentItemChanged.connect(lambda: self.openFiles(self.recentWdj.currentRow()))

        self.gap_Wdj_2 = QWidget()
        self.gap_Wdj_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gap_Wdj_3 = QWidget()
        self.gap_Wdj_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gap_Wdj_4 = QWidget()
        self.gap_Wdj_4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gap_Wdj_5 = QWidget()
        self.gap_Wdj_5.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.grid_lay = QGridLayout()
        self.grid_lay.addWidget(self.title, 0, 0, 3, 1)
        self.grid_lay.addWidget(self.img, 3, 0)
        self.grid_lay.addWidget(self.lbl, 4, 0)
        self.grid_lay.addWidget(self.gap_Wdj_5, 5, 0, 3, 1)

        self.grid_lay.addWidget(self.gap_Wdj_2, 0, 1, 8, 1)

        self.grid_lay.addWidget(self.gap_Wdj_2, 0, 2)
        self.grid_lay.addWidget(self.label, 1, 2)
        self.grid_lay.addWidget(self.recentWdj, 2, 2, 4, 1)
        self.grid_lay.addWidget(self.lbl_1, 7, 2)
        self.grid_lay.addWidget(self.gap_Wdj_3, 8, 2)

        self.file_wdj = QWidget(self)
        self.file_wdj.setLayout(self.grid_lay)

        self.stack_lay = QStackedLayout()
        self.stack_lay.addWidget(self.file_wdj)
        self.stack_lay.addWidget(self.pdf_wdj)
        self.stack_lay.setCurrentIndex(0)

        self.container.setLayout(self.stack_lay)
        self.setCentralWidget(self.container)

    def nextPrevPgAction(self, num):
        if not vary.doc is None:
            if num == 0:
                vary.current_page += 1
                if vary.current_page > vary.doc.page_count - 1:
                    vary.current_page = vary.doc.page_count - 1
            else:
                vary.current_page -= 1
                if vary.current_page < 0:
                    vary.current_page = 0
            vary.nav.jump(vary.current_page, QPoint(), vary.nav.currentZoom())
            self.changeCurrentPage()

    def nextPrevAction(self, num):
        if not vary.draw:
            try:
                vary.pages_array = []
                vary.files_array = []
                vary.current_page = 0
                self.preview_lay = QVBoxLayout()
                self.wdj = QWidget()
                self.wdj.setLayout(self.preview_lay)
                self.sideBar.setWidget(self.wdj)
                vary.last_page = None
                if num == 0:
                    vary.current_file += 1
                    if vary.current_file > len(vary.file_paths) - 1:
                        vary.current_file = 0
                else:
                    vary.current_file -= 1
                    if vary.current_file < 0:
                        vary.current_file = len(vary.file_paths) - 1
                vary.file_path = vary.file_paths[vary.current_file]
                vary.doc = fitz.open(vary.file_path)
                self.loadPdfFile()
                self.addingPagesThread()
                self.addingFilesThread()
            except:
                pass

    def closeFiles(self, num):
        try:
            vary.file_paths.pop(num)
            vary.pages_array = []
            vary.files_array = []
            vary.current_page = 0
            self.preview_lay = QVBoxLayout()
            self.wdj = QWidget()
            self.wdj.setLayout(self.preview_lay)
            self.sideBar.setWidget(self.wdj)
            vary.last_page = None

            if len(vary.file_paths) != 0:
                vary.file_path = vary.file_paths[-1]
                vary.doc = fitz.open(vary.file_path)
                vary.current_file = len(vary.file_paths) - 1
                self.loadPdfFile()
                self.addingPagesThread()
                self.addingFilesThread()
            else:
                vary.open = False
                vary.files.clear()

                try:
                    for i in range(12):
                        vary.files.append(vary.list[i])
                except:
                    pass

                self.recentWdj.clear()
                vary.current_file = -1
                for i in range(len(vary.files)):
                    list_wdj = pop.ListItem()
                    list_wdj.number = i
                    txt = f'<b>{os.path.basename(vary.files[i]).replace(".pdf", "")}</b> - {vary.files[i].replace(f"/{os.path.basename(vary.files[i])}", "")}'
                    list_wdj.lbl.setText(txt)
                    item = QListWidgetItem()
                    vary.list_array.append(item)
                    self.recentWdj.addItem(item)
                    self.recentWdj.setItemWidget(item, list_wdj)
                vary.file_paths = []
                vary.file_path = None
                vary.doc = None
                self.stack_lay.setCurrentIndex(0)
                self.fileName.setText('PDF Viewer')
                self.pgNumLabel.setText(f'Page 0 of 0')
        except:
            pass

    def closeBtnAction(self, num):
        text = vary.files[num]
        vary.files.clear()
        vary.list.pop(vary.list.index(text))

        try:
            for i in range(12):
                vary.files.append(vary.list[i])
        except:
            pass

        self.recentWdj.clear()
        for i in range(len(vary.files)):
            list_wdj = pop.ListItem()
            list_wdj.number = i
            txt = f'<b>{os.path.basename(vary.files[i]).replace(".pdf", "")}</b> - {vary.files[i].replace(f"/{os.path.basename(vary.files[i])}", "")}'
            list_wdj.lbl.setText(txt)
            item = QListWidgetItem()
            vary.list_array.append(item)
            self.recentWdj.addItem(item)
            self.recentWdj.setItemWidget(item, list_wdj)

    def changeCurrentPage(self):
        try:
            if vary.last_page is not None:
                if vary.theme == 'dark':
                    vary.last_page.lbl_1.setStyleSheet('background: #303030;')
                    vary.last_page.lbl.setStyleSheet('background: #303030;')
                else:
                    vary.last_page.lbl_1.setStyleSheet('background: #F1EDEC;')
                    vary.last_page.lbl.setStyleSheet('background: #F1EDEC;')

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
            vary.last_page = vary.pages_array[vary.current_page]
            scroll = (vary.current_page * 190) - (vary.current_page * ((1.01) ** vary.current_page))
            self.sideBarScroll.setValue(scroll)
        except:
            pass

    def changeCurrentFile(self):
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

            self.fileBarScroll.setValue(vary.current_file * 160)
        except:
            pass

    def clearRecent(self):
        vary.files.clear()
        vary.list.clear()
        self.recentWdj.clear()

    def closeUnnecassaryWindows(self):
        if vary.time == 1:
            self.widget.close()
            vary.time = 0
        if vary.time_1 == 1:
            self.widget_1.close()
            vary.time_1 = 0
        if vary.time_2 == 1:
            self.widget_two.close()
            vary.time_2 = 0
        if vary.time_3 == 1:
            self.widget_three.close()
            vary.time_3 = 0
        if vary.time_4 == 1:
            self.widget_four.close()
            vary.time_4 = 0
        if vary.time_5 == 1:
            self.widget_five.close()
            vary.time_5 = 0

    def pdfViewChanger(self, num):
        if num == 1:
            self.pdfView.setZoomMode(QPdfView.ZoomMode.FitInView)
        elif num == 2:
            self.pdfView.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        elif num == 6:
            self.pdfView.setZoomMode(QPdfView.ZoomMode.Custom)
        elif num == 3:
            self.pdfView.setPageMode(QPdfView.PageMode.SinglePage)
        elif num == 4:
            self.pdfView.setPageMode(QPdfView.PageMode.MultiPage)
        elif num == 5:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        self.pdfViewActionHandler()

    def pdfViewActionHandler(self):
        if vary.time == 1:
            self.widget.close()
            vary.time = 0
        if vary.time_1 == 1:
            self.widget_1.close()
            vary.time_1 = 0
        if vary.time_2 == 1:
            self.widget_two.close()
            vary.time_2 = 0
        if vary.time_3 == 1:
            self.widget_three.close()
            vary.time_3 = 0
        if vary.time_4 == 1:
            self.widget_four.close()
            vary.time_4 = 0

        if vary.time_5 == 0:
            self.widget_five = pop.ViewPanel(self.container)
            self.widget_five.setVisible(True)

            self.anim_5 = QPropertyAnimation(self.widget_five, b'pos')
            self.anim_5.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_5.setStartValue(QPoint(vary.width - 260, vary.height + 165))
            self.anim_5.setEndValue(QPoint(vary.width - 260, vary.height - 150))
            self.anim_5.setDuration(300)
            self.anim_5.start()

            vary.time_5 = 1
        elif vary.time_5 == 1:
            self.widget_five.close()
            vary.time_5 = 0

    def openFiles(self, number):
        try:
            vary.file_path = vary.files[number]
            vary.current_page = 0
            vary.doc = fitz.open(vary.file_path)
            vary.current_file = len(vary.file_paths) - 1
            self.preview_lay = QVBoxLayout()
            self.wdj = QWidget()
            self.wdj.setLayout(self.preview_lay)
            self.sideBar.setWidget(self.wdj)
            self.loadPdfFile()
            vary.pages_array = []
            vary.files_array = []
            self.addingPagesThread()
            self.addingFilesThread()
        except:
            pass

    def pageChanger(self):
        vary.current_page = vary.nav.currentPage()
        self.pgNumLabel.setText(f'Page {vary.current_page + 1} of {vary.doc.page_count}')
        self.changeCurrentPage()

    def recentPaneToggle(self):
        if vary.time == 1:
            self.widget.close()
            vary.time = 0
        if vary.time_1 == 1:
            self.widget_1.close()
            vary.time_1 = 0
        if vary.time_2 == 1:
            self.widget_two.close()
            vary.time_2 = 0
        if vary.time_3 == 1:
            self.widget_three.close()
            vary.time_3 = 0
        if vary.time_5 == 1:
            self.widget_five.close()
            vary.time_5 = 0

        if vary.time_4 == 0:
            self.widget_four = pop.RecentWidget(self.container)
            self.widget_four.setVisible(True)

            self.anim_4 = QPropertyAnimation(self.widget_four, b'pos')
            self.anim_4.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_4.setStartValue(QPoint(vary.width - 310, vary.height + 395))
            self.anim_4.setEndValue(QPoint(vary.width - 310, vary.height - 395))
            self.anim_4.setDuration(350)
            self.anim_4.start()

            vary.time_4 = 1
        elif vary.time_4 == 1:
            self.widget_four.close()
            vary.time_4 = 0

    def infoPaneToggle(self):
        if vary.time == 1:
            self.widget.close()
            vary.time = 0
        if vary.time_1 == 1:
            self.widget_1.close()
            vary.time_1 = 0
        if vary.time_2 == 1:
            self.widget_two.close()
            vary.time_2 = 0
        if vary.time_4 == 1:
            self.widget_four.close()
            vary.time_4 = 0
        if vary.time_5 == 1:
            self.widget_five.close()
            vary.time_5 = 0

        if vary.time_3 == 0:
            self.widget_three = pop.InfoWidget(self.container)
            self.widget_three.move(QPoint(vary.width - 310, 5))
            self.widget_three.setVisible(True)

            self.anim_3 = QPropertyAnimation(self.widget_three, b'pos')
            self.anim_3.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_3.setStartValue(QPoint(vary.width - 310, (-200)))
            self.anim_3.setEndValue(QPoint(vary.width - 310, 5))
            self.anim_3.setDuration(250)
            self.anim_3.start()

            vary.time_3 = 1
        elif vary.time_3 == 1:
            self.widget_three.close()
            vary.time_3 = 0

    def toggleMenu(self):
        if vary.time == 1:
            self.widget.close()
            vary.time = 0
        if vary.time_1 == 1:
            self.widget_1.close()
            vary.time_1 = 0
        if vary.time_3 == 1:
            self.widget_three.close()
            vary.time_3 = 0
        if vary.time_4 == 1:
            self.widget_four.close()
            vary.time_4 = 0
        if vary.time_5 == 1:
            self.widget_five.close()
            vary.time_5 = 0

        if vary.time_2 == 0:
            self.widget_two = pop.MenuPanel(self.container)
            self.widget_two.setVisible(True)

            self.anim_2 = QPropertyAnimation(self.widget_two, b'pos')
            self.anim_2.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_2.setStartValue(QPoint(vary.width - 410, (-200)))
            self.anim_2.setEndValue(QPoint(vary.width - 410, 5))
            self.anim_2.setDuration(250)
            self.anim_2.start()

            vary.time_2 = 1
        elif vary.time_2 == 1:
            self.widget_two.close()
            vary.time_2 = 0

    def goToPageAction(self):
        if vary.doc is not None:
            if vary.time_1 == 1:
                self.widget_1.close()
                vary.time_1 = 0
            if vary.time_2 == 1:
                self.widget_two.close()
                vary.time_2 = 0
            if vary.time_3 == 1:
                self.widget_three.close()
                vary.time_3 = 0
            if vary.time_4 == 1:
                self.widget_four.close()
                vary.time_4 = 0
            if vary.time_5 == 1:
                self.widget_five.close()
                vary.time_5 = 0

            if vary.time == 0:
                self.widget = pop.GoToWidget(self.container)
                self.widget.setVisible(True)

                self.anim_2 = QPropertyAnimation(self.widget, b'pos')
                self.anim_2.setEasingCurve(QEasingCurve.Type.InOutCubic)
                self.anim_2.setStartValue(QPoint(20, (-55)))
                self.anim_2.setEndValue(QPoint(20, 5))
                self.anim_2.setDuration(150)
                self.anim_2.start()

                vary.time = 1
            elif vary.time == 1:
                self.widget.close()
                vary.time = 0

    def paneToggleAction(self):
        if vary.time == 1:
            self.widget.close()
            vary.time = 0
        if vary.time_2 == 1:
            self.widget_two.close()
            vary.time_2 = 0
        if vary.time_3 == 1:
            self.widget_three.close()
            vary.time_3 = 0
        if vary.time_4 == 1:
            self.widget_four.close()
            vary.time_4 = 0
        if vary.time_5 == 1:
            self.widget_five.close()
            vary.time_5 = 0

        if vary.time_1 == 0:
            self.widget_1 = pop.TogglePanes(self.container)
            self.widget_1.setVisible(True)

            self.anim_1 = QPropertyAnimation(self.widget_1, b'pos')
            self.anim_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_1.setStartValue(QPoint(5, (-50)))
            self.anim_1.setEndValue(QPoint(5, 5))
            self.anim_1.setDuration(150)
            self.anim_1.start()

            vary.time_1 = 1
        elif vary.time_1 == 1:
            self.widget_1.close()
            vary.time_1 = 0

    def jumpToPages(self, page):
        try:
            vary.current_page = int(page)
            vary.nav.jump(vary.current_page, QPoint(), vary.nav.currentZoom())
            self.changeCurrentPage()
        except:
            pass

    def jumpToFiles(self, number):
        try:
            vary.last_page = None
            vary.file_path = vary.file_paths[number]
            vary.current_page = 0
            vary.doc = fitz.open(vary.file_path)
            vary.current_file = number
            self.changeCurrentFile()
            self.closeUnnecassaryWindows()
            self.preview_lay = QVBoxLayout()
            self.wdj = QWidget()
            self.wdj.setLayout(self.preview_lay)
            self.sideBar.setWidget(self.wdj)
            self.loadPdfFile()
            vary.pages_array = []
            vary.files_array = []
            self.addingPagesThread()
            self.addingFilesThread()
        except:
            pass

    def zoomAction(self, event):
        num = 1.05
        if event == 0:
            factor = self.pdfView.zoomFactor() * num
        elif event == 1:
            factor = self.pdfView.zoomFactor() / num
        self.pdfView.setZoomFactor(factor)
        self.closeUnnecassaryWindows()

    def addingPagesThread(self):
        try:
            self.thread = QThread()
            self.worker = AddingPreviews()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.progressBar.setRange(0, vary.doc.page_count)

            self.worker.progress.connect(self.addingPreviews)
            self.thread.start()

            self.thread.finished.connect(
                lambda: self.progressBar.setValue(0)
            )
        except:
            pass

    def addingFilesThread(self):
        try:
            self.threadOne = QThread()
            self.workerOne = AddingFiles()
            self.workerOne.moveToThread(self.threadOne)
            self.threadOne.started.connect(self.workerOne.run)
            self.workerOne.finished.connect(self.threadOne.quit)
            self.workerOne.finished.connect(self.workerOne.deleteLater)
            self.threadOne.finished.connect(self.threadOne.deleteLater)

            self.progressBar.setRange(0, vary.doc.page_count)

            self.workerOne.progress.connect(self.addingFiles)
            self.threadOne.start()

            self.threadOne.finished.connect(
                lambda: self.progressBar.setValue(0)
            )
        except:
            pass

    def openFileAction(self):
        try:
            self.closeUnnecassaryWindows()
            if not vary.open:
                file_dialog = QFileDialog(self)
                vary.current_page = 0
                vary.current_file = len(vary.file_paths) - 1
                vary.file_path, _ = file_dialog.getOpenFileName(
                    self, "Open PDF File", "D:/", "PDF Files (*.pdf);;All Files (*.*)"
                )
                if vary.file_path != '':
                    try:
                        vary.doc = fitz.open(vary.file_path)
                        vary.current_file = len(vary.file_paths) - 1
                        self.loadPdfFile()
                        vary.pages_array = []
                        vary.files_array = []
                        self.addingPagesThread()
                        self.addingFilesThread()
                    except Exception as e:
                        print(e)
                else:
                    return
        except Exception as e:
            print(e)

    def loadPdfFile(self):
        try:
            vary.open = True
            vary.last_page = None
            self.stack_lay.setCurrentIndex(1)
            vary.nav = self.pdfView.pageNavigator()
            if vary.file_path not in vary.file_paths:
                vary.file_paths.append(vary.file_path)
            if vary.file_path not in vary.files:
                vary.files.append(vary.file_path)
            if vary.file_path not in vary.list:
                ar = []
                for i in vary.list:
                    ar.append(i)
                vary.list.clear()
                vary.list.append(vary.file_path)
                for i in ar:
                    vary.list.append(i)
            if len(vary.files) > 12:
                vary.files = vary.files[1:]

            vary.full_name = os.path.basename(vary.file_path)
            self.fileName.setText(vary.full_name)
            self.pgNumLabel.setText(f'Page {vary.current_page + 1} of {vary.doc.page_count}')
            self.document.load(vary.file_path)
            vary.nav.jump(vary.current_page, QPoint(), vary.nav.currentZoom())
            vary.nav.currentPageChanged.connect(self.pageChanger)

        except:
            vary.open = False

    def addingFiles(self, num):
        try:
            self.preview_lay_one = QVBoxLayout()
            self.wdj_one = QWidget()

            self.progressBar.setValue(num + 1)

            doc = fitz.open(vary.file_paths[num])
            first_pg = doc.load_page(0)
            img = first_pg.get_pixmap()
            page = fitz.Pixmap(img, 0)
            imgdata = page.tobytes('ppm')
            image = QPixmap()
            image.loadFromData(imgdata)
            image = image.scaledToWidth(100)
            widget = pop.FilePreview()
            widget.setPixMap(image)
            vary.files_array.append(widget)
            name = os.path.basename(vary.file_paths[num])
            if len(name) > 16:
                name = f'{os.path.basename(vary.file_paths[num])[0:15]}...'
            widget.setNumber(name)
            widget.number = num

            if num == len(vary.file_paths) - 1:
                for i in vary.files_array:
                    self.preview_lay_one.addWidget(i)
                self.wdj_one.setLayout(self.preview_lay_one)
                self.fileBar.setWidget(self.wdj_one)
                self.changeCurrentFile()
        except:
            pass

    def addingPreviews(self, num):
        try:
            self.preview_lay = QVBoxLayout()
            self.wdj = QWidget()

            self.progressBar.setValue(num + 1)

            first_pg = vary.doc.load_page(num)
            img = first_pg.get_pixmap()
            page = fitz.Pixmap(img, 0)
            imgdata = page.tobytes('ppm')
            image = QPixmap()
            image.loadFromData(imgdata)
            image = image.scaledToWidth(100)
            widget = pop.PagePreview()
            widget.setPixMap(image)
            widget.setNumber(num + 1)
            vary.pages_array.append(widget)

            if num == vary.doc.page_count - 1:
                for i in vary.pages_array:
                    self.preview_lay.addWidget(i)
                self.wdj.setLayout(self.preview_lay)
                self.sideBar.setWidget(self.wdj)
                self.changeCurrentPage()
        except:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        lines = []
        for urls in event.mimeData().urls():
            if '.pdf' in urls.toLocalFile():
                lines.append(urls.toLocalFile())
        try:
            vary.file_paths = vary.file_paths + lines
            vary.file_path = vary.file_paths[len(vary.file_paths) - 1]
            vary.current_page = 0
            vary.current_file = len(vary.file_paths) - 1
            vary.doc = fitz.open(vary.file_path)
            self.loadPdfFile()
            vary.pages_array = []
            vary.files_array = []
            self.addingPagesThread()
            self.addingFilesThread()
        except Exception as e:
            pass

    def resizeEvent(self, event):
        vary.width = self.width()
        vary.height = self.height()
        try:
            self.widget_two.move(QPoint(vary.width - 410, 5))
        except:
            pass
        try:
            self.widget_three.move(QPoint(vary.width - 310, 5))
        except:
            pass
        try:
            self.widget_four.move(QPoint(vary.width - 310, vary.height - 395))
        except:
            pass
        try:
            self.widget_five.move(QPoint(vary.width - 260, vary.height - 150))
        except:
            pass
        text = f'{vary.width}\n{vary.height}'
        file = open('assets/data/winfo.txt', 'w')
        file.write(text)

    def closeEvent(self, event):
        if vary.file_path == '':
            vary.file_path = 'None'
        text = f'{vary.theme}'
        file = open('assets/data/theme.txt', 'w')
        file.write(text)
        text = ''
        for i in vary.list:
            text = f'{text}{i}\n'
        file = open('assets/data/files.txt', 'w')
        file.write(text)
        text = ''
        for i in vary.settings:
            text = f'{text}{i}\n'
        file = open('assets/data/settings.txt', 'w')
        file.write(text)


def main():
    styleSheet = open(f'assets/style/{vary.theme}.qss', 'r').read()
    vary.app = QApplication(sys.argv)
    vary.app.setStyleSheet(styleSheet)
    window = MainWindow()
    pywinstyles.apply_style(window, vary.theme)
    window.show()
    vary.app.exec()
