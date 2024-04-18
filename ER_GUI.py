import sys

import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton

import dbAdmin
from emotion_Recognition import analyse_emotion


class EmotionRecognitionWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QtCore.QTimer(self)  # Timer for grabbing images from the webcam
        self.cap = None  # This will hold the webcam stream

    def init_ui(self):
        self.setWindowTitle('Emotion Recognition System')
        self.setGeometry(100, 100, 800, 600)  # Set the window size

        # Create a central widget and set a layout
        self.central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(self.central_widget)  # Set the central widget
        layout = QVBoxLayout()  # Create a vertical layout
        self.central_widget.setLayout(layout)  # Set the layout to the central widget

        # Add a label to show emotions
        self.emotion_label = QLabel("Emotion will be displayed here")
        layout.addWidget(self.emotion_label)

        self.btn_open = QPushButton('Open Image', self)
        self.btn_open.clicked.connect(self.open_image)
        layout.addWidget(self.btn_open)

        self.start_btn = QPushButton("Start Webcam", self)
        self.start_btn.clicked.connect(self.start_webcam)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Webcam", self)
        self.stop_btn.clicked.connect(self.stop_webcam)
        layout.addWidget(self.stop_btn)

    def start_webcam(self):
            try:
                self.cap = cv2.VideoCapture(0)  # Attempt to start webcam
                if not self.cap.isOpened():
                    raise ValueError("Could not open webcam")
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(20)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Webcam Error", str(e))
                print(f"Error starting webcam: {e}")

    def update_frame(self):
            ret, frame = self.cap.read()
            if ret:
                # Convert to RGB for display
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_image(rgb_image)
            else:
                print("Failed to capture frame from webcam")

    def display_image(self, image):
            try:
                qformat = QImage.Format_RGB888
                out_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], qformat)
                out_image = out_image.rgbSwapped()
                self.emotion_label.setPixmap(QPixmap.fromImage(out_image))
            except Exception as e:
                print(f"Error displaying image: {e}")

    def stop_webcam(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def closeEvent(self, event):
        self.stop_webcam()
        super().closeEvent(event)

    def open_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home', "Image files (*.jpg *.jpeg *.png)")
        if fname:
            self.on_image_received(fname)

    def on_image_received(self, image_path):
        emotion = analyse_emotion(image_path)
        self.display_emotion(emotion)

    def display_emotion(self, emotion):
        if emotion:
            self.emotion_label.setText(f"Detected Emotion: {emotion}")
        else:
            self.emotion_label.setText("Failed to detect emotion.")

    # The function analyze_emotion needs to be defined

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog  # Store the reference to the Dialog
        self.emotion_recognition_window = EmotionRecognitionWindow()  # Emotion recognition GUI instance

        Dialog.setObjectName("Emotion Recognition Login")
        Dialog.resize(427, 321)

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(140, 190, 131, 31))
        self.pushButton.setObjectName("pushButton")

        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(140, 240, 131, 31))
        self.pushButton_2.setObjectName("pushButton_2")

        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(130, 80, 151, 21))
        self.lineEdit.setObjectName("lineEdit")

        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 130, 151, 21))
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.retranslateUi(Dialog)
        self.pushButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.register)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Emotion Recognition Login"))
        self.pushButton.setText(_translate("Dialog", "Login"))
        self.pushButton_2.setText(_translate("Dialog", "Register"))
        self.lineEdit.setPlaceholderText(_translate("Dialog", "Username"))
        self.lineEdit_2.setPlaceholderText(_translate("Dialog", "Password"))

    def login(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        if dbAdmin.authenticate_user(username, password):
            self.emotion_recognition_window.show()
            self.Dialog.hide()  # Use the stored Dialog reference
        else:
            QtWidgets.QMessageBox.warning(self.Dialog, "Login Failed", "Invalid username or password.")

    def register(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        try:
            dbAdmin.add_user(username, password)
            QtWidgets.QMessageBox.information(self.Dialog, "Registration Successful",
                                              "You can now login with your credentials.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.Dialog, "Registration Failed", str(e))


def main():
    dbAdmin.init_db()
    app = QtWidgets.QApplication(sys.argv)
    LoginDialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(LoginDialog)
    LoginDialog.show()
    sys.exit(app.exec_())
