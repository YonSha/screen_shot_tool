import math
import os
import random

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QRubberBand
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
import sys
import mss


class YonScreenshotTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot Tool with Compact Buttons")

        # Setup Yon SS tool layout
        self.main_layout = QVBoxLayout()

        # Single horizontal layout for all buttons
        button_layout = QHBoxLayout()

        # Adjust spacing between the buttons
        button_layout.setSpacing(0)  # No extra space between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)  # No margins around the layout

        # Construct each button
        self.construct_buttons(button_layout)

        # Add button layout to the Yon SS tool layout
        self.main_layout.addLayout(button_layout)

        # Initialize QLabel for displaying the screenshot
        self.screenshot_label = QLabel()
        self.main_layout.addWidget(self.screenshot_label)

        # Set the Yon SS tool layout
        self.setLayout(self.main_layout)

        # Variables for interaction
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.screenshot_label)
        self.origin = QPoint()
        self.isDrawing = False
        self.original_image = None
        self.scaled_image = None
        self.crop_rect = None

        # Automatically capture and display screenshot on startup
        self.capture_and_display_full_screen()

    def get_documents_path(self):
        """Get the path to the user's Documents directory."""
        return os.path.join(os.path.expanduser("~"), "Documents")

    def generate_random_filename(self, base_name):
        """Generate a unique filename by appending a random number."""
        random_number = random.randint(1000, 9999)
        return f"{base_name}_{random_number}.png"


    def construct_buttons(self, layout):
        """Add buttons to the layout."""
        # Button to save full screen to file
        self.save_full_button = QPushButton("Save Full Screen")
        self.save_full_button.setFixedWidth(130)
        self.save_full_button.clicked.connect(self.save_full_image)
        layout.addWidget(self.save_full_button)

        # Button to copy full screen to clipboard
        self.copy_full_button = QPushButton("Copy Full Screen")
        self.copy_full_button.setFixedWidth(130)
        self.copy_full_button.clicked.connect(self.copy_full_to_clipboard)
        layout.addWidget(self.copy_full_button)

        # Button to toggle arrow mode
        self.arrow_button = QPushButton("Add Arrows")
        self.arrow_button.setCheckable(True)
        self.arrow_button.setFixedWidth(100)
        layout.addWidget(self.arrow_button)

        # Button to save cropped area
        self.save_crop_button = QPushButton("Save Crop")
        self.save_crop_button.setFixedWidth(90)
        self.save_crop_button.clicked.connect(self.save_cropped_area)
        layout.addWidget(self.save_crop_button)

        # Button to copy cropped area to clipboard
        self.copy_crop_button = QPushButton("Copy Crop")
        self.copy_crop_button.setFixedWidth(90)
        self.copy_crop_button.clicked.connect(self.copy_cropped_to_clipboard)
        layout.addWidget(self.copy_crop_button)

        # Button to close the application
        self.close_button = QPushButton("Close App")
        self.close_button.setFixedWidth(100)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

    def capture_and_display_full_screen(self):
        """Capture the full screen and display it."""
        image = self.capture_full_screenshot()
        if image:
            self.original_image = image
            self.display_image()

    def capture_full_screenshot(self):
        """Capture the full screen using mss and return a QImage."""
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            screenshot = sct.grab(monitor)
            if screenshot:

                image = QImage(
                    screenshot.rgb,
                    screenshot.width,
                    screenshot.height,
                    QImage.Format_RGB888
                )
                return image
            return None

    def display_image(self):
        """Display the current screenshot."""
        self.scaled_image = self.original_image.scaled(
            1650, 700, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.screenshot_label.setPixmap(QPixmap.fromImage(self.scaled_image))
        self.screenshot_label.setFixedSize(self.scaled_image.size())

        # Ready label for interaction
        self.screenshot_label.mousePressEvent = self.on_mouse_press
        self.screenshot_label.mouseMoveEvent = self.on_mouse_move
        self.screenshot_label.mouseReleaseEvent = self.on_mouse_release

    def on_mouse_press(self, event):
        """Start drawing arrow or begin cropping."""
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            if self.arrow_button.isChecked():
                self.isDrawing = True
            else:
                self.rubberBand.setGeometry(QRect(self.origin, QSize()))
                self.rubberBand.show()

    def on_mouse_move(self, event):
        """Continue drawing or adjust cropping area."""
        if self.isDrawing and self.arrow_button.isChecked():
            self.update()
        elif self.rubberBand.isVisible():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def on_mouse_release(self, event):
        """Capture final drawing or cropping."""
        if event.button() == Qt.LeftButton:
            if self.isDrawing and self.arrow_button.isChecked():
                self.isDrawing = False
                self.draw_arrow(self.origin, event.pos())
            elif self.rubberBand.isVisible():
                #self.rubberBand.hide()
                self.crop_rect = self.rubberBand.geometry()

    def draw_arrow(self, start, end):
        """Draw an arrow on the original image."""
        scale_x = self.original_image.width() / self.scaled_image.width()
        scale_y = self.original_image.height() / self.scaled_image.height()

        # Convert points from scaled to original image coordinates
        start_orig = QPoint(int(start.x() * scale_x), int(start.y() * scale_y))
        end_orig = QPoint(int(end.x() * scale_x), int(end.y() * scale_y))

        painter = QPainter(self.original_image)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.red, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(start_orig, end_orig)

        # Calculate the arrowhead's direction based on the line's angle
        arrow_size = 10
        angle = math.atan2(end_orig.y() - start_orig.y(), end_orig.x() - start_orig.x())

        # Calculate coordinates for the arrowhead lines using integers
        p1 = end_orig - QPoint(int(arrow_size * math.cos(angle - math.pi / 6)),
                               int(arrow_size * math.sin(angle - math.pi / 6)))
        p2 = end_orig - QPoint(int(arrow_size * math.cos(angle + math.pi / 6)),
                               int(arrow_size * math.sin(angle + math.pi / 6)))

        painter.drawLine(end_orig, p1)
        painter.drawLine(end_orig, p2)
        painter.end()

        self.display_image()

    def save_full_image(self):
        # Uncheck arrow btn
        self.arrow_button.setChecked(False)

        """Save the full screenshot to a file in the Documents directory."""
        filename = self.generate_random_filename("full_screenshot")
        filepath = os.path.join(self.get_documents_path(), filename)

    def copy_full_to_clipboard(self):
        # Uncheck arrow btn
        self.arrow_button.setChecked(False)

        """Copy the full screenshot to the clipboard."""
        if self.original_image:
            clip = QApplication.clipboard()
            clip.setPixmap(QPixmap.fromImage(self.original_image))

    def save_cropped_area(self):
        # Uncheck arrow btn
        self.arrow_button.setChecked(False)

        """Save the cropped selection to a file in the Documents directory."""
        if self.crop_rect and self.crop_rect.isValid():
            self.rubberBand.hide()
            filename = self.generate_random_filename("cropped_screenshot")
            filepath = os.path.join(self.get_documents_path(), filename)
            scaled_rect = self._scale_rect(self.crop_rect)
            cropped = self.original_image.copy(scaled_rect)


    def copy_cropped_to_clipboard(self):
        # Uncheck arrow btn
        self.arrow_button.setChecked(False)

        """Copy the cropped selection to the clipboard."""
        if self.crop_rect and self.crop_rect.isValid():
            self.rubberBand.hide()
            scaled_rect = self._scale_rect(self.crop_rect)
            cropped = self.original_image.copy(scaled_rect)
            clip = QApplication.clipboard()
            clip.setPixmap(QPixmap.fromImage(cropped))


    def _scale_rect(self, rect: QRect):
        """Convert visualized crop area to actual image coordinates."""
        scale_x = self.original_image.width() / self.scaled_image.width()
        scale_y = self.original_image.height() / self.scaled_image.height()
        return QRect(
            int(rect.x() * scale_x),
            int(rect.y() * scale_y),
            int(rect.width() * scale_x),
            int(rect.height() * scale_y)
        )

    def keyPressEvent(self, event):
        """Handle key press events for actions like 'Esc'."""
        if event.key() == Qt.Key_Escape:
            if self.rubberBand.isVisible():
                self.rubberBand.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YonScreenshotTool()
    window.show()
    sys.exit(app.exec_())
