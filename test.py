import requests
import xml.etree.ElementTree as ET


x = requests.get('http://192.168.1.100/cgi-bin/GetCounts.cgi?getCounts')
# http://<IP>/cgi-bin/GetCounts.cgi?getCounts

print(x.text)


root = ET.fromstring(x.text)
print(root[0].text)
print(root[1].attrib["In"])


def get_aotc(ip, request):

