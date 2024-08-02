import sys

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPen, QColor, QBrush, QFont, QClipboard
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QRadioButton,
    QLabel, QPlainTextEdit, QFrame, QPushButton, QFileDialog
)

colors = ["Black", "Brown", "Red", "Orange", "Yellow", "Green", "Blue", "Violet", "Grey", "White"]
colors_without_black = ["Brown", "Red", "Orange", "Yellow", "Green", "Blue", "Violet", "Grey", "White"]
multipliers = {"Black": 1, "Brown": 10, "Red": 100, "Orange": 1000, "Yellow": 10000, "Green": 10 ** 5, "Blue": 10 ** 6,
               "Violet": 10 ** 7, "Grey": 10 ** 8, "White": 10 ** 9, "Gold": 0.1, "Silver": 0.01}
tolerances = {"Brown": 1, "Red": 2, "Orange": 3, "Yellow": 4, "Green": 0.5, "Blue": 0.25, "Violet": 0.1, "Gray": 0.05,
              "Gold": 5, "Silver": 10}
tempco = {"Brown": 100, "Red": 50, "Orange": 15, "Yellow": 25, "Blue": 10, "Violet": 5}


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.band = None

        #  Window Properties
        self.setWindowTitle("Resistor Calculator")
        self.setWindowIcon(QIcon(r"icon.png"))
        self.setGeometry(350, 180, 800, 500)
        self.setFixedSize(800, 500)
        with open("styles.qss", "r") as styles:
            self.setStyleSheet(styles.read())
        self.resistor_pixmap = QLabel(self)
        self.resistor_pixmap.setGeometry(300, 15, 450, 335)
        self.canvas = QPixmap(450, 350)
        self.canvas.fill(QColor("white"))

        self.painter = QPainter(self.canvas)

        self.pen = QPen()
        self.pen.setWidth(4)
        self.pen.setColor(QColor("#555d6a"))

        self.brush = QBrush()
        self.brush.setColor(QColor("#555d6a"))
        self.brush.setStyle(Qt.BrushStyle.SolidPattern)

        # Resistor terminals
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

        self.painter.drawRect(20, 160, 80, 5)
        self.painter.drawRect(350, 160, 80, 5)

        # Resistor body
        self.pen.setColor(QColor("#47e2d9"))
        self.brush.setColor(QColor("#47e2d9"))
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

        self.painter.drawRect(135, 133, 170, 65)
        self.painter.drawEllipse(90, 130, 75, 70)
        self.painter.drawEllipse(280, 130, 75, 70)
        self.resistor_pixmap.setPixmap(self.canvas)

        QLabel("Select your conversion :", self).setGeometry(30, 20, 130, 20)

        # Radio buttons
        self.ColorToOhmRadioButton = QRadioButton("Color code to Ohm Value", self)
        self.ColorToOhmRadioButton.setGeometry(30, 50, 160, 20)
        self.ColorToOhmRadioButton.setChecked(True)  # Default Option

        self.OhmToColorRadioButton = QRadioButton("Ohm Value to color code", self)
        self.OhmToColorRadioButton.setGeometry(30, 80, 160, 20)  # will be developed soon

        self.line1 = QFrame(self)
        self.line1.setLineWidth(2)
        self.line1.setGeometry(30, 105, 220, 20)
        self.line1.setFrameShape(QFrame.Shape.HLine)

        # input line edit
        QLabel("Enter your resistance value :", self).setGeometry(30, 120, 170, 20)
        self.result = QPlainTextEdit(self)
        self.result.setReadOnly(True)
        self.result.setGeometry(30, 140, 220, 35)

        self.line2 = QFrame(self)
        self.line2.setLineWidth(2)
        self.line2.setGeometry(30, 170, 220, 20)
        self.line2.setFrameShape(QFrame.Shape.HLine)

        # Number of Bands Combo box
        QLabel("Select number of bands :", self).setGeometry(30, 185, 150, 20)
        self.number_of_bands = QComboBox(self)
        self.number_of_bands.addItems(["4 Bands", "5 Bands", "6 Bands"])
        self.number_of_bands.setGeometry(30, 210, 220, 25)
        self.number_of_bands.setCurrentIndex(-1)
        self.number_of_bands.setPlaceholderText("Choose number of bands")
        self.number_of_bands.currentTextChanged.connect(self.reset_index)
        self.number_of_bands.currentTextChanged.connect(self.selected_band)

        self.line3 = QFrame(self)
        self.line3.setLineWidth(2)
        self.line3.setGeometry(30, 237, 220, 20)
        self.line3.setFrameShape(QFrame.Shape.HLine)

        # band Qrect objects
        self.first_band_rect = QRect(120, 130, 13, 70)
        self.secnd_band_rect = QRect(155, 133, 13, 65)
        self.third_band_rect = QRect(180, 133, 13, 65)
        self.forth_band_rect = QRect(205, 133, 13, 65)
        self.fifth_band_rect = QRect(270, 133, 13, 65)
        self.sixth_band_rect = QRect(313, 130, 13, 70)

        # First band ComboBox
        QLabel("Color of 1st band  :", self).setGeometry(30, 250, 105, 25)
        self.first_band = QComboBox(self)
        self.first_band.setObjectName("first_band")
        self.first_band.setGeometry(30, 275, 100, 25)
        self.first_band.setCurrentIndex(-1)
        self.first_band.setPlaceholderText("Select Color")
        self.first_band.currentTextChanged.connect(self.change_first_band_color)
        self.first_band.currentTextChanged.connect(self.calculate_resistance)

        # secnd band ComboBox
        QLabel("Color of 2nd band :", self).setGeometry(150, 250, 105, 25)
        self.secnd_band = QComboBox(self)
        self.secnd_band.setGeometry(150, 275, 100, 25)
        self.secnd_band.setCurrentIndex(-1)
        self.secnd_band.setPlaceholderText("Select Color")
        self.secnd_band.currentTextChanged.connect(self.change_secnd_band_color)
        self.secnd_band.currentTextChanged.connect(self.calculate_resistance)

        # Third band ComboBox
        QLabel("Color of 3rd band :", self).setGeometry(30, 300, 105, 25)
        self.third_band = QComboBox(self)
        self.third_band.setGeometry(30, 325, 100, 25)
        self.third_band.setCurrentIndex(-1)
        self.third_band.setPlaceholderText("Select Color")
        self.third_band.currentTextChanged.connect(self.change_third_band_color)
        self.third_band.currentTextChanged.connect(self.calculate_resistance)

        # Forth band ComboBox
        QLabel("Color of 4th band :", self).setGeometry(150, 300, 105, 25)
        self.forth_band = QComboBox(self)
        self.forth_band.setGeometry(150, 325, 100, 25)
        self.forth_band.setCurrentIndex(-1)
        self.forth_band.setPlaceholderText("Select Color")
        self.forth_band.currentTextChanged.connect(self.change_forth_band_color)
        self.forth_band.currentTextChanged.connect(self.calculate_resistance)

        # Fifth Band ComboBox
        self.fifth_band_str = QLabel("Color of 5th band :", self)
        self.fifth_band_str.setGeometry(30, 350, 105, 25)
        self.fifth_band = QComboBox(self)
        self.fifth_band.setGeometry(30, 375, 100, 25)
        self.fifth_band.setVisible(False)
        self.fifth_band_str.setVisible(False)
        self.fifth_band.setCurrentIndex(-1)
        self.fifth_band.setPlaceholderText("Select Color")
        self.fifth_band.currentTextChanged.connect(self.change_fifth_band_color)
        self.fifth_band.currentTextChanged.connect(self.calculate_resistance)

        # Sixth band ComboBox
        self.sixth_band_str = QLabel("Color of 6th band :", self)
        self.sixth_band_str.setGeometry(150, 350, 105, 25)
        self.sixth_band = QComboBox(self)
        self.sixth_band.setGeometry(150, 375, 100, 25)
        self.sixth_band.setVisible(False)
        self.sixth_band_str.setVisible(False)
        self.sixth_band.setCurrentIndex(-1)
        self.sixth_band.setPlaceholderText("Select Color")
        self.sixth_band.currentTextChanged.connect(self.change_sixth_band_color)
        self.sixth_band.currentTextChanged.connect(self.calculate_resistance)

        self.copy_value_button = QPushButton("Copy value to clipboard", self)
        self.copy_value_button.setGeometry(298, 355, 150, 45)
        self.copy_value_button.clicked.connect(self.copy_value)

        self.save_button = QPushButton("Save image", self)
        self.save_button.setGeometry(450, 355, 150, 45)
        self.save_button.clicked.connect(self.save_resistor_image)

        self.copy_image_button = QPushButton("Copy image to clipboard", self)
        self.copy_image_button.setGeometry(602, 355, 150, 45)
        self.copy_image_button.clicked.connect(self.copy_image)

    def save_resistor_image(self):
        filename, selected_filter = QFileDialog.getSaveFileName(self, filter='''JPG Format (*.jpg);;PNG Format (*.png);;
        All files (*)''')
        self.canvas.save(filename)

    def copy_value(self):
        clipboard = QClipboard(self)
        clipboard.clear()
        clipboard.setText(self.result.toPlainText())

    def copy_image(self):
        clipboard = QClipboard(self)
        clipboard.clear()
        clipboard.setImage(self.canvas.toImage())

    def selected_band(self, band):
        self.band = band
        if self.band == "4 Bands":
            self.first_band.clear()
            self.first_band.addItems(colors_without_black)

            self.secnd_band.clear()
            self.secnd_band.addItems(colors)

            self.third_band.clear()
            self.third_band.addItems(multipliers)

            self.forth_band.clear()
            self.forth_band.addItems(tolerances)

            self.fifth_band.setVisible(False)
            self.fifth_band_str.setVisible(False)
            self.sixth_band.setVisible(False)
            self.sixth_band_str.setVisible(False)

            # drawing 4 bands
            self.painter.fillRect(self.secnd_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.third_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.forth_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.fifth_band_rect, QColor("#aeb8b1"))

            # Hiding %5th and 6th band
            self.painter.fillRect(self.first_band_rect, QColor("#47e2d9"))
            self.painter.fillRect(self.sixth_band_rect, QColor("#47e2d9"))

            self.resistor_pixmap.setPixmap(self.canvas)
        elif self.band == "5 Bands":
            self.first_band.clear()
            self.first_band.addItems(colors_without_black)

            self.secnd_band.clear()
            self.secnd_band.addItems(colors)

            self.third_band.clear()
            self.third_band.addItems(colors)

            self.forth_band.clear()
            self.forth_band.addItems(multipliers)

            self.fifth_band.clear()
            self.fifth_band.addItems(tolerances)

            self.fifth_band.setVisible(True)
            self.fifth_band_str.setVisible(True)
            self.sixth_band.setVisible(False)
            self.sixth_band_str.setVisible(False)

            self.painter.fillRect(self.first_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.secnd_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.third_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.forth_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.fifth_band_rect, QColor("#aeb8b1"))

            # Hiding 6th band
            self.painter.fillRect(self.sixth_band_rect, QColor("#47e2d9"))

            self.resistor_pixmap.setPixmap(self.canvas)

        elif self.band == "6 Bands":
            self.first_band.clear()
            self.first_band.addItems(colors_without_black)

            self.secnd_band.clear()
            self.secnd_band.addItems(colors)

            self.third_band.clear()
            self.third_band.addItems(colors)

            self.forth_band.clear()
            self.forth_band.addItems(multipliers)

            self.fifth_band.clear()
            self.fifth_band.addItems(tolerances)

            self.sixth_band.clear()
            self.sixth_band.addItems(tempco)

            self.fifth_band.setVisible(True)
            self.fifth_band_str.setVisible(True)
            self.sixth_band.setVisible(True)
            self.sixth_band_str.setVisible(True)

            # Drawing all bands
            self.painter.fillRect(self.first_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.secnd_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.third_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.forth_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.fifth_band_rect, QColor("#aeb8b1"))
            self.painter.fillRect(self.sixth_band_rect, QColor("#aeb8b1"))

            self.resistor_pixmap.setPixmap(self.canvas)

    def reset_index(self):

        # Resetting everything when number of bands has changed
        self.first_band.setCurrentIndex(-1)
        self.secnd_band.setCurrentIndex(-1)
        self.third_band.setCurrentIndex(-1)
        self.forth_band.setCurrentIndex(-1)
        self.fifth_band.setCurrentIndex(-1)
        self.sixth_band.setCurrentIndex(-1)
        self.result.clear()
        self.painter.fillRect(0, 250, 450, 60, QColor("white"))
        self.resistor_pixmap.setPixmap(self.canvas)

    def change_first_band_color(self, color="#aeb8b1"):
        if self.band == "4 Bands":
            self.painter.fillRect(self.secnd_band_rect, QColor(color))
        else:
            self.painter.fillRect(self.first_band_rect, QColor(color))
        self.resistor_pixmap.setPixmap(self.canvas)
        return str(colors.index(self.first_band.currentText()))

    def change_secnd_band_color(self, color="#aeb8b1"):
        if self.band == "4 Bands":
            if color is None:
                self.painter.fillRect(self.secnd_band_rect, QColor("white"))
            else:
                self.painter.fillRect(self.third_band_rect, QColor(color))
        else:
            self.painter.fillRect(self.secnd_band_rect, QColor(color))
        self.resistor_pixmap.setPixmap(self.canvas)

        return str(colors.index(self.secnd_band.currentText()))

    def change_third_band_color(self, color="#aeb8b1"):
        if self.band == "4 Bands":
            self.painter.fillRect(self.forth_band_rect, QColor(color))
            self.resistor_pixmap.setPixmap(self.canvas)
            return multipliers.get(self.third_band.currentText())
        else:
            self.painter.fillRect(self.third_band_rect, QColor(color))
            self.resistor_pixmap.setPixmap(self.canvas)
            return str(colors.index(self.third_band.currentText()))

    def change_forth_band_color(self, color="#aeb8b1"):
        if self.band == "4 Bands":
            self.painter.fillRect(self.fifth_band_rect, QColor(color))
            self.resistor_pixmap.setPixmap(self.canvas)
            return str(tolerances.get(self.forth_band.currentText()))
        else:
            self.painter.fillRect(self.forth_band_rect, QColor(color))
            self.resistor_pixmap.setPixmap(self.canvas)
            return multipliers.get(self.forth_band.currentText())

    def change_fifth_band_color(self, color="#aeb8b1"):
        self.painter.fillRect(self.fifth_band_rect, QColor(color))
        self.resistor_pixmap.setPixmap(self.canvas)
        return str(tolerances.get(self.fifth_band.currentText()))

    def change_sixth_band_color(self, color="#aeb8b1"):
        self.painter.fillRect(self.sixth_band_rect, QColor(color))
        self.resistor_pixmap.setPixmap(self.canvas)
        return str(tempco.get(self.sixth_band.currentText()))

    def calculate_resistance(self):
        self.pen.setColor(QColor("Black"))
        self.painter.setPen(self.pen)
        bahnschrift_font = QFont("bahnschrift", 15)
        self.painter.setFont(bahnschrift_font)
        if self.band == "4 Bands":
            try:
                digits = "{0}{1}".format(self.change_first_band_color(self.first_band.currentText()),
                                         self.change_secnd_band_color(self.secnd_band.currentText()))
                digits = int(digits) * self.change_third_band_color(self.third_band.currentText())
                res = str(digits) + " Ω ± " + self.change_forth_band_color(self.forth_band.currentText()) + "%"
                self.result.setPlainText(res)
                self.painter.fillRect(0, 250, 450, 60, QColor("white"))
                self.painter.drawText(100, 250, 250, 300, Qt.AlignHCenter, res)
                self.resistor_pixmap.setPixmap(self.canvas)
            except (ValueError, TypeError):
                self.result.setPlainText("Some Colors are not specified")
                self.painter.fillRect(0, 250, 450, 60, QColor("white"))
                self.painter.drawText(0, 250, 450, 60, Qt.AlignHCenter, "Some Colors are not specified")
                self.resistor_pixmap.setPixmap(self.canvas)

        elif self.band == "5 Bands":
            try:
                digits = "{0}{1}{2}".format(self.change_first_band_color(self.first_band.currentText()),
                                            self.change_secnd_band_color(self.secnd_band.currentText()),
                                            self.change_third_band_color(self.third_band.currentText()))

                digits = int(digits) * self.change_forth_band_color(self.forth_band.currentText())
                res = str(digits) + " Ω ± " + self.change_fifth_band_color(self.fifth_band.currentText()) + "%"
                self.result.setPlainText(res)
                self.painter.fillRect(0, 250, 450, 60, QColor("white"))
                self.painter.drawText(100, 250, 250, 300, Qt.AlignHCenter, res)
                self.resistor_pixmap.setPixmap(self.canvas)
            except (ValueError, TypeError):
                self.result.setPlainText("Some Colors are not specified")
                self.painter.fillRect(0, 250, 450, 60, QColor("white"))
                self.painter.drawText(0, 250, 450, 60, Qt.AlignHCenter, "Some Colors are not specified")
                self.resistor_pixmap.setPixmap(self.canvas)

        elif self.band == "6 Bands":
            try:
                digits = "{0}{1}{2}".format(str(self.change_first_band_color(self.first_band.currentText())),
                                            str(self.change_secnd_band_color(self.secnd_band.currentText())),
                                            str(self.change_third_band_color(self.third_band.currentText())))

                digits = int(digits) * self.change_forth_band_color(self.forth_band.currentText())
                digits = str(digits) + " Ω ± " + self.change_fifth_band_color(self.fifth_band.currentText()) + "%, "
                res = digits + self.change_sixth_band_color(self.sixth_band.currentText()) + " ppm/°C"
                self.result.setPlainText(res)
                self.painter.fillRect(0, 250, 450, 60, QColor("white"))
                self.painter.drawText(0, 250, 450, 300, Qt.AlignHCenter, res)
                self.resistor_pixmap.setPixmap(self.canvas)
            except (ValueError, TypeError):
                self.result.setPlainText("Some Colors are not specified")
                self.painter.fillRect(0, 250, 450, 60, QColor("white"))
                self.painter.drawText(0, 250, 450, 300, Qt.AlignHCenter, "Some Colors are not specified")
                self.resistor_pixmap.setPixmap(self.canvas)


app = QApplication(sys.argv)
app.setWindowIcon(QIcon(r"icon.png"))
window = MainWindow()
window.show()
app.exec()
