'''

import cv2
cap = cv2.VideoCapture(0)          # try 1 or 2 if 0 opens the wrong camera (e.g. a laptop's built-in one)
while True:
    ok, frame = cap.read()
    if not ok: break
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
cap.release(); cv2.destroyAllWindows()

'''

import sys
from PySide6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Viewer")
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())