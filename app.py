from flask import Flask, render_template, send_from_directory
import time
import json
import os
from test import get_data, get_aotc

app = Flask(__name__)
initial_data = get_aotc('192.168.1.100')

old_aotc = initial_data["occupancy"]
old_in = initial_data["in"]
old_out = initial_data["out"]
UPLOAD_FOLDER = os.getcwd() + '/icons'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_old():
    return old_aotc, old_in, old_out


def set_old(old_aotc_here, old_in_here, old_out_here):
    old_aotc = old_aotc_here
    old_in = old_in_here
    old_out = old_out_here


@app.route('/home')
def hello():


    return render_template('display.html')


@app.route('/update_screen', methods=['GET'])
def hello_name():
    old_aotc, old_in, old_out = get_old()
    result = get_data('192.168.1.100',old_aotc,old_in, old_out )
    print(result)
    with open("data.json", "r") as f:
        response = json.load(f)
    if result["occupancy"] >= response["maximum_occupancy"]:

        response["occupancy_color"] = "darkred"
        response["status"] = "STOP"
    else:
        response["occupancy_color"] = "darkgreen"
        response["status"] = "GO"
    #
    # old_aotc = result["now_aotc"]
    # old_in = result["now_in"]
    # old_out = result["now_out"]
    set_old(result["now_aotc"],result["now_in"], result["now_out"])
    response["current_occupancy"] = result["occupancy"]
    response["in_count"] = result["in"]
    response["out_count"] = result["out"]
    return json.dumps(response)


@app.route('/get_icon/<icon>', methods=['GET'])
def get_icon(icon):
    return send_from_directory(UPLOAD_FOLDER, icon)


@app.route('/show_image', methods=['GET'])
def show_image():
    return render_template('img_show.html')


if __name__ == '__main__':

    print("here")

    app.run(host='0.0.0.0', port=5000, debug=True)