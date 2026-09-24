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
from PySide6.QtCore import QEvent, Qt, QTimer, QPoint
from PySide6.QtGui import QImage, QPixmap
import os
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #VARIABLES
        self.roi = None
        self.cap = None
        self.drag_start = None
        self.frame = None
        #WINDOW TITLE AND SIZE
        self.setWindowTitle("Camera Viewer")
        self.resize(800, 600)

        #LABEL TO DISPLAY CAMERA FEED
        self.label = QLabel("Camera Stopped")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #111")
        

        #BUTTONS FOR CAMERA CONTROL
        self.btn_start = QPushButton("Start Camera")
        self.btn_stop = QPushButton("Stop Camera")
        self.btn_snap = QPushButton("Snap Photo")

        #LAYOUTS
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_snap)
        
        #VIDEO DISPLAY LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(button_layout)

        #CONTAINER WIDGET AND SET THE LAYOUT
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        #CONNECT BUTTONS TO FUNCTIONS
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_snap.clicked.connect(self.snap_photo)
        self.btn_stop.setEnabled(False)     #cant stop before starting


        #TIMER FOR UPDATING FRAMES
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.statusBar().showMessage("Ready", 5000)  # Show message for 5 seconds

        self.label.installEventFilter(self)  # Install event filter for mouse events


    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)  # Update every 30 ms
        # self.label.setText("Camera Started")
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # GREEN RECTANGLE 
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

    def label_to_frame(self, point):
        fh, fw = self.frame.shape[:2]                  # frame height, width
        lw, lh = self.label.width(), self.label.height()
        scale = min(lw / fw, lh / fh)                  # same scale show_frame used
        off_x = (lw - fw * scale) / 2                  # empty bar on left
        off_y = (lh - fh * scale) / 2                  # empty bar on top
        x = int((point.x() - off_x) / scale)
        y = int((point.y() - off_y) / scale)
        x = max(0, min(x, fw - 1))                     # keep inside the frame
        y = max(0, min(y, fh - 1))
        return x, y

    def eventFilter(self, obj, event):
        if obj is self.label and self.frame is not None:
            if event.type() == QEvent.MouseButtonPress:
                self.drag_start = self.label_to_frame(event.position().toPoint())
            elif event.type() == QEvent.MouseMove and self.drag_start:
                x0, y0 = self.drag_start
                x1, y1 = self.label_to_frame(event.position().toPoint())
                self.roi = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            elif event.type() == QEvent.MouseButtonRelease and self.drag_start:
                self.drag_start = None
                self.statusBar().showMessage(f"Box set: {self.roi}", 5000)
        return super().eventFilter(obj, event)
        

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