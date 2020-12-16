# from selenium import webdriver

# PATH = '/home/vivek/selenium/chromedriver'
# driver = webdriver.Chrome(PATH)

# driver.get('https://www.google.com/search?q=breaking+bad+season+1+episodes')

# print(driver.title)
# # driver.quit()

import sys
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class Application(qtw.QApplication):
    
    def __init__(self, argv):
        super().__init__(argv)

        self.mainWindow = MainWindow()
        self.mainWindow.setWindowTitle('Renamer')
        self.mainWindow.setFixedSize(550, 375)
        self.mainWindow.move(150, 100)
        self.mainWindow.show()


class MainWindow(qtw.QWidget):

    def __init__(self):
        super().__init__()

        self.exampleString = 'Breaking{}Bad{}S01E01{name}.mkv'
        self.exampleText = qtw.QLabel(self.exampleString.format(' ', ' ', name=''))

        self.titleInput = qtw.QLineEdit()
        self.pathInput = qtw.QLineEdit()

        browseButton = qtw.QPushButton()
        browseButton.setIcon(qtg.QIcon(qtw.QApplication.style().standardIcon(qtw.QStyle.SP_FileIcon)))
        browseButton.clicked.connect(self.openFolder)

        pickerLayout = qtw.QHBoxLayout()
        pickerLayout.addWidget(self.pathInput)
        pickerLayout.addWidget(browseButton)
        
        layout = qtw.QGridLayout()

        layout.addWidget(qtw.QLabel('Title of Series'), 0, 0)
        layout.addWidget(self.titleInput, 0, 1)
        layout.addWidget(qtw.QLabel('Directory Path'), 1, 0)
        layout.addLayout(pickerLayout, 1, 1)
        
        
        layout.addWidget(qtw.QLabel('Separator'), 2, 0)

        self.episodeNamesCheckBox = qtw.QCheckBox('Get episode names from the web. Will be auto skipped if sources fail.')
        self.episodeNamesCheckBox.setChecked(False)

        separators = {'Space': ' ', 'Period': '.', 'Dash': '-'}
        separatorRadios = []

        for separator in separators:
            separatorRadios.append(qtw.QRadioButton(separator))
            separatorRadios[-1].separator = separators[separator]
            separatorRadios[-1].toggled.connect(self.separatorToggled) 

        separatorRadios[0].setChecked(True)

        self.separatorGroup = qtw.QButtonGroup(self)

        separatorLayout = qtw.QVBoxLayout()

        for i, radio in enumerate(separatorRadios):
            self.separatorGroup.addButton(radio, i)
            separatorLayout.addWidget(radio)    

        layout.addLayout(separatorLayout, 2, 1)

        layout.addWidget(qtw.QLabel('Example'), 3, 0)
        layout.addWidget(self.exampleText, 3, 1)

        
        self.episodeNamesCheckBox.stateChanged.connect(self.namesChecked)
        layout.addWidget(self.episodeNamesCheckBox, 4, 0, 1, -1) # column span of -1

        self.sourceText = qtw.QLabel('Source')
        self.sourceText.setEnabled(False)
        layout.addWidget(self.sourceText, 5, 0)

        sourceLayout = qtw.QVBoxLayout()

        radioApi = qtw.QRadioButton('API')
        radioApi.setChecked(True)
        radioApi.setEnabled(False)
        radioScrape = qtw.QRadioButton('Web Scrape (i see you\'re a man of culture)')
        radioScrape.setEnabled(False)

        sourceLayout.addWidget(radioApi)
        sourceLayout.addWidget(radioScrape)

        self.sourceGroup = qtw.QButtonGroup(self)
        self.sourceGroup.addButton(radioApi, 1)
        self.sourceGroup.addButton(radioScrape, 2)

        layout.addLayout(sourceLayout, 5, 1)

        buttonLayout = qtw.QHBoxLayout()
        

        self.startButton = qtw.QPushButton('Lets Go!')
        self.startButton.setToolTip('Something you never knew you needed.')
        self.startButton.clicked.connect(self.start)

        closeButton = qtw.QPushButton('Close')
        closeButton.clicked.connect(self.close)
        
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(closeButton)

        layout.addLayout(buttonLayout, 6, 0, 1, -1, qtc.Qt.AlignHorizontal_Mask)

        layout.setVerticalSpacing(15)
        layout.setRowStretch(0, 3)

        self.setLayout(layout)
        # Your code ends here

    def openFolder(self):

        folder = qtw.QFileDialog.getExistingDirectory(self, 'Select Directory')
        self.pathInput.setText(folder)


    def start(self):

        if self.titleInput.text() == '' or self.pathInput.text() == '':
            qtw.QMessageBox.critical(self, 'Failed', 'Title/Path cannot be empty')
        else:
            for file in os.listdir(self.pathInput.text()):
                print(file)

    def namesChecked(self):
        separator = self.separatorGroup.checkedButton().separator
        self.exampleText.setText(self.exampleString.format(separator, separator, name=(f'{separator}Pilot') if self.episodeNamesCheckBox.isChecked() else ''))
        
        self.sourceText.setEnabled(self.episodeNamesCheckBox.isChecked())
        for radio in self.sourceGroup.buttons():
            radio.setEnabled(self.episodeNamesCheckBox.isChecked())     
        
    def separatorToggled(self):

        radioButton = self.sender()
        if radioButton.isChecked():
            self.exampleText.setText(self.exampleString.format(radioButton.separator, radioButton.separator, name=(f'{radioButton.separator}Pilot') if self.episodeNamesCheckBox.isChecked() else ''))


if __name__ == '__main__':

    app = Application(sys.argv)
    sys.exit(app.exec_())