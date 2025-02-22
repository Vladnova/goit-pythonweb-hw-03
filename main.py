import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from typing import Dict
import os
from datetime import datetime
from jinja2 import Template


FILE_PATH = os.path.join("storage", "data.json")


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        pr_url = urllib.parse.urlparse(self.path)
        # print("ewew", pr_url)

        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.show_messages()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self) -> None:
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        self.save_storage_data(data_dict)

        print(f"Дані збережено у {FILE_PATH}")

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        with open(filename, "rb") as fb:
            self.wfile.write(fb.read())

    def send_static(self) -> None:
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def save_storage_data(self, data: Dict[str, str]) -> None:
        date_create_message = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")

        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)
                    if not isinstance(existing_data, dict):
                        existing_data = {}
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # Додаємо новий запис
        existing_data[date_create_message] = data

        # Записуємо оновлений словник назад у файл
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)

    def show_messages(self) -> None:

        try:
            with open(FILE_PATH, "r") as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = {}

        with open("read.html", "r") as f:
            template = Template(f.read())

        rendered_html = template.render(messages=messages)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(rendered_html.encode("utf-8"))


def run(server_class=HTTPServer, handler_class=HttpHandler):
    print("start")
    server_address = ("0.0.0.0", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
