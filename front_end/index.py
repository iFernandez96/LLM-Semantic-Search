import sys
import subprocess
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

        self.selectFileButton = QPushButton("Select a Schema", self)
        self.selectFileButton.clicked.connect(self.get_file)
        layout.addWidget(self.selectFileButton)

    def button_clicked(self):
        self.submitLabel.setText("TEXT HAS BEEN SUBMITTED")
        userInputedString = self.textbox.text()
        with open("userInput.txt", "w") as file:
            file.write(f"{userInputedString}")
        # Currently runs a Test.sh file (this only works if running on wsl, ubuntu, linux)
        # Change later to work with RunLLM.sh 
        # Make sure in RunLLM takes in user input (will have to remove while loop in RunLLM.sh)
        # Can look at Test.sh to see how to take in user input
        subprocess.run(["../LLMs/Test.sh"], input=userInputedString, text=True)

    def get_file(self):  
        # Include Pandas to convert .xlsx files into .txt files
        # Check if that would be a good use of time or necessary 
        user_selected_file = QFileDialog.getOpenFileName(self, "Select a File", "", "Text Based Files (*.txt *.json *.csv)")

        actualFile = user_selected_file[0]

        if actualFile:
            with open("user_selected_file_contents.txt", "w") as standardFile:
                contents = ""
                with open(f"{user_selected_file[0]}", "r") as selectedFile:
                    contents = selectedFile.read()
                standardFile.write(contents)

        print(f"File contents of {actualFile} have been read and move to user_selected_file_contents.txt")
                
                


my_win = NL2SQ()
my_win.show()
sys.exit(application.exec())