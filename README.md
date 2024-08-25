# Embed Tab
* Embed all tab (chrome, ldplayer)
## How to use api embed 
### Import module
``` python
from EmbedAPI.embed import EmbedAPI
from utils.find_handle import find_handle

```
### LDPlayer
+ Create new view
```python
embed = EmbedAPI()
for data in find_handle("LDPlayer"):
    title, handle = data.split(":")
    embed.embed_tab(handle, new=True)
```
or
```python
import win32gui
hwnd = win32gui.FindWindow(None, "LDPlayer")
embed = EmbedAPI()
embed.embed_tab(handle, new=True)
```
+ Add tab with index
```python
embed.embed_tab(handle, index=0)
```
### Chrome
+ Demo
![image](https://github.com/user-attachments/assets/2355db37-a358-4e1c-9457-225b92594347)
+ Code
```python
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
```
