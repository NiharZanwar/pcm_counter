from functions import *
import time
from _thread import *


def print_my_data():
    while 1:
        print(get_occupancy_data()['occupancy'])
        time.sleep(1)


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
                # print("five min  crossed")
            else:
                device_list[i]["final_in"] = device_list[i]["today_latest_in"] + (
                        device_list[i]["now_aotc_in"] - device_list[i]["aotc_in_old"])

            if device_list[i]["today_latest_out"] != device_list[i]["today_latest_out_old"]:
                device_list[i]["aotc_out_old"] = device_list[i]["now_aotc_out"]
                device_list[i]["today_latest_out_old"] = device_list[i]["today_latest_out"]
                device_list[i]["final_out"] = device_list[i]["today_latest_out"]
                # print("five min  crossed")
            else:
                device_list[i]["final_out"] = device_list[i]["today_latest_out"] + (
                        device_list[i]["now_aotc_out"] - device_list[i]["aotc_out_old"])
            device_list[i]["final_occ"] = device_list[i]["final_in"] - device_list[i]["final_out"]
            # print("Poll data", device_list)

            total_all_in = total_all_in + device_list[i]["final_in"]
            total_all_out = total_all_out + device_list[i]["final_out"]
            total_all_occ = total_all_occ + device_list[i]["final_occ"]


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

def get_occupancy_data():
    global total_all_occ, total_all_out, total_all_in, live_max_offset
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
        "live_status": get_live_devices(),
        "banner-text": "",
        "relay-function": 0
    }
    config = get_config_data()
    if config == 0:
        total_result["config_error"] = True
    total_result["occupancy"] = total_all_occ - config["relative_offset"]
    total_result["maximum_occupancy"] = config["maximum_occupancy"] + live_max_offset
    if total_result["occupancy"] >= total_result["maximum_occupancy"]:
        total_result["status"] = "STOP"
        total_result["occupancy_color"] = "darkred"
    else:
        total_result["status"] = "GO"
        total_result["occupancy_color"] = "darkgreen"
    total_result["audio-stop"] = config["audio-stop"]
    total_result["audio-go"] = config["audio-go"]
    total_result["banner-text"] = config["banner-text"]
    total_result["relay-function"] = config["relay-function"]
    total_result["success"] = 1

    return total_result

def update_device_status():
    global device_list
    while True:
        for device in device_list:
            if not device["active"]:
                response = get_aotc(device["ip"], False)
                if response["success"] == 1:
                    device["active"] = True
        time.sleep(5)


if __name__ == '__main__':
    global device_list
    global total_all_occ
    total_all_occ = 0
    global total_all_in, total_all_out, live_max_offset
    total_all_in = 0
    total_all_out = 0
    live_max_offset = 0
    while 1:
        device_list = get_device_list()
        if device_list == 0:
            time.sleep(10)
        else:
            config_done = True
            print("config done")
            break

    # start_new_thread(print_my_data, ())
    start_new_thread(maintain_device_list, ())
    start_new_thread(update_device_status, ())

    while 1:
        print(get_occupancy_data())
        time.sleep(1)

