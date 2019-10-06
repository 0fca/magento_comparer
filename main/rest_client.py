import requests


class RestClient:
    def send_get(self, url, headers, content):
        r = requests.get(url, headers=headers, data=content)
        return r.json(), r.status_code

    def send_post(self, url, headers, content):
        r = requests.post(url, headers=headers, data=content)
        return r.json(), r.status_code

    def send_delete(self, url, headers, content):
        r = requests.delete(url, headers=headers, data=content)
        return r.json(), r.status_code

    def send_put(self, url, headers, content):
        r = requests.put(url, headers=headers, data=content)
        return r.json(), r.status_code

    def send_get_binary(self, url, headers, content):
        r = requests.get(url, headers=headers, data=content)
        return r.content, r.status_code
