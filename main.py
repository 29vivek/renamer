import sys
import os
import re
import api
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class Application(qtw.QApplication):
    
    def __init__(self, argv):
        super().__init__(argv)

        self.mainWindow = MainWindow()
        self.mainWindow.setWindowTitle('Renamer')
        self.mainWindow.setFixedSize(500, 375)
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

        self.episodeNamesCheckBox = qtw.QCheckBox('Also include episode names')
        self.episodeNamesCheckBox.setChecked(False)

        self.separators = {'Space': ' ', 'Period': '.', 'Dash': '-'}
        separatorRadios = []

        for separator in self.separators:
            separatorRadios.append(qtw.QRadioButton(separator))
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

        radioFile = qtw.QRadioButton('Manual info.txt file')
        radioFile.setToolTip('Place episode names in a info.txt file, separated by season numbers and new lines!')
        radioFile.setEnabled(False)
        radioApi = qtw.QRadioButton('TVMaze API')
        radioApi.setChecked(True)
        radioApi.setToolTip('I see you\'re a man of culture :)')
        radioApi.setEnabled(False)

        sourceLayout.addWidget(radioFile)
        sourceLayout.addWidget(radioApi)

        self.sourceGroup = qtw.QButtonGroup(self)
        self.sourceGroup.addButton(radioFile, 1)
        self.sourceGroup.addButton(radioApi, 2)

        layout.addLayout(sourceLayout, 5, 1)

        buttonLayout = qtw.QHBoxLayout()
        

        self.startButton = qtw.QPushButton('Lets Go!')
        self.startButton.setToolTip('Say your prayers :D')
        self.startButton.clicked.connect(self.start)

        closeButton = qtw.QPushButton('Close')
        closeButton.setToolTip(':(')
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

        messageBox = qtw.QMessageBox()

        if self.titleInput.text() == '' or self.pathInput.text() == '':
            messageBox.critical(self, 'Failed', 'Title/Path cannot be empty.')
        else:
            overview = []
            info = None

            chosenSeparator = self.separatorGroup.checkedButton().text()
            includeNames = self.episodeNamesCheckBox.isChecked()
            if includeNames:
                sourceId = self.sourceGroup.checkedId()
            else:
                sourceId = 0

            overview.append(f'chosen separator: {chosenSeparator}')
            overview.append(f'chosen to {"include" if includeNames else "exclude"} episode names.')
            
            if includeNames:
                pathToFile = os.path.join(self.pathInput.text(), 'info.txt')
                if sourceId == 1:
                    # find info.txt file in root directory mentioned and load data onto info.
                    try:
                        info = self.readInfoFromFile(pathToFile)
                        overview.append(f'found data for {len(info.keys())} seasons.')
                    except:
                        messageBox.critical(self, 'Failed', 'File info.txt not found in root directory.')
                        return
    
                else:
                    info = api.getDataFor(self.titleInput.text())
                    if info['status'] == 1:
                        try:
                            for key in ['name', 'language', 'genres', 'premiered']:
                                overview.append(f'{key}: {info[key]}')
                            
                            # take off unnecessary information
                            info = info['episodes']
                            overview.append(f'found data for {len(info.keys())} seasons.')
                            self.writeInfoToFile(pathToFile, info)
                        
                        except:
                            messageBox.critical(self, 'Failed', 'Root directory probably doesn\'t exist.')
                            return
                    else:
                        messageBox.critical(self, 'Failed', 'Bad input/network connection. You could always try again.')
                        return
            
            # print(info)

            subfoldersPathSorted = self.sortedAlphanumeric([f.path for f in os.scandir(self.pathInput.text()) if f.is_dir()])
            # print(subfoldersPathSorted)

            overview.append(f'found {len(subfoldersPathSorted)} folders in root path: {self.pathInput.text()}')
            overview.append('DO YOU WISH TO CONTINUE?')

            confirmation = messageBox.question(self, 'Details', '\n'.join(overview), messageBox.Yes, messageBox.No)

            if confirmation == messageBox.Yes:
                # make the UI show a busy indicator or something here
                
                self.rename(
                    title = os.path.basename(self.pathInput.text()),
                    subfolders=subfoldersPathSorted,
                    info=info,
                    separator=self.separators[chosenSeparator]
                )

            else:
                messageBox.information(self, 'Alert', 'Operation Cancelled.')


    def rename(self, title, subfolders, info, separator):

        progress = qtw.QProgressDialog(self)
        progress.setWindowModality(qtc.Qt.WindowModal)
        progress.setWindowTitle('Hang in there')
        progress.setLabel(qtw.QLabel("Doing some magic..."))
        # enable custom window hint
        progress.setWindowFlags(progress.windowFlags() | qtc.Qt.CustomizeWindowHint)
        # disable (but not hide) close button
        progress.setWindowFlags(progress.windowFlags() & ~qtc.Qt.WindowCloseButtonHint)
        # remove the cancel button
        progress.setCancelButton(None)
        progress.setAutoClose(True)

        progress.setMaximum(len(subfolders))
        
        videoExtensions = ['.mp4', '.mkv', '.avi']

        for i, folder in enumerate(subfolders):
            progress.setValue(i)
             
            filesInFolder = os.listdir(folder)
            videos = self.sortedAlphanumeric([file_ for file_ in filesInFolder if os.path.splitext(file_)[1] in videoExtensions])
            
            if info is not None:
                expectedEpisodes = len(info[f'Season {i+1}'].keys())
                if len(videos) != expectedEpisodes:
                    qtw.QMessageBox.critical(self, 'Failed', f'Mismatch in Season {i+1}. Didn\'t find expected number of episodes ({expectedEpisodes})')
                    return
            
            # get list of videos in folder. for a given video, if subtitle with same name exists, rename subtitle too, else don't bother.
            
            template = '{title} {which} {name}{extension}' if info is not None else '{title} {which}{extension}'
            for j, video in enumerate(videos):
                
                newName = separator.join(template.format(title=title, which=f'S{i+1:02d}E{j+1:02d}', name=info[f'Season {i+1}'][j+1] if info is not None else '', extension=os.path.splitext(video)[1]).split(' '))
                # print(f'{j+1}: {os.path.join(folder, video)}')
                # print(newName)

                os.rename(os.path.join(folder, video), os.path.join(folder, newName))

                fileName, _ = os.path.splitext(video)
                if os.path.isfile(os.path.join(folder, fileName + '.srt')):
                    newFileName, _ = os.path.splitext(newName)
                    os.rename(os.path.join(folder, fileName + '.srt'), os.path.join(folder, newFileName + '.srt'))
  
            
        progress.setValue(len(subfolders))
        

    def namesChecked(self):
        separator = self.separators[self.separatorGroup.checkedButton().text()]
        includeNames = self.episodeNamesCheckBox.isChecked()
        self.exampleText.setText(self.exampleString.format(separator, separator, name=(f'{separator}Pilot') if includeNames else ''))
        
        self.sourceText.setEnabled(includeNames)
        for radio in self.sourceGroup.buttons():
            radio.setEnabled(includeNames)     
        
    def separatorToggled(self):

        radioButton = self.sender()
        separator = self.separators[radioButton.text()]
        if radioButton.isChecked():
            self.exampleText.setText(self.exampleString.format(separator, separator, name=(f'{separator}Pilot') if self.episodeNamesCheckBox.isChecked() else ''))

    @staticmethod
    def sortedAlphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanumKey = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(data, key=alphanumKey)

    @staticmethod
    def readInfoFromFile(path):
        info = {}
        lines = []
        with open(path, 'r') as file_:
            lines = file_.readlines()

        # print(os.path.basename(os.path.dirname(path)))
        seasonSeparators = [i for i, x in enumerate(lines) if x.startswith(('Season', 'season', os.path.basename(os.path.dirname(path))))]
        for i, index in enumerate(seasonSeparators):
            info[f'Season {i+1}'] = ({j+1: name.strip('\n') for j, name in enumerate(lines[index+1:seasonSeparators[i+1]])}) if i+1 < len(seasonSeparators) else ({j+1: name.strip('\n') for j, name in enumerate(lines[index+1:])})

        return info

    @staticmethod
    def writeInfoToFile(path, info):
        lines = []
        for season in info:
            # whichSeason = re.findall(r'\d+', season)[0]
            lines.append(season + '\n')
            for episode in info[season]:
                lines.append(info[season][episode] + '\n')
        
        with open(path, 'w+') as file_:
            file_.writelines(lines)
        

if __name__ == '__main__':

    app = Application(sys.argv)
    sys.exit(app.exec_())