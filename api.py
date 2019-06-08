from face_recognition import face_locations, face_encodings, face_distance
from cv2 import resize
from numpy import argmin
class NoFaceDetectedError(Exception):
	pass

#input: an image that contains exactly one face
#output: the encoding of that face
#exception: if no face detected, raise NoFaceDetectedError
def train(image):
	location = face_locations(image)
	if not location:
		raise NoFaceDetectedError()
	encodings = face_encodings(image, location)
	return encodings[0]

#input: an image that contains exactly one face
#input: a dictionary represent the encodings we knew
#output: a tuple with format (top, right, bottom, left, name)
def identify(image, known_dict):
	image = resize(image, (0, 0), fx=0.25, fy=0.25)
	location = face_locations(image)[0]
	if not locations:
		raise NoFaceDetectedError()
	unknown_encoding = face_encodings(image, [locations])[0]
	distances = face_distance(list(known_dict.values()), unknown_encoding)
	index = argmin(distances)
	if distances[index] <= 0.4:
		return (location[0], location[1], location[2], location[3], list(known_dict.keys())[index])
	else:
		return (location[0], location[1], location[2], location[3], "unknown")

