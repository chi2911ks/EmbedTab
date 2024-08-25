import requests


class EmbedAPI:
    def __init__(self, port: int=5000) -> None:
        self.domain = "http://127.0.0.1:%s"%port
    def embed_tab(self, handle, **kwargs):
        """params: index
        new=False or True"""
        params = {"handle": handle}
        params.update(kwargs)
        path = "/embed"
        url = self.domain+path
        response = requests.get(url, params=params)
        print(response.url)
        print(response.json())
