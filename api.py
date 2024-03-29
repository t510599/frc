from face_recognition import face_locations, face_encodings, face_distance, load_image_file
from cv2 import resize
from numpy import argmin
class NoFaceDetectedError(Exception):
	pass

#input: an image that contains exactly one face
#output: the encoding of that face
#exception: if no face detected, raise NoFaceDetectedError
def train(file_stream):
	image = load_image_file(file_stream)
	location = face_locations(image)
	if not location:
		raise NoFaceDetectedError()
	encodings = face_encodings(image, location)
	return encodings[0]

#input: an image that contains exactly one face
#input: a dictionary represent the encodings we knew
#output: a tuple with format (top, right, bottom, left, name)
def identify(image, known_dict):
	locations = face_locations(image)
	if not locations:
		raise NoFaceDetectedError()
	unknown_encoding = face_encodings(image, locations)[0]
	pos = (locations[0][0], locations[0][1], locations[0][2], locations[0][3])
	distances = face_distance(list(known_dict.values()), unknown_encoding)
	if distances.size == 0:
		return (pos, "unknown")
	index = argmin(distances)
	if distances[index] <= 0.4:
		return (pos, list(known_dict.keys())[index])
	else:
		return (pos, "unknown")

