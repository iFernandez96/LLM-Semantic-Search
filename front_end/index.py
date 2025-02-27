import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit)

application = QApplication([])

userInputedString = None

class NL2SQ(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 100, 100)
        self.setWindowTitle("Natural Language to Structured Query")
        layout = QVBoxLayout()


        self.label = QLabel("What are you looking for?", self)
        layout.addWidget(self.label)

        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Enter Text Here: ")
        layout.addWidget(self.textbox)

        self.button = QPushButton("Submit", self)
        self.button.clicked.connect(self.button_clicked)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.submitLabel = QLabel("", self)
        layout.addWidget(self.submitLabel)

    def button_clicked(self):
        self.submitLabel.setText("TEXT HAS BEEN SUBMITTED")
        userInputedString = self.textbox.text()


my_win = NL2SQ()
my_win.show()
sys.exit(application.exec())