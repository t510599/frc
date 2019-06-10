from flask import *
import cv2
from api import *

ft = cv2.freetype.createFreeType2()
ft.loadFontData("./edukai-3.ttf", 0)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

encodings = dict()


@app.route('/')
def index():
	render_template('index.html')

@app.route('/api/train', methods=['PUT'])
	if not request.files:
		return jsonify({'status': 'failed', 'error': 'no_file'}), 400
	if not 'name' in request.form:
		return jsonify({'status': 'failed', 'error': 'no_name'}), 400
	file = list(request.files.values())[0]
	name = request.form['name']
	encoding = train(file)
	encodings[name] = encoding
	return jsonify({'status: succeed'})

@app.route('/api/idnetify', methods=[''])

