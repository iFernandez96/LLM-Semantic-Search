import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog)

application = QApplication([])

userInputedString = None

class NL2SQ(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 250, 250, 100)
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

        self.selectFileButton = QPushButton("Select a File", self)
        self.selectFileButton.clicked.connect(self.get_file)
        layout.addWidget(self.selectFileButton)

    def button_clicked(self):
        self.submitLabel.setText("TEXT HAS BEEN SUBMITTED")
        userInputedString = self.textbox.text()
        with open("userInput.txt", "w") as file:
            file.write(f"{userInputedString}")

    def get_file(self):  
        user_selected_file = QFileDialog.getOpenFileName(self, "Select a File", "", "Text Based Files (*.txt *.json);; Excel Files (*.xlsx *xls)")

        actualFile = user_selected_file[0]

        if actualFile:
            # self.selectFileButton.setText(user_selected_file[0])
            with open("user_selected_file_contents.txt", "w") as standardFile:
                contents = ""
                with open(f"{user_selected_file[0]}", "r") as selectedFile:
                    contents = selectedFile.read()
                standardFile.write(contents)
        print(f"File contents of {actualFile} have been read and move to user_selected_file_contents.txt")
                
                


my_win = NL2SQ()
my_win.show()
sys.exit(application.exec())