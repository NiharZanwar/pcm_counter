import requests
import xml.etree.ElementTree as ET
import json


def get_aotc(ip):
    url = "http://{}/cgi-bin/GetCounts.cgi?getCounts".format(ip)

    data = {
        "success": 0,
        "in": 0,
        "out": 0,
        "occupancy": 0,
        "datetime": ''
    }

    try:
        response = requests.get(url)
        if response.status_code != 200:
            data["success"] = 0
            return data

        xml_root = ET.fromstring(response.text)
        data["in"] = int(xml_root[1].attrib["In"])
        data["out"] = int(xml_root[1].attrib["Out"])
        data["occupancy"] = data["in"] - data["out"]
        data["datetime"] = xml_root[0].text
        data["success"] = 1
        return data

    except Exception as e:
        print("Error - {}".format(e))
        data["success"] = 0
        return data


def get_day_count(ip, interval, day):
    url = "http://{}/cgi-bin/GetCounts.cgi?getReports&{}&{}&{}&{}".format(ip, day["year"], day["month"], day["day"],
                                                                          interval)
    data = {
        "success": 0,
        "in": 0,
        "out": 0,
        "occupancy": 0,
        "datetime": ''
    }

    try:
        response = requests.get(url)
        xml_root = ET.fromstring(response.text)

        for child in xml_root[0]:
            data["in"] += int(child.attrib["In"])
            data["out"] += int(child.attrib["Out"])

        data["occupancy"] = data["in"] - data["out"]
        data["success"] = 1
        return data
    except:
        data["success"] = 0
        return data


def get_device_list():
    device_list = []
    try:
        with open("config.json", "r+") as f:
            config = json.load(f)
            number_of_devices = config["number_of_devices"]

            for i in range(0, number_of_devices):
                device_status = {"ip": config["device_ip"][i],
                                 "final_occ": 0,"final_in": 0, "final_out": 0,
                                 "now_aotc": 0, "now_aotc_in": 0, "aotc_in_old": 0,
                                 "now_aotc_out": 0, "aotc_out_old": 0,
                                 "today_latest_in": 0, "today_latest_in_old": 0,
                                 "today_latest_out": 0, "today_latest_out_old": 0,
                                 "today_latest": 0, "active": True}

                device_list.append(device_status)
        f.close()
        return device_list
    except Exception as e:
        print("error while reading config.json - {}".format(e))
        f.close()
        return 0


def get_config_data():

    try:
        with open("config.json", "r+") as f:
            config = json.load(f)
            f.close()
            return config
    except Exception as e:
        print("error while reading config.json - {}".format(e))
        f.close()
        return 0


def set_config_data(data):

    try:
        with open("config.json", "w") as f:
            f.write(data)
            f.close()
            return 1
    except Exception as e:
        print("error while writing to config file - {}".format(e))
        return 0


def check_password(string):
    try:
        with open("password.txt", "r") as f:
            password = f.read()
            if string == password:
                f.close()
                return 1
            else:
                f.close()
                return 0
    except Exception as e:
        print("error while checking password - {}".format(e))
        return 0

