# Face Recognition Live Stream Demo
For CK demostration.

## Requirement
- Flask
- numpy
- opencv (with [freetype](https://docs.opencv.org/master/d9/dfa/classcv_1_1freetype_1_1FreeType2.html) support)
- [ageitgey/face_recognition](https://github.com/ageitgey/face_recognition)

## Libraries
- axios
- TocasUI

## Use
```bash
python3 backend.py
```
Now you can connect to `localhost:5000` with browser.

## Notice
`navigator.mediaDevices.getUserMedia()` works only in secure contexts (localhost or site with https://).
More info at [MDN](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia#Security).