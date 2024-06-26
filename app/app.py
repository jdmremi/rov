from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QHBoxLayout, QMainWindow, QStatusBar
from PyQt5.QtGui import QIcon
import logging
import coloredlogs
import sys
import time

# local
from videowidget import VideoWidget
from joystickthread import JoystickThread
from arduinothread import ArduinoThread

WINDOW_TITLE = "ROV Control"
GREEN_TEXT_CSS = "color: green"
RED_TEXT_CSS = "color: red"
YELLOW_TEXT_CSS = "color: yellow"
ICON_PATH = "./assets/logo.png"

coloredlogs.install(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Main(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(width, height)

        logger.info("MainWindow initialized")
        logger.info(f"Display found: Width = {width}, Height = {height}")

        self.__layout = QHBoxLayout()

        # Initialize video widget
        self.__video_widget = VideoWidget(width, height)

        self.__layout.addWidget(self.__video_widget)
        self.__container = QWidget()
        self.__container.setLayout(self.__layout)

        # Status bar related widgets, etc.
        self.__status_bar = QStatusBar()
        self.__status_bar_widgets = {
            "joystickStatus": QLabel("Joystick status: Disconnected"),
            # "arduinoTemperature": QLabel(text="Arduino Temperature: 0.00°C"),
            # "arduinoHumidity": QLabel(text="Humidity: 0.00% RH"),
            "clawStatus": QLabel(text="Claw status: Open/Closed..."),
            "forwardBackwardThrustStatusLabel": QLabel(),
            "leftRightThrustStatusLabel": QLabel(),
            "verticalThrustStatusLabel": QLabel(),
            "pitchThrustStatusLabel": QLabel()
        }
        self.__status_bar.addWidget(QLabel(text=" "))
        # Add all of the relevant widgets to the status bar
        for widgetName, widget in self.__status_bar_widgets.items():
            self.__status_bar.addWidget(widget)
            logger.info(f"Successfully initialized {widgetName} widget!")
            # Spacing in between widgets
            self.__status_bar.addWidget(QLabel(text=" | "))

        # <3
        self.__status_bar.addWidget(QLabel(text="Made with ❤️"))

        self.setCentralWidget(self.__container)
        self.setStatusBar(self.__status_bar)

        # Initialize the Arduino thread
        self.__arduino_thread = ArduinoThread()
        self.__arduino_thread.arduino_data_channel_signal.connect(
            self.update_arduino_status)

        # Initialize the Joystick thread and pass in the relevant progress bars/labels so that the thread can update them.
        self.__joystick_thread = JoystickThread(
            self.__status_bar_widgets.get("forwardBackwardThrustStatusLabel"),
            self.__status_bar_widgets.get("leftRightThrustStatusLabel"),
            self.__status_bar_widgets.get("verticalThrustStatusLabel"),
            self.__status_bar_widgets.get("pitchThrustStatusLabel"),
            self.__status_bar_widgets.get("joystickStatus"),
            self.__arduino_thread,
            self.__video_widget.get_video_thread()
        )

        # Start the program with the window fully maximized
        self.showMaximized()

    def update_arduino_status(self, data):
        # Update the status bar with data from the Arduino
        """
        temperature = data.get("temp", 0.0)
        humidity = data.get("humidity", 0.0)
        logger.debug(
            f"Received data - Temperature: {temperature}, Humidity: {humidity}%")
        self.__status_bar_widgets.get("arduinoTemperature").setText(
            f"Temperature: {temperature:.2f}°C")
        self.__status_bar_widgets.get("arduinoHumidity").setText(
            f"Humidity: {humidity:.2f}%")
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON_PATH))
    app.setApplicationName(WINDOW_TITLE)
    screen = app.primaryScreen()
    a = Main(screen.size().width(), screen.size().height())
    # So that our Arduino doesn't freak out
    time.sleep(7.5)
    a.show()
    sys.exit(app.exec_())
