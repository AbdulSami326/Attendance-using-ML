from flask import Flask, render_template, redirect, url_for
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import time  # Import time module

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/take-attendance', methods=['POST'])
def attendance():
    path = 'ImagesAttendance'
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        if not cl.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            print(f"Skipping non-image file: {path}/{cl}")
            continue
        curImg = cv2.imread(f'{path}/{cl}')
        if curImg is None:
            print(f"Error reading image: {path}/{cl}")
            continue
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open('Attendance.csv','a+') as f:
            myDataList = f.readlines()
            nameList = [line.split(',')[0] for line in myDataList]
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)
    start_time = time.time()  # Start time

    while True:
        success, img = cap.read()
        
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)
                
                # Release the webcam and close OpenCV windows
                cap.release()
                cv2.destroyAllWindows()
                
                # Redirect to home after marking attendance
                return "ATTENDANCE MARKED"

        # Check if 10 seconds have passed
        if time.time() - start_time > 5:
            cap.release()
            cv2.destroyAllWindows()
            return "Unsuccessful Attempt"  # Return if 10 seconds have passed

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        

    # Release the webcam and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
