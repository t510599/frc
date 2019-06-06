import cv2
import pickle
from sklearn import neighbors
import face_recognition as frc
from flask import Flask, jsonify, request, redirect
import base64
import warnings
import os

warnings.filterwarnings('ignore', category=UserWarning)

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} #可以接受的副檔名

ft = cv2.freetype.createFreeType2()
ft.loadFontData("./edukai-3.ttf", 0)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #處理回傳的中文問題

html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>KNN Face Recognition</title>
</head>
<body>
    <form action="/api/upload" method="POST" name="form" id="form">
        <input type="file" name="file" id="file">
        <input type="text" name="name" id="name">
        <input type="submit" name="submit" value="Submit">
    </form>

    <div id="result"></div>

    <img src="" id="image" style="max-width: 100%; height: auto;">
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <script>
        var $result = document.querySelector("#result");
        var $image = document.querySelector("#image");
        var submit = document.form.submit;

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            submit.disabled = "disabled";
            submit.value = "Processing";
            axios.request({
                method: "PUT",
                data: new FormData(this),
                url: "/api/upload"
            }).then(function (res) {
                console.log(res.data);
                $result.innerHTML = `<p>是否找到人臉: ${(res.data["face_found"] ? "是" : "否")}</p><p>名單: ${res.data["names"].join(", ")}</p>`;
                $image.src = res.data["img"];
            }).catch(function (err) {
                if (err.response) {
                    $result.textContent = err.response.data.status;
                    $image.src = "";
                }
            }).finally(function () {
                submit.disabled = "";
                submit.value = "Submit";
            });
        });
    </script>
</body>
</html>'''

#回傳是否為可接受的檔案格式類型
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def render():
    # 如果不合法則回傳上傳檔案的表單格式，請使用者重新上傳檔案:
    return html

@app.route('/api/upload', methods=["PUT"])
def upload_image():
    # 若上傳的檔案合法
    if request.method == 'PUT':
        if 'file' not in request.files:
            return jsonify({"status": "no file"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"status": "no filename"}), 400

        if 'name' not in request.form:
            return jsonify({"status": "no name"}), 400
        name = request.form['name']
        if name == '':
            return jsonify({"status": "no name"}), 400

        if file and allowed_file(file.filename):
            # 若檔案合法則進入辨識階段並回傳結果.
            return detect_faces_in_image(file, name)
        else:
            return jsonify({"status": "image not allowed"}), 415 # Unsupported Media Type
    else:
        return jsonify({"status": "wrong method"}), 405 # Method Not Allowed

def detect_faces_in_image(file_stream, name):
    img = frc.load_image_file(file_stream)

    status, img = find(img, name)

    _ret, buffer = cv2.imencode('.png', cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    data_url = base64.b64encode(buffer)

    del buffer, img
    # 回傳結果呈現在網頁上
    result = {
        "face_found": status,
        "names": [name],
        "img": "data:image/png;base64,{}".format(data_url.decode())
    }
    return jsonify(result)

def find(X_image, name, distance_threshold=0.4):
    X_face_locations = frc.face_locations(X_image)
    faces_encodings = frc.face_encodings(X_image, known_face_locations=X_face_locations)

    if not X_face_locations:
        return False, X_image
    mark_face(X_image, name, X_face_locations[0])
    known = dict()
    if 'known_encodings.clf' in os.listdir():
        with open('known_encodings.clf', 'rb') as f:
            known = pickle.load(f)
    known[name] = faces_encodings[0]
    with open('known_encodings.clf', 'wb') as f:
        pickle.dump(known, f)
    return True, X_image

def mark_face(image, name, pos):
    top, right, bottom, left = pos
    # mark face
    cv2.rectangle(image, (left, bottom), (right, top), (255, 0, 0), 2, cv2.LINE_AA)
    # name block
    cv2.rectangle(image, (left, bottom), (right, bottom + 30), (255, 0, 0), -1)

    # put name
    ft.putText(image, name, (left + 5, bottom + 5 + 20), 20, (255, 255, 255), -1, cv2.LINE_AA, True)

    return (name, pos)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)