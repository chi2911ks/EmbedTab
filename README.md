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
![image](https://github.com/user-attachments/assets/c67634a5-62a2-418e-806d-d1f753dec990)