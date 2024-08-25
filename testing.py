from EmbedAPI.embed import EmbedAPI
from utils.find_handle import find_handle
embed = EmbedAPI()
for index, data in enumerate(find_handle("LDPlayer")):
    title, handle = data.split(":")
    if "LDPlayer" in title:
       embed.embed_tab(handle, new=True)