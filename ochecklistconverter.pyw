from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QLabel,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
)
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import csv


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.inputFileName = ""
        self.outputFileName = ""

        self.wLayout = QVBoxLayout(self)

        title = QLabel("OCheckListConverter v1.0")
        titleFont = title.font()
        titleFont.setPointSize(24)
        titleFont.setBold(True)
        title.setFont(titleFont)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wLayout.addWidget(title)

        author = QLabel("by JacobCZ")
        author.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.wLayout.addWidget(author)

        aboutLayout = QHBoxLayout()

        aboutQtBtn = QPushButton("O Qt Frameworku")
        aboutQtBtn.clicked.connect(lambda: QMessageBox.aboutQt(self, "O Qt Frameworku"))
        aboutLayout.addWidget(aboutQtBtn)

        aboutQtBtn = QPushButton("O programu")
        aboutQtBtn.clicked.connect(
            lambda: QMessageBox.about(
                self,
                "O programu",
                """OCheckListConverter je program, který převede soubor vyexportovaný aplikací "O CheckList" na CSV soubor formátovaný jako soubor záložní paměti kontroly SportIdent. Ten lze poté naimportovat do softwaru pro organizaci závodů.

Verze: 1.0

Autorem je JacobCZ
Licencováno pod Apache 2.0 licencí.""",
            )
        )
        aboutLayout.addWidget(aboutQtBtn)

        self.wLayout.addLayout(aboutLayout)

        self.wLayout.addWidget(QHLine())

        inputFileBtn = QPushButton("Vybrat soubor z O Checklist")
        inputFileBtn.clicked.connect(self.selectInputFile)
        self.wLayout.addWidget(inputFileBtn)

        self.inpLabel = QLabel(f"Soubor nevybrán")
        self.inpLabel.setStyleSheet("QLabel { color: red; }")
        self.wLayout.addWidget(self.inpLabel)

        self.wLayout.addWidget(QHLine())

        outputFileBtn = QPushButton("Vybrat výstupní soubor")
        outputFileBtn.clicked.connect(self.selectOutputFile)
        self.wLayout.addWidget(outputFileBtn)

        self.outLabel = QLabel(f"Soubor nevybrán")
        self.outLabel.setStyleSheet("QLabel { color: red; }")
        self.wLayout.addWidget(self.outLabel)

        self.wLayout.addWidget(QHLine())

        self.wLayout.addWidget(QLabel("Start 00"))

        self.start0Edit = QTimeEdit()
        self.start0Edit.setDisplayFormat("HH:mm:ss")
        self.start0Edit.setTime(QTime(10, 00))
        self.wLayout.addWidget(self.start0Edit)

        self.wLayout.addWidget(QHLine())

        self.convertBtn = QPushButton("Převést")
        self.convertBtn.setEnabled(False)
        self.convertBtn.clicked.connect(self.convert)
        self.wLayout.addWidget(self.convertBtn)

        self.setVisible(True)

    def selectInputFile(self):
        self.inputFileName, _ = QFileDialog.getOpenFileName(
            self,
            "Vyberte soubor z O Checklist",
            filter="O Checklist (start-status.yaml)",
        )
        self.inpLabel.setText(f"Soubor vybrán: {self.inputFileName}")
        self.inpLabel.setStyleSheet("QLabel { color: green; }")
        self.convertBtn.setEnabled(
            self.inputFileName != "" and self.outputFileName != ""
        )

    def selectOutputFile(self):
        self.outputFileName, _ = QFileDialog.getSaveFileName(
            self,
            "Vyberte soubor z O Checklist",
            filter="SportIdent backup CSV (*.csv)",
        )
        self.outLabel.setText(f"Soubor vybrán: {self.outputFileName}")
        self.outLabel.setStyleSheet("QLabel { color: green; }")
        self.convertBtn.setEnabled(
            self.inputFileName != "" and self.outputFileName != ""
        )

    def convert(self):
        with open(self.inputFileName, "r", encoding="utf8") as yamlFile:
            with open(
                self.outputFileName, "w+", encoding="utf8", newline=""
            ) as csvFile:
                siPunch = csv.writer(csvFile, delimiter=";")
                yamlDoc = load(yamlFile, Loader=Loader)
                i = 0
                for runner in yamlDoc["Data"]:
                    match runner["Runner"]["StartStatus"].upper():
                        case "LATE START":
                            if runner["Runner"]["Card"] != None:
                                i += 1
                                siPunch.writerow(
                                    [
                                        i,
                                        runner["Runner"]["Card"],
                                        runner["ChangeLog"]["LateStart"].strftime(
                                            "%H:%M:%S"
                                        ),
                                    ]
                                )
                        case "STARTED OK":
                            if runner["Runner"]["Card"] != None:
                                i += 1
                                if runner["Runner"]["StartTime"] == None:
                                    runner["Runner"][
                                        "StartTime"
                                    ] = self.start0Edit.time().toPython()
                                siPunch.writerow(
                                    [
                                        i,
                                        runner["Runner"]["Card"],
                                        runner["Runner"]["StartTime"].strftime(
                                            "%H:%M:%S"
                                        ),
                                    ]
                                )

                        case _:
                            ...
        QMessageBox.information(self, "OCheckListConverter", "Převedeno úspěšně")


app = QApplication()
app.setApplicationName("OCheckListConverter")
app.setOrganizationName("JacobCZ")

w = Window()

app.exec()
