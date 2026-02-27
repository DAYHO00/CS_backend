from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse

# in-memory DB
STORE = {}
SEQ = 1

def send_json(handler, status, obj=None, headers=None):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    if headers:
        for k, v in headers.items():
            handler.send_header(k, v)
    handler.end_headers()
    if obj is not None:
        handler.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

def parse_body_json(handler):
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return None
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 조용히(로그 최소화)
        return

    def do_GET(self):
        path = urlparse(self.path).path

        # GET /todos (전체 조회)
        if path == "/todos":
            items = []
            for tid, content in STORE.items():
                items.append({
                    "id": tid,
                    "content": content,
                    "_links": {
                        "self": {"href": f"/todos/{tid}"},
                        "delete": {"href": f"/todos/{tid}", "method": "DELETE"}
                    }
                })
            return send_json(self, 200, {"items": items, "_links": {"self": {"href": "/todos"}}})

        # GET /todos/{id} (단건 조회)
        if path.startswith("/todos/"):
            try:
                tid = int(path.split("/")[2])
            except:
                return send_json(self, 400, {"message": "Invalid id"})

            if tid not in STORE:
                return send_json(self, 404, {"message": "Not Found"})

            return send_json(self, 200, {
                "id": tid,
                "content": STORE[tid],
                "_links": {
                    "self": {"href": f"/todos/{tid}"},
                    "collection": {"href": "/todos"},
                    "delete": {"href": f"/todos/{tid}", "method": "DELETE"}
                }
            })

        return send_json(self, 404, {"message": "Not Found"})

    def do_POST(self):
        global SEQ
        path = urlparse(self.path).path

        # POST /todos (생성)
        if path == "/todos":
            body = parse_body_json(self)
            if not body or "content" not in body:
                return send_json(self, 400, {"message": "Body must include 'content'."})

            tid = SEQ
            SEQ += 1
            STORE[tid] = body["content"]

            # REST스럽게: 201 + Location 헤더(새 리소스 URI)
            return send_json(
                self,
                201,
                {
                    "id": tid,
                    "content": STORE[tid],
                    "_links": {
                        "self": {"href": f"/todos/{tid}"},
                        "collection": {"href": "/todos"}
                    }
                },
                headers={"Location": f"/todos/{tid}"}
            )

        return send_json(self, 404, {"message": "Not Found"})

    def do_DELETE(self):
        path = urlparse(self.path).path

        # DELETE /todos/{id} (삭제)
        if path.startswith("/todos/"):
            try:
                tid = int(path.split("/")[2])
            except:
                return send_json(self, 400, {"message": "Invalid id"})

            if tid not in STORE:
                return send_json(self, 404, {"message": "Not Found"})

            del STORE[tid]
            # 204 No Content: 성공했지만 응답 바디 없음
            self.send_response(204)
            self.end_headers()
            return

        return send_json(self, 404, {"message": "Not Found"})

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    print("REST Todo server running at http://127.0.0.1:8000")
    print("Try: GET /todos, POST /todos, GET /todos/{id}, DELETE /todos/{id}")
    server.serve_forever()