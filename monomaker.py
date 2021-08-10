# MonoMaker by MMMIX - 2021


# TODO Få højre table liste til at vise, hvilke filer er blevet konverterede.
# TODO Total files for processing, Files converted (x of x)
# TODO File size after conversion

# TODO UI :
# TODO      Thanks for using - text
# TODO      Knapper skal hide/show dynamisk
# TODO      Pænere UI
# TODO      Window Title

# ? Eventuel gainjustering, for at kompensere for tab af volume? * LAV TEST *


import os
import sys
import shutil
import numpy as np
import wavio
from threading import Thread
from PyQt5 import QtWidgets, uic
from pydub import AudioSegment
from scipy.io import wavfile


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        uic.loadUi("gui.ui", self)

        self.tableWidget.setColumnWidth(0, 280)
        self.tableWidget.setColumnWidth(1, 80)
        self.tableWidget.setColumnWidth(2, 270)
        self.browse.clicked.connect(self.browsefiles)
        self.output.clicked.connect(self.selectOutputFolder)
        self.convert.clicked.connect(self.checkReady_convertfiles)

        self.progressBar.hide()
        self.status.hide()

        # De to "ready"-check variabler
        global checkBrowse
        checkBrowse = 0
        global checkOutput
        checkOutput = 0

        global filenames
        global loopCount

    # "ready"-check inden convertfiles. Kræver både output-folder og browse.
    def checkReady_convertfiles(self):
        if checkBrowse == 1 and checkOutput == 1:

            # Show/hide GUI
            self.progressBar.show()
            self.status.show()
            self.browse.hide()
            self.output.hide()
            self.convert.hide()

            # Run function
            self.convertfiles()
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

        for i in filenamesShort:
            # indsæt forkortet filnavn i listen
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(i))

            # find filstørrelse og indsæt i listen
            size = os.path.getsize(str(filenames[row]))
            size = self.humansize(size)
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(size)))

            row = row + 1

    # Konvertering sker her
    def convertfiles(self):

        global loopCount
        loopCount = 0
        counter = 0
        row = 0
        self.tableWidget.setRowCount(len(filenames))
        self.progressBar.setMaximum(len(filenames) - 1)

        # Filerne læses
        for x in filenames:
            rate, data = wavfile.read(x)
            faudio = AudioSegment.from_file(filenames[loopCount])

            # Hvis filen allerede er mono, kopieres den til output-folder
            if faudio.channels <= 1:
                shutil.copy2(
                    (str(filenames[loopCount])),
                    (str(outputFolder) + "/" + str(filenamesShort[loopCount])),
                )
                self.tableWidget.setItem(
                    row, 2, QtWidgets.QTableWidgetItem("Mono - No Conversion")
                )
                QtWidgets.QApplication.processEvents()

                self.progressBar.setValue(int(loopCount))

                row = row + 1
                loopCount = loopCount + 1
                continue

            # Tjek hvor mange samples der er forskellige mellem de to channels.
            length = len(data[:, 0])
            for i in range(length):
                if data[i, 0] != data[i, 1]:
                    counter = counter + 1

            # Hvis de to channels har mere end X % til fælles, anses filen som mono og skal derfor konverteres.
            # TODO Denne procentsats kan og bør justeres.
            equalSamples = length - counter
            equalSamplesPercent = equalSamples / length * 100
            if equalSamplesPercent > 95:

                # Venstre side af filen skrives til output-folder.
                left = data[:, 0]
                # right = data[:, 1]
                wavio.write(
                    str(outputFolder) + "/" + str(filenamesShort[loopCount]),
                    left,
                    rate,
                    sampwidth=3,
                )

                self.tableWidget.setItem(
                    row, 2, QtWidgets.QTableWidgetItem("Mono - Converted!")
                )

                QtWidgets.QApplication.processEvents()

                self.progressBar.setValue(int(loopCount))

                row = row + 1
                loopCount = loopCount + 1

            else:
                # Hvis filerne har mindre end X % samples til fælles,
                # kopieres den originale stereofil til output-folder, da den anses for at være "true" stereo
                shutil.copy2(
                    (str(filenames[loopCount])),
                    (str(outputFolder) + "/" + str(filenamesShort[loopCount])),
                )

                self.tableWidget.setItem(
                    row, 2, QtWidgets.QTableWidgetItem("Stereo - No Conversion")
                )

                QtWidgets.QApplication.processEvents()

                self.progressBar.setValue(int(loopCount))

                row = row + 1
                loopCount = loopCount + 1

        # Opdater status label
        self.status.setText("Sucess!")

    # Vælg output-folder
    def selectOutputFolder(self):

        # Aktivér "ready"-check for output-folder
        global checkOutput
        checkOutput = 1

        global outputFolder
        outputFolder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        self.output.setText(outputFolder)


# System
app = QtWidgets.QApplication(sys.argv)
mainwindow = Ui()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.show()
sys.exit(app.exec_())
