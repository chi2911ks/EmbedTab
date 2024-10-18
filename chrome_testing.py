from time import sleep
import requests
# from undetected_chromedriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


from utils.find_handle import find_handle, get_pid_from_handle
from EmbedAPI.embed import EmbedAPI
embed = EmbedAPI()

def get_handle_from_pid(browser_pid):
    handles = find_handle()
    for data in handles:
        title, handle = data.split("|")

        pid = get_pid_from_handle(int(handle))
        if pid == browser_pid:
            return handle
    return 0


def open_browser():
    url = 'http://127.0.0.1:11253/api/v3/profiles/start/c309b176-f253-4e4d-8caa-a8f612676175'
    response = requests.get(url)
    remote_debugging_address = response.json()['data']['remote_debugging_address']
    pid = response.json()['data']['process_id']
    driver_path = response.json()['data']['driver_path']

    # start selenium with remote debugging address
    chrome_options = Options()

    chrome_options.debugger_address = remote_debugging_address
    myService = webdriver.chrome.service.Service(driver_path)

    driver = webdriver.Chrome(service=myService, options=chrome_options)

    handle = get_handle_from_pid(pid)
    print(handle)
    embed.embed_tab(handle, new=True)
    driver.get('https://www.google.com')
    input('Press Enter to quit')
    driver.quit()
    embed.unembed_tab(handle)



open_browser()

    

