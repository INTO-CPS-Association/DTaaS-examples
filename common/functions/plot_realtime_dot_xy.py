#!/usr/bin/python3
import importlib.util
import sys
import subprocess






# Install dependencies
pip_dependencies = ['PyQt5','watchdog','matplotlib']
for package in pip_dependencies:
    if (spec := importlib.util.find_spec(package)) is not None:
        # Package is found
        pass
    else:
        # Install package
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Imports
import os
import argparse
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt import TimerQT, FigureCanvasQT as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


# Debug
DEBUG = True
def log(value):
    if(DEBUG):
        print(value)



# Arguments
parser = argparse.ArgumentParser(
    prog='plot_realtime_dot_xt.py',
    description='Plot real-time data from a CSV file in xy coordinates. Example: plot_realtime_dot_xy.py file.csv {FMU}.Ins1.x,{FMU}.Ins1.y',
)
parser.add_argument('csv_dir', help='Path to look for the output file with the .csv extension', type=str)
parser.add_argument('file_name',help='csv file name.',type=str)
parser.add_argument('-l','--xypairs-list',
                        help='-l {FMU}.Ins1.x,{FMU}.Ins1.y {FMU}.Ins2.x,{FMU}.Ins2.y',
                        type=str,
                        nargs='+',
                        required=True)
OBSERVE_PATH = parser.parse_args().csv_dir
log("OBSERVE_PATH: " + OBSERVE_PATH)
FILENAME = parser.parse_args().file_name
log("FILENAME: " + FILENAME)
XYPAIRS = parser.parse_args().xypairs_list
log("XYPAIRS: " + str(XYPAIRS))


# File and Watcher
class File():
    def __init__(self, p):
        self.filePath = p
        self.file = open(self.filePath, 'r')
        self.lines = []
        self.header_line = None

if OBSERVE_PATH[-1] != '/':
    OBSERVE_PATH = OBSERVE_PATH + '/'
log("OBSERVE_PATH + FILENAME: " + OBSERVE_PATH + FILENAME)

csvFile = File(OBSERVE_PATH + FILENAME)

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.rows = []
    def on_created(self, event):
        if FILENAME in event.src_path:
            csvFile.file.open(csvFile.filePath,'r')
            csvFile.header_line = None
            csvFile.lines = []
        return super().on_created(event)
    def on_deleted(self, event):
        if FILENAME in event.src_path:
            csvFile.header_line = None
            csvFile.lines = []
            csvFile.file.close()
        return super().on_deleted(event)
    def on_modified(self, event):
        log("ON_MODIFIED_EVENT file: " + event.src_path)
        if FILENAME in event.src_path:
            log("Updating fileContent")
            lines = csvFile.file.readlines()
            if len(lines) == 0:
                return
            if len(lines[0].split('{')) > 2:
                csvFile.header_line = lines[0].strip()
                lines.pop(0)
            for line in lines:
                csvFile.lines.append(line.strip())
        return super().on_modified(event)
        
observer = Observer()
fileEventHandler = FileEventHandler()
observer.schedule(fileEventHandler, parser.parse_args().csv_dir, recursive=True)
observer.start()

# Matplotlib Qt Window
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self._timer = TimerQT

        # Main
        super().__init__()
        self.main = QtWidgets.QWidget()
        self.setCentralWidget(self.main)

        # Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QtWidgets.QVBoxLayout(self.main)
        layout.addWidget(self.canvas)

        # Axes
        self.axes = self.figure.add_subplot(1,1,1)

        # Timer
        self.timer = self.canvas.new_timer(250, [(self.update_data, (), {})])

    def update_data(self):
        log("Updating")

# Terminate/kill handlers
def shutdown_handler(signal_number, frame): 
    print("\nShutting down")
    observer.stop()
    csvFile.file.close()
    QtWidgets.QApplication.quit()
if os.name == 'nt':
    signal.signal(signal.SIGBREAK, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# Run
app = QtWidgets.QApplication(sys.argv)
window = ApplicationWindow()
window.show()
window.activateWindow()
sys.exit(app.exec_())
