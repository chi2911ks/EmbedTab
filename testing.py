from utils.find_handle import find_handle


index = 0
for i in find_handle(""):
    import requests
    if "ẩn" in i:
        requests.get("http://127.0.0.1:5000/embed?handle="+i.split(":")[0])
        index += 1