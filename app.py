from flask import Flask, render_template, send_from_directory, request
import time
import json
import os
from functions import get_aotc, get_device_list, get_day_count, get_config_data, set_config_data, check_password,\
    restart_app, logging, get_network_data, set_network_data, restart_network
from _thread import *
from datetime import datetime
import for_restart

global total_all_in, total_all_out

app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd() + '/icons'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def print_my_data():
    print(device_list)
    print("total_all_occ", total_all_occ)
    time.sleep(4)


def get_live_devices():
    global device_list
    total_devices = len(device_list)
    active_devices = []
    inactive_devices = []
    for device in device_list:
        if device["live_status"] == 1:
            active_devices.append(device["ip"])
        else:
            inactive_devices.append((device["ip"]))

    response = {
        "total_devices": total_devices,
        "active_number": len(active_devices),
        "active_devices": active_devices,
        "inactive_number": len(inactive_devices),
        "inactive_devices": inactive_devices
    }

    return response


def get_final_realtime_counts():
    global total_all_occ
    global device_list
    global total_all_in, total_all_out
    total_all_in = 0
    total_all_out = 0
    total_all_occ = 0

    for i in range(0, len(device_list)):
        if device_list[i]["active"]:
            if device_list[i]["today_latest_in"] != device_list[i]["today_latest_in_old"]:
                device_list[i]["aotc_in_old"] = device_list[i]["now_aotc_in"]
                device_list[i]["today_latest_in_old"] = device_list[i]["today_latest_in"]
                device_list[i]["final_in"] = device_list[i]["today_latest_in"]
                print("five min  crossed")
            else:
                device_list[i]["final_in"] = device_list[i]["today_latest_in"] + (
                            device_list[i]["now_aotc_in"] - device_list[i]["aotc_in_old"])

            if device_list[i]["today_latest_out"] != device_list[i]["today_latest_out_old"]:
                device_list[i]["aotc_out_old"] = device_list[i]["now_aotc_out"]
                device_list[i]["today_latest_out_old"] = device_list[i]["today_latest_out"]
                device_list[i]["final_out"] = device_list[i]["today_latest_out"]
                print("five min  crossed")
            else:
                device_list[i]["final_out"] = device_list[i]["today_latest_out"] + (
                            device_list[i]["now_aotc_out"] - device_list[i]["aotc_out_old"])
            device_list[i]["final_occ"] = device_list[i]["final_in"] - device_list[i]["final_out"]
            # print("Poll data", device_list)

            total_all_in = total_all_in + device_list[i]["final_in"]
            total_all_out = total_all_out + device_list[i]["final_out"]
            total_all_occ = total_all_occ + device_list[i]["final_occ"]

    # print("Poll data , Final Occ = ", total_all_occ, "total_all_in = " , total_all_in,  "total_all_out = " ,
    # total_all_out )


def maintain_device_list():
    global device_list

    for device in device_list:

        result = get_aotc(device["ip"])
        if result["success"] == 0:
            device["active"] = False
            device["live_status"] = 0
            continue

    while 1:
        for device in device_list:
            if device["active"]:

                response = get_aotc(device["ip"])
                if response["success"] == 0:
                    device["live_status"] = 0
                    time.sleep(2)
                    continue
                device["live_status"] = 1
                device["now_aotc"] = response["occupancy"]
                device["now_aotc_in"] = response["in"]
                device["now_aotc_out"] = response["out"]
                try:
                    date = {
                        "day": response["datetime"].split(' ')[0].split('/')[1],
                        "year": response["datetime"].split(' ')[0].split('/')[2],
                        "month": response["datetime"].split(' ')[0].split('/')[0]
                    }
                except:
                    logging("Error while parsing datetime" + response["datetime"])
                    date = {
                        "day": datetime.now().strftime("%d"),
                        "year": datetime.now().strftime("%m"),
                        "month": datetime.now().strftime("%Y")
                    }

                response2 = get_day_count(device["ip"], '5', date)

                device["today_latest"] = response2["occupancy"]
                device["today_latest_in"] = response2["in"]
                device["today_latest_out"] = response2["out"]

        get_final_realtime_counts()
        time.sleep(2)


@app.route('/home')
def hello():
    return render_template('display.html')


@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html')


@app.route('/settings_values', methods=['GET', 'POST'])
def get_settings_values():
    if request.method == 'GET':
        config = get_config_data()
        if config == 0:
            response = {
                "offset": 0,
                "success": 0,
                "maximum-occupancy": 0
            }
            return json.dumps(response)
        else:
            response = {
                "offset": config["relative_offset"],
                "success": 1,
                "maximum-occupancy": config["maximum_occupancy"],
                "audio-stop": config["audio-stop"],
                "audio-go": config["audio-go"]
            }
            return json.dumps(response)
    elif request.method == 'POST':

        config = get_config_data()
        json_response = json.loads(request.get_data(as_text=True))
        config["relative_offset"] = int(json_response["offset"])
        config["maximum_occupancy"] = int(json_response["maximum_occupancy"])
        config["audio-stop"] = int(json_response["audio-stop"])
        config["audio-go"] = int(json_response["audio-go"])

        if set_config_data(json.dumps(config)) == 0:
            return json.dumps({"success": 0})
        else:
            return json.dumps({"success": 1})


@app.route('/update_screen', methods=['GET'])
def hello_name():
    global total_all_occ, total_all_out, total_all_in

    total_result = {
        "success": 0,
        "in": total_all_in,
        "out": total_all_out,
        "occupancy": 0,
        "datetime": '',
        "status": "",
        "occupancy_color": "",
        "maximum_occupancy": 0,
        "config_error": False,
        "audio-stop": 1,
        "audio-go": 1,
        "live_status": get_live_devices()
    }

    config = get_config_data()
    if config == 0:
        total_result["config_error"] = True

    total_result["occupancy"] = total_all_occ - config["relative_offset"]
    total_result["maximum_occupancy"] = config["maximum_occupancy"]

    if total_result["occupancy"] >= config["maximum_occupancy"]:
        total_result["status"] = "STOP"
        total_result["occupancy_color"] = "darkred"
    else:
        total_result["status"] = "GO"
        total_result["occupancy_color"] = "darkgreen"
    total_result["audio-stop"] = config["audio-stop"]
    total_result["audio-go"] = config["audio-go"]
    total_result["success"] = 1

    return json.dumps(total_result)


@app.route('/get_icon/<icon>', methods=['GET'])
def get_icon(icon):
    return send_from_directory(UPLOAD_FOLDER, icon)


@app.route('/show_image', methods=['GET'])
def show_image():
    global device_list
    return str(device_list)


@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    return render_template('config.html')


@app.route('/config_values', methods=['POST', 'GET'])
def config_values():
    if request.method == 'GET':
        config = get_config_data()
        if config == 0:
            return json.dumps({"success": 0})
        else:
            config["success"] = 1
            return json.dumps(config)

    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)

        # print(data)
        response = {
            "success": 1,
            "message": ""
        }
        if check_password(json_data["password"]) == 0:
            response["success"] = 0
            response["message"] = 'Password is wrong'
            return json.dumps(response)

        config = get_config_data()

        config["name"] = json_data["device_name"]
        config["number_of_devices"] = int(json_data["number_of_devices"])
        config["device_ip"] = json_data["ip_string"]

        set_config_data(json.dumps(config))

        return json.dumps(response)

@app.route('/upload_images', methods=['GET', 'POST'])
def upload_images():
    if request.method == 'GET':

        return render_template('upload_images.html')
    if request.method == 'POST':

        allowed = ['jpg', 'png']
        if 'ad' in request.files:
            file = request.files['ad']
            try:
                if file.filename.split('.')[1].lower() not in allowed:
                    return render_template('upload_images.html', data='please upload file with extension ".jpg",".png"')
            except IndexError:
                return render_template('upload_images.html', data='please upload 1 file atleast')

            file.filename = 'ad.' + file.filename.split('.')[1].lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return render_template('upload_images.html')

        if 'logo' in request.files:

            file = request.files['logo']
            try:
                if file.filename.split('.')[1].lower() not in allowed:
                    return render_template('upload_images.html', data='please upload file with extension ".jpg",".png"')
            except IndexError:
                return render_template('upload_images.html', data='please upload 1 file atleast')

            file.filename = 'logo.' + file.filename.split('.')[1].lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return render_template('upload_images.html')


@app.route('/restart_app', methods=['GET'])
def restart():
    restart_app()
    return 'success'


@app.route('/live_status', methods=['GET'])
def live_status():
    response = get_live_devices()
    return json.dumps(response)


@app.route('/network_settings', methods=['GET'])
def network_settings():
    return render_template('network_settings.html')


@app.route('/network_values',methods=['POST','GET'])
def network_values():
    if request.method == 'GET':
        config = get_network_data()
        if config == 0:
            return json.dumps({"success": 0})
        else:
            config["success"] = 1
            return json.dumps(config)

    if request.method == 'POST':
        data = request.get_data(as_text=True)
        json_data = json.loads(data)

        # print(data)
        response = {
            "success": 1,
            "message": ""
        }
        if check_password(json_data["password"]) == 0:
            response["success"] = 0
            response["message"] = 'Password is wrong'
            return json.dumps(response)

        config = get_network_data()

        config["device_ip"] = json_data["device_ip"]
        config["default_gateway"] = json_data["default_gateway"]
        config["dns_server"] = json_data["dns_server"]
        config["dns_server2"] = json_data["dns_server2"]

        set_network_data(json.dumps(config))
        restart_network()

        return json.dumps(response)




if __name__ == '__main__':

    global device_list
    global total_all_occ
    total_all_occ = 0
    global total_all_in, total_all_out
    total_all_in = 0
    total_all_out = 0
    while 1:
        device_list = get_device_list()
        if device_list == 0:
            time.sleep(10)
        else:
            config_done = True
            break

    start_new_thread(print_my_data, ())
    start_new_thread(maintain_device_list, ())

    app.run(host='0.0.0.0', port=5000, debug=True)

# todo refine css and html
# todo create themes
# todo add provision to add advertisement picture


