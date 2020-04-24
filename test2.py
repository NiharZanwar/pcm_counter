from selenium import webdriver


driver = webdriver.Firefox()

url = 'http://localhost:5000/home'
driver.get(url)
driver.fullscreen_window()