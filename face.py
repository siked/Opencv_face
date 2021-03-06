#coding=utf-8
### Imports ###################################################################

import multiprocessing as mp
import cv2
import os
import sys
import time
import numpy as np


### Setup #####################################################################

resX = 640
resY = 480

# The face cascade file to be used
face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

#三种识别算法
#model = cv2.createEigenFaceRecognizer()
#model = cv2.createFisherFaceRecognizer()
#model = cv2.createLBPHFaceRecognizer()

model = cv2.face.EigenFaceRecognizer_create()


t_start = time.time()
fps = 0


### Helper Functions ##########################################################

def normalize(X, low, high, dtype=None):
    """Normalizes a given array in X to a value between low and high."""
    X = np.asarray(X)
    minX, maxX = np.min(X), np.max(X)
    # normalize to [0...1].
    X = X - float(minX)
    X = X / float((maxX - minX))
    # scale to [low...high].
    X = X * (high-low)
    X = X + low
    if dtype is None:
        return np.asarray(X)
    return np.asarray(X, dtype=dtype)


def load_images(path, sz=None):
    c = 0
    X,y = [], []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    filepath = os.path.join(subject_path, filename)
                    if os.path.isdir(filepath):
                        continue
                    img = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                    if (img is None):
                        print ("image " + filepath + " is none")
                    else:
                        print (filepath)
                    # resize to given size (if given)
                    if (sz is not None):
                        img = cv2.resize(img, (200, 200))

                    X.append(np.asarray(img, dtype=np.uint8))
                    y.append(c)
                # except IOError, (errno, strerror):
                #     print ("I/O error({0}): {1}".format(errno, strerror))
                except:
                    print ("Unexpected error:", sys.exc_info()[0])
                    raise
            print (c)
            c = c+1


    print (y)
    return [X,y]

def get_faces( img ):

    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return faces, img, gray

def draw_frame( faces, img, gray ):

    global xdeg
    global ydeg
    global fps
    global time_t

    # Draw a rectangle around every face
    for ( x, y, w, h ) in faces:
        cv2.rectangle(img,( x, y ),( x + w, y + h ), ( 200, 255, 0 ), 2 )
        #-----rec-face
        roi = gray[x:x+w, y:y+h]
        try:
            roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_LINEAR)
            params = model.predict(roi)
            sign=("%s %.2f" % (names[params[0]], params[1]))
            print("%s = %.2f" %(params[0],params[1]/1000))
            cv2.putText(img, sign, (x, y+5), cv2.FONT_HERSHEY_SIMPLEX, 1, ( 0, 0, 255 ), 5 )
            cv2.imshow('frame', img)
            # if (params[0] == 0):
            #     cv2.imwrite('face_rec.jpg', img)
        except:
            cv2.putText(img, "NO Face", (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow('frame', img)
            continue


    # Calculate and show the FPS
    fps = fps + 1
    sfps = fps / (time.time() - t_start)
    cv2.putText(img, "FPS : " + str( int( sfps ) ), ( 10, 15 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )

    cv2.imshow( "recognize-face", img )


### Main ######################################################################

if __name__ == '__main__':

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,resX)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT,resY)
    pool = mp.Pool(processes=4)


    # -----------init-rec----------
    # 人名要与datamap.csv里面的对应，不要弄错了顺序
    names = ['liu', 'cheng','li']
    if len(sys.argv) < 2:
        print ("USAGE: facerec.py 人脸数据存放路径 [数据对应表]")
        sys.exit()

    [X,y] = load_images(sys.argv[1])
    y = np.asarray(y, dtype=np.int32)

    if len(sys.argv) == 3:
        out_dir = sys.argv[2]

    model.train(np.asarray(X), np.asarray(y))
    # ------init finish---------
    print("-------")
    # read, img = camera.read()
    #
    # pr1 = pool.apply_async( get_faces, [ img ] )
    # read, img = camera.read()
    while (True):
        read, img = camera.read()

        cv2.imshow('frame1', img)

        # pr1 = pool.apply_async( get_faces, [ img ] )
        faces, img, gray=get_faces(img)
        # print(faces, img, gray)
        draw_frame( faces, img, gray )

        if cv2.waitKey(1000 // 12) & 0xff == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()