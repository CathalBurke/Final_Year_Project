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
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QSlider, QGroupBox, QSizePolicy, QStackedWidget, QButtonGroup, QListWidget, QProgressBar
from PySide6.QtCore import QEvent, Qt, QTimer, QPoint
from PySide6.QtGui import QImage, QPixmap
import os
import time
import numpy as np
from gui_design.theme import load_style, PALETTE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #VARIABLES
        self.roi = None
        self.cap = None
        self.drag_start = None
        self.frame = None
        self.prev_roi = None
        self.model = None   #tought part
        self.parts = []
        self.results = []
        self.last_check = 0
        self.model_area = None   # area of the taught part
        self.count_ok = 0
        self.count_ng = 0
        self.box_was_empty = True  # Track if the box was empty in the previous frame
        
        #WINDOW TITLE AND SIZE
        self.setWindowTitle("Vision Inspection")
        self.resize(1440, 900)

        #LABEL TO DISPLAY CAMERA FEED
        self.label = QLabel("Camera Stopped")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("feed")
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # Allow resizing
        self.label.setMinimumSize(320,180)
        

        #BUTTONS FOR CAMERA CONTROL
        self.btn_start = QPushButton("Start Camera")
        self.btn_stop = QPushButton("Stop Camera")
        self.btn_snap = QPushButton("Snap Photo")
        self.btn_save = QPushButton("Save Part")
        self.btn_load = QPushButton("Load Part")
        self.btn_settings = QPushButton("Settings")
        self.chk_thresh = QCheckBox("Show threshold")
        self.btn_teach = QPushButton("Teach")
        self.btn_teach.setObjectName("primary")    
        self.slider = QSlider(Qt.Horizontal)               
        self.slider.setRange(0, 255)                       
        self.slider.setValue(127)
        self.accept_slider = QSlider(Qt.Horizontal)
        self.accept_slider.setRange(0, 100)
        self.accept_slider.setValue(80)
        self.lbl_accept = QLabel("Accept: 80%")
        
        #SETUP STEP PAGES - ONE GROUP PER STEP, SHOWN ON THE RIGHT
        cam_box = QGroupBox("1 · Camera")
        cam_layout = QVBoxLayout(cam_box)
        cam_layout.addWidget(self.btn_start)
        cam_layout.addWidget(self.btn_stop)
        cam_layout.addWidget(self.btn_snap)
        cam_layout.addWidget(self.btn_settings)
        cam_layout.addStretch()

        area_box = QGroupBox("2 · Inspection area")
        area_layout = QVBoxLayout(area_box)
        area_help = QLabel("Drag a box on the live image around the area you want to inspect.")
        area_help.setWordWrap(True)
        area_layout.addWidget(area_help)
        area_layout.addStretch()

        image_box = QGroupBox("3 · Image")
        image_layout = QVBoxLayout(image_box)
        image_layout.addWidget(self.chk_thresh)
        image_layout.addWidget(self.slider)
        image_layout.addStretch()

        teach_box = QGroupBox("4 · Teach")
        teach_layout = QVBoxLayout(teach_box)
        teach_layout.addWidget(self.btn_teach)
        teach_layout.addWidget(self.btn_save)
        teach_layout.addWidget(self.btn_load)
        teach_layout.addStretch()

        tol_box = QGroupBox("5 · Tolerances")
        tol_layout = QVBoxLayout(tol_box)
        tol_layout.addWidget(self.lbl_accept)
        tol_layout.addWidget(self.accept_slider)
        tol_layout.addStretch()

        cal_box = QGroupBox("6 · Calibrate")
        cal_layout = QVBoxLayout(cal_box)
        cal_help = QLabel("Grid calibration will be added once the conveyor is assembled.")
        cal_help.setWordWrap(True)
        cal_layout.addWidget(cal_help)
        cal_layout.addStretch()

        self.step_stack = QStackedWidget()
        for box in (cam_box, area_box, image_box, teach_box, tol_box, cal_box):
            self.step_stack.addWidget(box)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.step_stack)

        #SETUP STEP LIST - LEFT
        self.step_list = QListWidget()
        for name in ["1 · Camera", "2 · Inspection area", "3 · Image", "4 · Teach", "5 · Tolerances", "6 · Calibrate"]:
            self.step_list.addItem(name)
        cal_item = self.step_list.item(5)
        cal_item.setFlags(cal_item.flags() & ~Qt.ItemIsEnabled)   # greyed out until grid calibration exists
        self.step_list.setCurrentRow(0)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Setup steps"))
        left_layout.addWidget(self.step_list)

        #RUN MODE PANELS
        result_box = QGroupBox("Result")
        result_layout = QVBoxLayout(result_box)
        self.lbl_result = QLabel("--")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setStyleSheet("font-size: 40px; font-weight: 800;")
        self.lbl_reason = QLabel("Waiting for a part")
        self.lbl_reason.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.lbl_result)
        result_layout.addWidget(self.lbl_reason)

        counts_box = QGroupBox("Counts")
        counts_layout = QVBoxLayout(counts_box)
        self.lbl_counts = QLabel()
        self.btn_reset = QPushButton("Reset counts")
        counts_layout.addWidget(self.lbl_counts)
        counts_layout.addWidget(self.btn_reset)

        

        run_left = QWidget()
        run_left_layout = QVBoxLayout(run_left)
        run_left_layout.addWidget(result_box)
        run_left_layout.addWidget(counts_box)
        run_left_layout.addStretch()

        checks_box = QGroupBox("Checks")
        checks_layout = QVBoxLayout(checks_box)
        self.lbl_shape = QLabel("Shape match: --")
        self.bar_shape = QProgressBar()
        self.bar_shape.setRange(0, 100)
        self.bar_shape.setTextVisible(False)
        self.lbl_shape_limit = QLabel("Accept at 80% or more")

        self.lbl_size = QLabel("Size vs model: --")
        self.bar_size = QProgressBar()
        self.bar_size.setRange(0, 30)
        self.bar_size.setTextVisible(False)
        self.lbl_size_limit = QLabel("Allowed within ±10% of taught area")

        for w in (self.lbl_shape, self.bar_shape, self.lbl_shape_limit,
                  self.lbl_size, self.bar_size, self.lbl_size_limit):
            checks_layout.addWidget(w)

        run_right = QWidget()
        run_right_layout = QVBoxLayout(run_right)
        run_right_layout.addWidget(checks_box)
        run_right_layout.addStretch()

        #STACKS - PAGE 0 = SETUP, PAGE 1 = RUN
        self.left_stack = QStackedWidget()
        self.left_stack.setObjectName("sidePanel")
        self.left_stack.setFixedWidth(236)
        self.left_stack.addWidget(left_panel)
        self.left_stack.addWidget(run_left)

        self.right_stack = QStackedWidget()
        self.right_stack.setObjectName("sidePanel")
        self.right_stack.setFixedWidth(330)
        self.right_stack.addWidget(right_panel)
        self.right_stack.addWidget(run_right)

        #MODE BAR - SETUP / RUN
        self.btn_setup = QPushButton("Setup")
        self.btn_run = QPushButton("Run")
        self.btn_setup.setCheckable(True)
        self.btn_run.setCheckable(True)
        self.btn_setup.setChecked(True)
        mode_group = QButtonGroup(self)
        mode_group.addButton(self.btn_setup)
        mode_group.addButton(self.btn_run)

        mode_bar = QHBoxLayout()
        mode_bar.addWidget(self.btn_setup)
        mode_bar.addWidget(self.btn_run)
        mode_bar.addStretch()

        #MAIN LAYOUT - LEFT, FEED, RIGHT
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_stack)
        main_layout.addWidget(self.label, stretch=1)
        main_layout.addWidget(self.right_stack)

        #OUTER LAYOUT - MODE BAR ON TOP, MAIN BELOW
        outer_layout = QVBoxLayout()
        outer_layout.addLayout(mode_bar)
        outer_layout.addLayout(main_layout)

        #CONTAINER WIDGET AND SET THE LAYOUT
        container = QWidget()
        container.setLayout(outer_layout)
        self.setCentralWidget(container)
        

        #CONNECT BUTTONS TO FUNCTIONS
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_snap.clicked.connect(self.snap_photo)
        self.btn_save.clicked.connect(self.save_part)
        self.btn_load.clicked.connect(self.load_part)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_reset.clicked.connect(self.reset_counts)
        self.update_counts()   # show zeros at start
        self.btn_setup.clicked.connect(lambda: self.set_mode(0))
        self.btn_run.clicked.connect(lambda: self.set_mode(1))
        self.step_list.currentRowChanged.connect(self.step_stack.setCurrentIndex)
        self.btn_teach.clicked.connect(self.teach_model)
        self.btn_stop.setEnabled(False)     #cant stop before starting

        self.accept_slider.valueChanged.connect(lambda v: self.lbl_accept.setText(f"Accept: {v}%"))                    


        #TIMER FOR UPDATING FRAMES
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.statusBar().showMessage("Ready", 5000)  # Show message for 5 seconds

        self.label.installEventFilter(self)  # Install event filter for mouse events

    def open_settings(self):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_SETTINGS, 1)

    def set_mode(self, page):
        self.left_stack.setCurrentIndex(page)
        self.right_stack.setCurrentIndex(page)
        mode = "Setup" if page == 0 else "Run"
        self.statusBar().showMessage(f"{mode} mode", 3000)

    def judge(self):
        if not self.results:
            self.box_was_empty = True          # box is empty, ready for the next part
            return
        limit = self.accept_slider.value()
        fails = [r for r in self.results if r[6] < limit or not r[7]]
        ok = len(fails) == 0
        if ok:
            self.lbl_result.setText("OK")
            self.lbl_result.setStyleSheet(f"font-size: 40px; font-weight: 800; color: {PALETTE['pass']};")
            self.lbl_reason.setText(f"{len(self.results)} part(s) pass")
        else:
            reason = "out of size" if not fails[0][7] else "below shape limit"
            self.lbl_result.setText("NG")
            self.lbl_result.setStyleSheet(f"font-size: 40px; font-weight: 800; color: {PALETTE['fail']};")
            self.lbl_reason.setText(f"{len(fails)} part(s) {reason}")

        worst = fails[0] if fails else min(self.results, key=lambda r: r[6])
        score = worst[6]
        dev = 100 * (cv2.contourArea(worst[0]) - self.model_area) / self.model_area
        shape_ok = score >= limit
        size_ok = worst[7]
        self.lbl_shape.setText(f"Shape match: {score:.0f}%   {'PASS' if shape_ok else 'FAIL'}")
        self.bar_shape.setValue(int(score))
        self.lbl_shape_limit.setText(f"Accept at {limit}% or more")
        self.lbl_size.setText(f"Size vs model: {dev:+.1f}%   {'PASS' if size_ok else 'FAIL'}")
        self.bar_size.setValue(min(30, int(abs(dev))))
        self.set_bar_colour(self.bar_shape, shape_ok)
        self.set_bar_colour(self.bar_size, size_ok)
        
        if self.box_was_empty:                 # a new part has arrived, count it once
            if ok:
                self.count_ok += 1
            else:
                self.count_ng += 1
            self.box_was_empty = False
            self.update_counts()

    def update_counts(self):
        total = self.count_ok + self.count_ng
        yield_pct = 100 * self.count_ok / total if total else 0
        self.lbl_counts.setText(f"Inspected: {total}\nOK: {self.count_ok}\nNG: {self.count_ng}\nYield: {yield_pct:.1f}%")

    def reset_counts(self):
        self.count_ok = 0
        self.count_ng = 0
        self.update_counts() 

    def set_bar_colour(self, bar, ok):
        colour = PALETTE["muted_fill"] if ok else PALETTE["fail"]
        bar.setStyleSheet(f"QProgressBar::chunk {{ background: {colour}; }}")

    def start_camera(self):
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        if not self.cap.isOpened():  # Check if the camera opened successfully
            self.statusBar().showMessage("Failed to open camera", 5000)
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        

        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # GREEN RECTANGLE
        self.roi = (w//4, h//4, 3*w//4, 3*h//4)  # Centered GREEN ROI

        self.timer.start(30)  # Update every 30 ms
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage(f"Camera Started at {w}x{h}", 5000)

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

            roi = frame[y1:y2, x1:x2]     
            if roi.size > 0:                                          
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)                             
                gray = cv2.GaussianBlur(gray, (5, 5), 0)                                 
                _, mask = cv2.threshold(gray, self.slider.value(), 255, cv2.THRESH_BINARY) 

                if self.chk_thresh.isChecked():                                               
                    display[y1:y2, x1:x2] = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)           

                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                rh, rw = mask.shape                              # height and width of the box
                parts = []
                for c in contours:
                    if cv2.contourArea(c) < 500:
                        continue                                 # too small, dust or noise
                    x, y, w, h = cv2.boundingRect(c)
                    if x <= 1 or y <= 1 or x + w >= rw - 1 or y + h >= rh - 1:
                        continue                                 # touches the box edge, finger or cable
                    parts.append(c)

                self.parts = parts  # Store parts for later use in teach_model
                #cv2.drawContours(display, parts, -1, (0, 255, 0), 2, offset=(x1, y1))  

                

                now = time.time()
                if now - self.last_check >= 0.2:              # inspect 5 times a second
                    self.last_check = now
                    self.results = []
                    for c in parts:
                        x, y, w, h = cv2.boundingRect(c)
                        rect = cv2.minAreaRect(c)
                        score = None
                        size_ok = True
                        if self.model is not None:
                            d = cv2.matchShapes(self.model, c, cv2.CONTOURS_MATCH_I1, 0.0)
                            score = max(0, 100 * (1 - d))
                            area = cv2.contourArea(c)
                            size_ok = abs(area - self.model_area) / self.model_area < 0.1
                        self.results.append((c, x, y, w, h, rect, score, size_ok))

                    if self.model is not None and self.left_stack.currentIndex() == 1:
                        self.judge()

                fs = frame.shape[1] / 800
                th = max(2, int(fs * 2))
                for c, x, y, w, h, rect, score, size_ok in self.results:     # draw last results every frame
                    colour = (0, 255, 0)                                       # green = pass
                    if score is not None and score < self.accept_slider.value() or not size_ok:
                        colour = (0, 0, 255)                                   # red = fail
                    cv2.drawContours(display, [c + [x1, y1]], -1, colour, th)
                    if score is not None:
                        box = cv2.boxPoints(rect).astype("int32") + [x1, y1]   # 4 corners of rotated box
                        cv2.drawContours(display, [box], -1, colour, th)
                        label = f"{score:.0f}%" if size_ok else f"{score:.0f}% SIZE DOESNT MATCH"
                        cv2.putText(display, label, (x1 + x, y1 + y - int(10 * fs)),
                                    cv2.FONT_HERSHEY_SIMPLEX, fs, colour, th)
                  

            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            self.show_frame(display)



    def teach_model(self):
        if not self.parts:
            self.statusBar().showMessage("No parts detected to teach", 5000)
            return
        self.model = max(self.parts, key=cv2.contourArea)
        self.model_area = cv2.contourArea(self.model)
        area = int (cv2.contourArea(self.model))
        self.statusBar().showMessage(f"Part Trained with area: {area}", 5000)

    def save_part(self):
        if self.model is None:
            self.statusBar().showMessage("Teach a part before saving", 3000)
            return
        os.makedirs("Models", exist_ok=True)
        np.save("Models/taught_part.npy", self.model)
        self.statusBar().showMessage("Part saved to Models/taught_part.npy", 5000)


    def load_part(self):
        path = "Models/taught_part.npy"
        if not os.path.exists(path):
            self.statusBar().showMessage("No saved part found", 3000)
            return
        self.model = np.load(path)
        self.model_area = cv2.contourArea(self.model)
        self.statusBar().showMessage(f"Part loaded with area: {int(self.model_area)}", 5000)


    def show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
                self.prev_roi = self.roi                      # remember current box
                self.drag_start = self.label_to_frame(event.position().toPoint())
            elif event.type() == QEvent.MouseMove and self.drag_start:
                x0, y0 = self.drag_start
                x1, y1 = self.label_to_frame(event.position().toPoint())
                self.roi = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            elif event.type() == QEvent.MouseButtonRelease and self.drag_start:
                self.drag_start = None
                x1, y1, x2, y2 = self.roi                     # check the size
                if x2 - x1 < 10 or y2 - y1 < 10:
                    self.roi = self.prev_roi                  # too small, put old box back
                    self.statusBar().showMessage("Box too small, kept previous box", 3000)
                else:
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
    app.setStyle("Fusion")
    app.setStyleSheet(load_style())
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())