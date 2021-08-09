import os
import sys
import shutil
import numpy as np
import wavio
from PyQt5 import QtWidgets, uic
from pydub import AudioSegment
from scipy.io import wavfile


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        uic.loadUi("gui.ui", self)

        self.browse.clicked.connect(self.browsefiles)
        self.tableWidget.setColumnWidth(0, 220)
        self.tableWidget.setColumnWidth(1, 75)
        self.tableWidget2.setColumnWidth(0, 300)
        self.convert.clicked.connect(self.checkReady_convertfiles)
        self.output.clicked.connect(self.selectOutputFolder)
        self.check.clicked.connect(self.checkReady_checkbefore)

        # De to "ready"-check variabler
        global checkBrowse
        checkBrowse = 0
        global checkOutput
        checkOutput = 0

    # "ready"-check inden convertfiles. Kræver både output-folder og browse.
    def checkReady_convertfiles(self):
        if checkBrowse == 1 and checkOutput == 1:
            self.convertfiles()
        else:
            pass

    # "ready"-check inden checkbefore. Kræver kun browse.
    def checkReady_checkbefore(self):
        if checkBrowse == 1:
            self.checkbefore()
        else:
            pass

    # Omskriver filstørrelser til læselige formater.
    def humansize(self, nbytes):

        suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0

        while nbytes >= 1024 and i < len(suffixes) - 1:
            nbytes /= 1024.0
            i += 1

        f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
        return "%s %s" % (f, suffixes[i])

    # Vælg filer til konvertering og hent navn, sti og filstørrelse
    def browsefiles(self):

        # Aktivér "ready"-check for browse
        global checkBrowse
        checkBrowse = 1

        # Declare variabler så de andre funktioner kan hente filnavne
        global filenames
        global filenamesShort

        # Selve browse-funktionen
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setNameFilters(["Wav files (*.wav)"])

        if dialog.exec():
            filenames = dialog.selectedFiles()

        # Forkort filnavne så man kun får den sidste bid af stien og ikke hele stien
        filenamesShort = [i.split("/")[-1] for i in filenames]

        row = 0
        self.tableWidget.setRowCount(len(filenames))

        # counter til at increment hvilken fil der skal findes størrelse på
        x = 0

        for i in filenamesShort:
            # indsæt forkortet filnavn i listen
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(i))

            # find filstørrelse og indsæt i listen
            size = os.path.getsize(str(filenames[x]))
            size = self.humansize(size)
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(size)))

            row = row + 1
            x = x + 1

    #  Tjek om filen er mono eller stereo før konvertering.
    # ? Funktion ligegyldig for brugeren?
    def checkbefore(self):
        row = 0
        self.tableWidget2.setRowCount(len(filenames))

        for i in range(len(filenames)):
            faudio = AudioSegment.from_file(filenames[i])

            if faudio.channels > 1:
                self.tableWidget2.setItem(
                    row, 0, QtWidgets.QTableWidgetItem("File seems Stereo")
                )
            else:
                self.tableWidget2.setItem(
                    row, 0, QtWidgets.QTableWidgetItem("Mono (No conversion")
                )
            row = row + 1

    #! KONVERTERING SKER HER - COMMENT SKAL OPDATERES
    def convertfiles(self):

        loopCount = 0
        counter = 0

        for x in filenames:

            rate, data = wavfile.read(x)

            faudio = AudioSegment.from_file(filenames[loopCount])

            if faudio.channels <= 1:
                print("MONO")

                shutil.copy2(
                    (str(filenames[loopCount])),
                    (str(outputFolder) + "/" + str(filenamesShort[loopCount])),
                )
                loopCount = loopCount + 1
                continue

            length = len(data[:, 0])

            for i in range(length):
                if data[i, 0] != data[i, 1]:
                    counter = counter + 1

            equalSamples = length - counter
            equalSamplesPercent = equalSamples / length * 100

            # ? Her sker sorteringen af filerne efter fastsat procentsats.
            # ? Denne kan og bør justeres senere.

            if equalSamplesPercent > 95:

                left = data[:, 0]
                # right = data[:, 1]

                wavio.write(
                    str(outputFolder) + "/" + str(filenamesShort[loopCount]),
                    left,
                    rate,
                    sampwidth=3,
                )

                loopCount = loopCount + 1

            else:

                # Kopier original stereofil til output-folder

                shutil.copy2(
                    (str(filenames[loopCount])),
                    (str(outputFolder) + "/" + str(filenamesShort[loopCount])),
                )

                loopCount = loopCount + 1

            # TODO Få den højre liste til at vise, hvilke filer er blevet konverterede.

    # Vælg output-folder
    def selectOutputFolder(self):

        # Aktivér "ready"-check for output-folder
        global checkOutput
        checkOutput = 1

        global outputFolder
        outputFolder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        self.output.setText(outputFolder)


# ? Eventuelt med gainjustering, for at kompensere for tab af volume?


# System
app = QtWidgets.QApplication(sys.argv)
mainwindow = Ui()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.show()
sys.exit(app.exec_())
