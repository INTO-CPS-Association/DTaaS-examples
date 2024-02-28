#!/usr/bin/python3
import importlib.util
import sys
import subprocess


# Install dependencies
pip_dependencies = ['PyQt5','watchdog','matplotlib', 'pandas','pyarrow']
for package in pip_dependencies:
    if (spec := importlib.util.find_spec(package)) is not None:
        # Package is found
        pass
    else:
        # Install package
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Imports
import os
import json
import argparse
import signal
import pandas as pd
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5 import QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5 import TimerQT, FigureCanvasQT as FigureCanvas
from matplotlib.backends.backend_qt5 import FigureCanvas
from matplotlib.figure import Figure


# Debug
DEBUG = False
def log(value):
    if(DEBUG):
        print(value)



# Arguments

parser = argparse.ArgumentParser(
    prog='plot_realtime_dot_xt.py',
    description='''Plot data at runtimefrom a CSV file in xy coordinates.
        Example 1: Single x,y pair
        \tplot_realtime_dot_xy.py ./ file.csv -l "{FMU}.Ins1.x,{FMU}.Ins1.y"
        Example 2: Two x,y pairs
        \tplot_realtime_dot_xy.py ./ file.csv -l "{FMU}.Ins1.x,{FMU}.Ins1.y" "time,{FMU}.Ins1...
        Example 3: Including title and labels
        \tplot_realtime_dot_xy.py ./ file.csv -l -t "Titel" -lx "Label_x" -ly "Label_y" "{FMU...''',
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('csv_dir', help='Path to look for the output file with the .csv extension', type=str)
parser.add_argument('file_name',help='csv file name.',type=str)
parser.add_argument('-t','--title', help='-t TitleInStringFormat', type=str, nargs='?', required=False, default="")
parser.add_argument('-lx','--label-x', help='-lx LabelInStringFormat', type=str, nargs='?', required=False, default="")
parser.add_argument('-ly','--label-y', help='-ly LabelInStringFormat', type=str, nargs='?', required=False, default="")
parser.add_argument('-rt','--refresh-time', help='-rt RefreshTimeInMilliseconds', type=int, nargs='?', required=False, default=250)
parser.add_argument('-l','--xypairs-list',
                        help='-l "{FMU}.Ins1.x,{FMU}.Ins1.y" "time,{FMU}.Ins1.y"',
                        type=str,
                        nargs='+',
                        required=True)
OBSERVE_PATH = parser.parse_args().csv_dir
log("OBSERVE_PATH: " + OBSERVE_PATH)
FILENAME = parser.parse_args().file_name
log("FILENAME: " + FILENAME)
XYPAIRS = parser.parse_args().xypairs_list
log("XYPAIRS: " + str(XYPAIRS))
TITLE = parser.parse_args().title
log("TITLE: " + str(TITLE))
LABEL_X = parser.parse_args().label_x
log("LABEL_X: " + str(LABEL_X))
LABEL_Y = parser.parse_args().label_y
log("LABEL_Y: " + str(LABEL_Y))
REFRESH_TIME = parser.parse_args().refresh_time
log("REFRESH_TIME: " + str(REFRESH_TIME))

# File and Watcher
class File():
    def __init__(self, p):
        self.filePath = p
        self.data = None

if OBSERVE_PATH[-1] != '/':
    OBSERVE_PATH = OBSERVE_PATH + '/'
log("OBSERVE_PATH + FILENAME: " + OBSERVE_PATH + FILENAME)
csvFile = File(OBSERVE_PATH + FILENAME)

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.processFileData()
    def on_created(self, event):
        log("ON_CREATED_EVENT file: " + event.src_path)
        if FILENAME in event.src_path:
            self.processFileData()
        return super().on_created(event)
    def on_deleted(self, event):
        log("ON_DELETED_EVENT file: " + event.src_path)
        if FILENAME in event.src_path:
            self.processFileData()
        return super().on_deleted(event)
    def on_modified(self, event):
        log("ON_MODIFIED_EVENT file: " + event.src_path)
        if FILENAME in event.src_path:
            self.processFileData()
        return super().on_modified(event)
    def processFileData(self):
            log("Updating fileContent")
            try:
                csvFile.data =  json.loads(pd.read_csv(csvFile.filePath).to_json())
            except Exception as e:
                log(e)
                log("processFileData() - Invalid file")
                return


observer = Observer()
fileEventHandler = FileEventHandler()
observer.schedule(fileEventHandler, parser.parse_args().csv_dir, recursive=True)
#observer.start()

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
        self.timer = self.canvas.new_timer(REFRESH_TIME, [(self.update_data, (), {})])
        self.timer.start()

    def update_data(self):
        log("Updating START")
        log("Total number of xypairs: " + str(len(XYPAIRS)))
        
        self.axes.clear()
        global XYPARIS
        xy_data = []
        splitted = []
        for index in range(0, len(XYPAIRS)):
            splitted = XYPAIRS[index].split(',')  
            if (len(splitted) > 0):
                try:
                    for item in csvFile.data:
                        if ( splitted[0] == item ):
                            d = {
                                'x_key': splitted[0],
                                'x_data' : [],
                                'y_key': splitted[1],
                                'y_data' : []
                            }
                            xy_data.append(d)
                except Exception as e:
                    log(e)
            else:
                log("update_data() - Invalid xypair")
                return
        try:
            log("Total number of keys: " + str(len(csvFile.data)))
        except:
            return
        for index in range(0, len(csvFile.data[str(xy_data[0]['x_key'])])):
            for item in xy_data:
                item['x_data'].append(csvFile.data[str(item['x_key'])][str(index)])
                item['y_data'].append(csvFile.data[str(item['y_key'])][str(index)])

        colors = ['red','blue','green','purple','yellow','magenta','cyan','black','olive']
        for item in xy_data:
            line, = self.axes.plot(item['x_data'], item['y_data'])
            line.set_label(item['x_key'] + ',' + item['y_key'])
            line.set_marker('o'),
            line.set_color(colors.pop(0))
            line.set_markerfacecolor('None')
            line.set_linestyle('None')
        self.axes.set_title(TITLE if TITLE != "" else datetime.datetime.now().strftime("%B %d, %Y - %H:%M") + " - Plot of '" + FILENAME + "'")
        self.axes.set_xlabel(LABEL_X if LABEL_X != "" else "")
        self.axes.set_ylabel(LABEL_Y if LABEL_Y != "" else "")
        self.axes.legend()
        self.axes.grid(color='gray', linestyle='dashed')
        log("Updating END")
        log("Updated Data. Refreshing plot...")
        self.canvas.draw()

app = QtWidgets.QApplication(sys.argv)
window = ApplicationWindow()

# Terminate/kill handlers
def shutdown_handler(signal_number, frame): 
    print("\nShutting down")
    window.timer.stop()
    observer.stop()
    QtWidgets.QApplication.quit()
if os.name == 'nt':
    signal.signal(signal.SIGBREAK, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# Run
window.showMaximized()
window.activateWindow()
sys.exit(app.exec_())
