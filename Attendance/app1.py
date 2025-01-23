from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index1.html')

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        # Get the image and name from the request
        data = request.get_json()
        image_data = data['image']
        image_name = data['name']

        # Decode the base64 image data
        image_data = image_data.split(',')[1]  # Remove the data URL prefix
        image_bytes = base64.b64decode(image_data)

        # Convert the byte data to a numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Create a safe file name (add timestamp to avoid overwriting)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_image_name = f"{image_name}.png"

        # Save the image
        cv2.imwrite(os.path.join('ImagesAttendance', safe_image_name), img)
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False})

if __name__ == '__main__':
    app.run(debug=True, port=2000)
