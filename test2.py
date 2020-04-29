from selenium import webdriver

fp = webdriver.FirefoxProfile()
# fp.set_preference('media.autoplay.default', "0")
fp.set_preference('media.autoplay.enabled', "True")


driver = webdriver.Firefox(fp)

url = 'http://localhost:5000/home'
driver.get(url)

driver.fullscreen_window()
# # import time
# #
# # from test import get_aotc, get_day_count, get_device_list
# # ip = '192.168.1.100'
# # time_now = time.time()
# # response = get_aotc(ip)
# # print(response)
# # date = {
# #         "day": response["datetime"].split(' ')[0].split('/')[1],
# #         "year": response["datetime"].split(' ')[0].split('/')[2],
# #         "month": response["datetime"].split(' ')[0].split('/')[0]
# #     }
# # response2 = get_day_count(ip, '5', date)
# # print(response2)
# #
# #
# # print(get_device_list())
# # print(time.time()-time_now)


# from gtts import gTTS
# import os
#
# mytext = 'Please stop. Maximum occupancy reached'
#
# # Language in which you want to convert
# language = 'en'
#
# # Passing the text and language to the engine,
# # here we have marked slow=False. Which tells
# # the module that the converted audio should
# # have a high speed
# myobj = gTTS(text=mytext, lang=language, slow=False)
#
# # Saving the converted audio in a mp3 file named
# # welcome
# myobj.save("STOP.mp3")
#
# # Playing the converted file
# os.system("ffplay STOP.mp3")