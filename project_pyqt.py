# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'project.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import face_recognition
import os
from elasticsearch import Elasticsearch


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(520, 600)
        font = QtGui.QFont()
        font.setFamily("HY헤드라인M")
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 245);\n" "")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(210, 510, 75, 23))
        self.pushButton.clicked.connect(self.button_clicked)
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 521, 81))
        font = QtGui.QFont()
        font.setFamily("HY헤드라인M")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setStyleSheet(
            "background-color: rgb(62, 64, 67);\n" "color: rgb(255, 255, 255);"
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(140, 110, 230, 90))
        font = QtGui.QFont()
        font.setFamily("HY헤드라인M")
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("border-color: rgb(0, 0, 0);")
        self.groupBox.setObjectName("groupBox")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 40, 51, 16))
        self.label_3.setObjectName("label_3")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(70, 30, 150, 30))
        self.textEdit.setObjectName("textEdit")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(140, 230, 230, 90))
        font = QtGui.QFont()
        font.setFamily("HY헤드라인M")
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton.setGeometry(QtCore.QRect(80, 40, 61, 16))
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_2.setGeometry(QtCore.QRect(140, 40, 71, 16))
        self.radioButton_2.setObjectName("radioButton_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(20, 40, 56, 12))
        self.label_2.setObjectName("label_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(140, 360, 230, 90))
        font = QtGui.QFont()
        font.setFamily("HY헤드라인M")
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(20, 40, 41, 16))
        self.label_4.setObjectName("label_4")
        self.textEdit_2 = QtWidgets.QTextEdit(self.groupBox_3)
        self.textEdit_2.setGeometry(QtCore.QRect(70, 30, 150, 30))
        self.textEdit_2.setObjectName("textEdit_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 520, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def button_clicked(self):
        es = Elasticsearch("http://localhost:9200")

        def sign_up(name, gender, age):
            save_flag = False
            retry_flag = False
            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                frame = cv2.flip(frame, 1)

                if not ret:
                    break

                font = cv2.FONT_HERSHEY_TRIPLEX
                cv2.putText(
                    frame, "press 't' to take picture", (30, 30), font, 1.0, (123, 26, 55), 1
                )
                if retry_flag == True:
                    cv2.putText(
                        frame,
                        "face not found, retake picture",
                        (30, 75),
                        font,
                        1.0,
                        (123, 26, 55),
                        1,
                    )
                cv2.imshow("Video", frame)

                key = cv2.waitKey(1)

                if key & 0xFF == ord("q"):
                    break
                elif key & 0xFF == ord("t"):
                    cv2.imwrite(f"./{name}.jpg", frame)
                    try:
                        new_member_img = face_recognition.load_image_file(f"./{name}.jpg")
                        new_member_face_encoding = face_recognition.face_encodings(new_member_img)[
                            0
                        ]
                        print(new_member_face_encoding)
                        cap.release()
                        os.remove(f"./{name}.jpg")
                        print(name, gender, age)
                        save_flag = True
                        es.index(
                            index="user_info",
                            doc_type="_doc",
                            body={
                                "name": name,
                                "gender": gender,
                                "age": age,
                                "face_info": new_member_face_encoding,
                            },
                        )
                    except:
                        print("retry...")
                        retry_flag = True
                        os.remove(f"./{name}.jpg")
                if save_flag == True:
                    break

            cv2.destroyAllWindows()

        try:
            print(self.textEdit.toPlainText())
            name = self.textEdit.toPlainText()
            if self.radioButton.isChecked():
                print("male")
                gender = "male"
            elif self.radioButton_2.isChecked():
                print("female")
                gender = "female"
            print(int(self.textEdit_2.toPlainText()))
            age = int(self.textEdit_2.toPlainText())
            print(f"name : {name}, gender: {gender}, age: {age}")
            sign_up(name, gender, age)
        except:
            pass

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Submit"))
        self.label.setText(_translate("MainWindow", "User Sign up"))
        self.groupBox.setTitle(_translate("MainWindow", "< User Name >"))
        self.label_3.setText(_translate("MainWindow", "Name :"))
        self.groupBox_2.setTitle(_translate("MainWindow", "< User gender >"))
        self.radioButton.setText(_translate("MainWindow", "male"))
        self.radioButton_2.setText(_translate("MainWindow", "female"))
        self.label_2.setText(_translate("MainWindow", "Gender :"))
        self.groupBox_3.setTitle(_translate("MainWindow", " < User Age >"))
        self.label_4.setText(_translate("MainWindow", "Age :"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

