from flask import *
import cv2

ft = cv2.freetype.createFreeType2()
ft.loadFontData("./edukai-3.ttf", 0)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
	render_template('index.html')

@app.route('/api/train', methods=['PUT'])
