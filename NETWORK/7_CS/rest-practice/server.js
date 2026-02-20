const http = require("http");

let data = ["apple", "banana"];

const server = http.createServer((req, res) => {
  res.setHeader("content-Type", "application/json; charset=utf-8");

  if (req.method == "GET") {
    res.statusCode = 200;
    res.end(JSON.stringify({ data }));
    return;
  }

  res.statusCode = 405;
  res.end(JSON.stringify({ error: "Method Not Allowed", allowed: ["GET"] }));
});

server.listen(3000, "127.0.0.1", () => {
  console.log("server running on http:local");
});
