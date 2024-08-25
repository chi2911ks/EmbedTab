from time import sleep
from undetected_chromedriver import Chrome
from utils.find_handle import find_handle, get_pid_from_handle
from EmbedAPI.embed import EmbedAPI
embed = EmbedAPI()
def get_handle_from_pid(browser_pid):
    handles = find_handle()
    for data in handles:
        title, handle = data.split(":")
        pid = get_pid_from_handle(int(handle))
        if pid == browser_pid:
            return handle
    return 0
driver = Chrome()
handle = get_handle_from_pid(driver.browser_pid)
embed.embed_tab(handle, new=True)
driver.get("https://www.youtube.com/@cbtool")
sleep(100)
driver.quit()