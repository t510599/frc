from flask import *
import cv2
from api import *
import pickle

ft = cv2.freetype.createFreeType2()
ft.loadFontData("./edukai-3.ttf", 0)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

class VideoCamera:
    _camera = None
    @classmethod
    def get_camera(cls):
        if cls._camera is None:
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

def mark_face(image, name, pos):
    top, right, bottom, left = pos
    # mark face
    cv2.rectangle(image, (left, bottom), (right, top), (255, 0, 0), 2, cv2.LINE_AA)
    # name block
    cv2.rectangle(image, (left, bottom), (right, bottom + 30), (255, 0, 0), -1)

    # put name
    ft.putText(image, name, (left + 5, bottom + 5 + 20), 20, (255, 255, 255), -1, cv2.LINE_AA, True)

    return (name, pos)
    
def gen():
    while True:
        frame = VideoCamera.get_camera().get_frame()
        pos, name = identify(frame, encodings)
        mark_face(frame, name, pos)
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    render_template('index.html')

@app.route('/api/train', methods=['PUT'])
def train():
    if not request.files:
        return jsonify({'status': 'failed', 'error': 'no_file'}), 400
    if not 'name' in request.form:
        return jsonify({'status': 'failed', 'error': 'no_name'}), 400
    file = list(request.files.values())[0]
    name = request.form['name']
    encoding = train(file)
    encodings[name] = encoding
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)
    return jsonify({'status: succeed'})

@app.route('/api/identify')
def identify():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    encodings = dict()
    try:
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
    except:
        #file not found
        #skip it
        pass
    # make sure singleton
    VideoCamera.get_camera()
    app.run(host='0.0.0.0', debug=True)