import requests
import xml.etree.ElementTree as ET

# x = requests.get('http://192.168.1.100/cgi-bin/GetCounts.cgi?getReports&2020&04&23&60')
# # http://<IP>/cgi-bin/GetCounts.cgi?getCounts
#
# print(x.text)
#
# open("data.xml", "w+").write(x.text)
# root = ET.fromstring(x.text)
# # print(root[0][2].attrib)
# # my_dict=xmltodict.parse(x.text)
# # print(my_dict)
# # print(root[1].attrib["In"])
#
# for child in root[0]:
#     print(type(child.attrib["In"]))


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
        # print(response.text)
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


# print(get_aotc('192.168.1.100'))


def get_day_count(ip, interval, day):

    url = "http://{}/cgi-bin/GetCounts.cgi?getReports&{}&{}&{}&{}".format(ip, day["year"], day["month"], day["day"],
                                                                          interval)
    # print(url)
    data = {
        "success": 0,
        "in": 0,
        "out": 0,
        "occupancy": 0,
        "datetime": ''
    }

    try:
        # print("here")
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





def get_data(ip, old_aotc, old_in, old_out):

    data = {
        "success": 0,
        "in": 0,
        "out": 0,
        "occupancy": 0,
        "datetime": '',
        "now_aotc": 0, "now_in": 0, "now_out": 0
    }

    response = get_aotc(ip)
    if response["success"] == 0:
        return data
    # 04 / 24 / 2020
    now_aotc = response["occupancy"]
    now_in = response["in"]
    now_out = response["out"]

    date = {
        "day": response["datetime"].split(' ')[0].split('/')[1],
        "year": response["datetime"].split(' ')[0].split('/')[2],
        "month": response["datetime"].split(' ')[0].split('/')[0]
    }

    response2 = get_day_count(ip, '5', date)

    print(response)
    print(response2)

    present_occupancy = response2["occupancy"] + now_aotc - old_aotc
    present_in = response2["in"] + now_in - old_in
    present_out = response2["out"] + now_out - old_out

    data["occupancy"] = present_occupancy
    data["in"] = present_in
    data["out"] = present_out
    data["now_aotc"] = now_aotc
    data["now_in"] = now_in
    data["now_out"] = now_out

    return data


#
# date = {"day": "23", "year": "2020", "month": "04"}
# result = get_day_count('192.168.1.100', '5', date)

# get_data('192.168.1.100', 0, 0, 0)

# print(result)
# while