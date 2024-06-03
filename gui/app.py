from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QHBoxLayout, QMainWindow, QStatusBar, QProgressBar
import logging
import coloredlogs
import sys

# local
from videowidget import VideoWidget
from joystickthread import JoystickThread
from arduinothread import ArduinoThread

WINDOW_TITLE = "ROV Control"
GREEN_TEXT_CSS = "color: green"
RED_TEXT_CSS = "color: red"
YELLOW_TEXT_CSS = "color: yellow"

coloredlogs.install(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Main(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(width, height)

        logger = logging.getLogger(__name__)
        logger.info("MainWindow initialized")
        logger.info(f"Display found: Width = {
            width}, Height = {height}")

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
            "arduinoTemperature": QLabel(text="Arduino Temperature: 0.00°C"),
            "arduinoVoltage": QLabel(text="Arduino Voltage: 0.00V"),
            "clawStatus": QLabel(text="Claw status: Open/Closed..."),
            "xThrust": QProgressBar(),
            "yThrust": QProgressBar(),
            "zThrust": QProgressBar()
        }
        self.__status_bar.addWidget(QLabel(text=" "))
        # Add all of the relevant widgets to the status bar
        for widgetName, widget in self.__status_bar_widgets.items():
            self.__status_bar.addWidget(widget)
            logger.info(f"Successfully initialized {
                widgetName} widget!")
            # Spacing in between widgets
            self.__status_bar.addWidget(QLabel(text=" | "))
        # <3
        self.__status_bar.addWidget(QLabel(text="Made with ❤️"))

        self.setCentralWidget(self.__container)
        self.setStatusBar(self.__status_bar)

        # Initialize the Joystick thread and pass in the relevant progress bars/labels so that the thread can update them.
        # We pass in the arduino thread so that our joystick can send the data to it directly.
        # It is also used here to update GUI elements.
        self.__arduino_thread = ArduinoThread()
        self.__joystick_thread = JoystickThread(
            self.__status_bar_widgets.get("xThrust"),
            self.__status_bar_widgets.get("yThrust"),
            self.__status_bar_widgets.get("zThrust"),
            self.__status_bar_widgets.get("joystickStatus"),
            self.__arduino_thread
        )

        # Start the program with the window fully maximized
        self.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    a = Main(screen.size().width(), screen.size().height())
    a.show()
    sys.exit(app.exec_())