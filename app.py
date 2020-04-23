from flask import Flask, render_template, send_from_directory
import time
import json
import os


app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd() + '/icons'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/home')
def hello():


    return render_template('display.html')


@app.route('/update_screen', methods=['GET'])
def hello_name():
    with open("data.json", "r") as f:
        response = json.load(f)
    if response["current_occupancy"] >= response["maximum_occupancy"]:
        response["occupancy_color"] = "darkred"
        response["status"] = "STOP"
    else:
        response["occupancy_color"] = "darkgreen"
        response["status"] = "GO"
    return json.dumps(response)


@app.route('/get_icon/<icon>', methods=['GET'])
def get_icon(icon):
    return send_from_directory(UPLOAD_FOLDER, icon)


@app.route('/show_image', methods=['GET'])
def show_image():
    return render_template('img_show.html')





if __name__ == '__main__':
    app.run(port=5000, debug=True)