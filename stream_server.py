import cv2
import pickle
from sklearn import neighbors
import face_recognition as frc
from flask import Flask, render_template, Response
import warnings
import numpy as np
from multiprocessing import Process

warnings.filterwarnings('ignore', category=UserWarning)

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} #可以接受的副檔名

with open("known_encodings.clf", 'rb') as f:
    known_encodings = pickle.load(f)

ft = cv2.freetype.createFreeType2()
ft.loadFontData("./edukai-3.ttf", 0)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #處理回傳的中文問題

class VideoCamera:
    _camera = None
    @classmethod
    def get_camera(cls):
        if cls._camera is None:
            print('create new camera')
            cls._camera = cls.Camera()
        return cls._camera

    class Camera(object):
        def __init__(self):
            # 利用opencv開啟攝影機
            self.video = cv2.VideoCapture(0)

        def __del__(self):
            self.video.release()

        def get_frame(self):
            _success, image = self.video.read()
            return image

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        frame = VideoCamera.get_camera().get_frame()
        #img = predict(frame)
        #del frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        #del img
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def mark_face(image, name, pos):
    top, right, bottom, left = pos
    # mark face
    cv2.rectangle(image, (left, bottom), (right, top), (255, 0, 0), 2, cv2.LINE_AA)
    # name block
    cv2.rectangle(image, (left, bottom), (right, bottom + 30), (255, 0, 0), -1)

    # put name
    ft.putText(image, name, (left + 5, bottom + 5 + 20), 20, (255, 255, 255), -1, cv2.LINE_AA, True)

    return (name, pos)

def identify():
    while True:
        distance_threshold=0.4
        X_image = VideoCamera.get_camera().get_frame()
        rect_image = np.zeros(X_image.shape, dtype=X_image.dtype)

        X_face_locations = frc.face_locations(X_image)

        faces_encodings = frc.face_encodings(X_image, known_face_locations=X_face_locations)

        if not faces_encodings: # empty
            return X_image

        closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=4)

        are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

        for name, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches):
            if not rec.any():
                name = "unknown"

            mark_face(rect_image, name, loc)

        ret, jpeg = cv2.imencode('.jpg', rect_image)
        print('done identify')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/predict')
def predict():
    return Response(identify(), mimetype='multipart/x-mixed-replace; boundary=frame')

if ＿__name＿__ == '__main__':
    #we need to init camera here because the singleton here is not thread safe
    VideoCamera.get_camera()
    app.run(host='0.0.0.0', debug=True)