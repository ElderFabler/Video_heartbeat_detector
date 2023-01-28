import sys
from time import sleep
#import cv2
import pyqtgraph as pg
from PyQt5 import QtWidgets,QtCore,QtGui
from heartbeat import cameraCap

class HBThread(QtCore.QThread):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.running = True

    changePixmap = QtCore.pyqtSignal(QtGui.QImage,object)

    def run(self):
        for img,mass in cameraCap():
            h,w,l = img.shape
            bpl = l*w
            convert = QtGui.QImage(img.data,w,h,bpl,QtGui.QImage.Format_RGB888)
            scl = convert.scaled(640,480,QtCore.Qt.KeepAspectRatio)
            self.changePixmap.emit(scl,mass)
            if self.running == False:
                break
            else:
                pass



class HBWind(QtWidgets.QWidget):
    def __init__(self,parent = None):
        super().__init__(parent)

        self.camera = QtWidgets.QLabel()
        self.puls = QtWidgets.QLabel("Wait",alignment = QtCore.Qt.AlignCenter)
        self.shed_av = pg.PlotWidget()
        self.shed_av_d = self.shed_av.plot(name = "Average")
        self.shed_filt = pg.PlotWidget()
        self.shed_filt_d = self.shed_filt.plot(name = "Filtered signal")
        #self.shed_filtn = pg.PlotWidget()
        #self.shed_filtn_d = self.shed_filtn.plot(name = "Filtered adn normalized signal")
        self.shed_fft = pg.PlotWidget()
        self.shed_fft_d = self.shed_fft.plot(name = "Spectrum")

        #self.puls.setAlignment()
        self.setStyleSheet("QLabel {font-size: 48px}")

        vlout_sheds = QtWidgets.QVBoxLayout()
        vlout_sheds.addWidget(self.shed_av)
        vlout_sheds.addWidget(self.shed_filt)
        #vlout_sheds.addWidget(self.shed_filtn)
        vlout_sheds.addWidget(self.shed_fft)

        vlout_camera = QtWidgets.QVBoxLayout()
        vlout_camera.addWidget(self.camera)
        vlout_camera.addWidget(self.puls)

        hlout = QtWidgets.QHBoxLayout()
        hlout.addLayout(vlout_camera)
        hlout.addLayout(vlout_sheds)
        self.setLayout(hlout)

        self.th = HBThread(self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()

    @QtCore.pyqtSlot(QtGui.QImage,object)
    def setImage(self,image,arr):
        self.camera.setPixmap(QtGui.QPixmap.fromImage(image))
        self.shed_av_d.setData(arr[0])
        self.shed_filt_d.setData(arr[1])
        #self.shed_filtn_d.setData(arr[2])
        self.shed_fft_d.setData(arr[3])
        if len(arr[0]) < 1800:
            self.puls.setText(f"Wait: {60-int(len(arr[0])/30)} sec\nCollecting data...")
        else:
            self.puls.setText(f"Your heart rate is: {str(arr[4])}")

    def closeEvent(self,e):
        self.hide()
        self.th.running = False
        self.th.wait(5000)
        e.accept()
        QtWidgets.QWidget.closeEvent(self,e)



if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        win = HBWind()
        win.setWindowTitle("HeartBeat Detector")
        win.show()
        sys.exit(app.exec_())
    except Exception as ex:
        with open("log_file.txt","w") as file_w:
            file_w.write(str(ex))