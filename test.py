'''

import cv2
cap = cv2.VideoCapture(0)          
while True:
    ok, frame = cap.read()
    if not ok: break
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
cap.release(); cv2.destroyAllWindows()

'''
import cv2
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
import os
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Viewer")
        self.resize(800, 600)
        self.label = QLabel("Camera Stopped")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #111")


        self.btn_start = QPushButton("Start Camera")
        self.btn_stop = QPushButton("Stop Camera")
        self.btn_snap = QPushButton("Snap Photo")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_snap)
        

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_snap.clicked.connect(self.snap_photo)
        self.btn_stop.setEnabled(False)     #cant stop before starting

        self.frame = None
        self.roi = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.statusBar().showMessage("Ready", 5000)  # Show message for 5 seconds


    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)  # Update every 30 ms
        # self.label.setText("Camera Started")
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.roi = (w//4, h//4, 3*w//4, 3*h//4)  # Centered  GREEN ROI
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage("Camera Started", 5000)  # Show message for 5 seconds

    def stop_camera(self):
        self.timer.stop()
        self.cap.release()
        self.label.clear()
        self.btn_stop.setEnabled(False)
        self.label.setText("Camera Stopped")
        self.btn_start.setEnabled(True)
        self.statusBar().showMessage("Camera Stopped", 5000)  # Show message for 5 seconds

    def update_frame(self):
        ok, frame = self.cap.read()
        if ok:
            self.frame = frame
            display = frame.copy()
            x1, y1, x2, y2 = self.roi
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            self.show_frame(display)

    def show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(self.label.size(), Qt.KeepAspectRatio)
        self.label.setPixmap(pix)

    def snap_photo(self):
        ##self.label.setText("Photo Snapped")
      if self.frame is None:
              return
      os.makedirs("Captures", exist_ok=True)
      filename = time.strftime("Captures/img_%d%m%Y_%H%M%S.jpg")
      cv2.imwrite(filename, self.frame)
      print("Photo saved as:", filename)   
      self.statusBar().showMessage("Photo saved as: " + filename, 5000)  # Show message for 5 seconds

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())