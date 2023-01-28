import cv2
import numpy as np
import numpy.fft as npf
from scipy import signal as sig
import matplotlib.pyplot as plt


def cameraCap():
    try:
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        cap = cv2.VideoCapture(0)
        cap.set(3,512)
        cap.set(4,512)
        minW = 0.1*cap.get(3)
        minH = 0.1*cap.get(4)

        av_arr = np.array([])
        av_arr_n = np.array([])
        filtarr = np.array([])
        filt_n = np.array([])
        ftt = np.array([])
        rez = []
        b, a = sig.butter(10, [40, 240], btype = 'bp', analog = False,fs = 1024)
        b1, a1 = sig.butter(3, 50, btype = 'low', analog = False,fs = 300)
        filt_coef = [b,a,b1,a1]
        lenth = 1800

        while True:
            ret,val = cap.read()
            img = cv2.flip(val,1)
            gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
            #img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor = 1.2,
                minNeighbors = 4,
                minSize = (int(minW),int(minH))
            )

            fps = cap.get(cv2.CAP_PROP_FPS)

            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.rectangle(img,(int(x+w/6),int(y+h/10)),(int(x+5*w/6),int(y+9*h/10)),(255,255,0),2)
                roi_color = img[int(y+h/10):int(y+9*h/10),int(x+w/6):int(x+5*w/6),1]

            #if count > 30:
            try:
                av = np.mean(roi_color)
                av_arr = np.append(av_arr,av)
                if len(av_arr) > lenth:
                    av_arr = av_arr[-lenth::]
                else:
                    pass
                """ av_arr_m = av_arr-np.mean(av_arr)
                av_max = np.max(np.absolute(av_arr_m))
                av_arr_n = np.around(av_arr_m/av_max,decimals = 3) """
                #if len(av_arr) >= 300:
                filtarr,filt_n,rez,ftt = filtration(av_arr,filt_coef)
            except Exception as ex:
                print(ex)
            rgbImg = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            yield rgbImg, [av_arr,filtarr,filt_n,ftt,rez]
            """ cv2.imshow("video",img)
            cv2.imshow("small",roi_color)

            key = cv2.waitKey(30) & 0xff
            if key == 27:
                break """
        cap.release()
    except Exception as ex:
        with open("log_file_cam.txt","w") as file_w:
            file_w.write(str(ex))

def filtration(srp,coef_list):
    filt_n = np.array([])
    filtsig = sig.filtfilt(coef_list[0],coef_list[1],srp)
    #filtsig = sig.filtfilt(coef_list[2],coef_list[3],filtsig1)
    """ if len(filtsig) >= 1800:
        x = np.linspace(0,1800,1800)
        xd = np.linspace(0,1800,32000)
        filt_n = np.interp(xd,x,filtsig) """
    #triedIBI(filt_n)
    ftt = npf.fft(filtsig)
    absol = np.abs(ftt)
    absol = absol[:500]
    rez = np.argmax(absol)
    return filtsig, filt_n, rez, absol

def triedIBI(sig):
    for i in np.where(sig == 0):
        print(i)

if __name__ == "__main__":
    cameraCap()
