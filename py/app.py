import http.server
import time
from prometheus_client import start_http_server, Counter, Summary, Histogram

APP_PORT = 8175
METRICS_PORT = 8176

METRIC_REQUEST_COUNT = Counter(
    "python_app_request_count",
    "Total number of HTTP requests served.",
    ["app_name", "endpoint"])

METRIC_REQUEST_DURATION = Summary(
    "python_app_request_duration",
    "Application time in millseconds to serve a single request.",
    ["app_name", "endpoint"])

HIST_BUCKETS = [0.5, 1, 5, 10, 50, 100, 500]

METRIC_REQUEST_DURATION_HIST = Histogram(
    "python_app_request_duration_hist",
    "Application time in millseconds to serve a single request.",
    ["app_name", "endpoint"],
    buckets=HIST_BUCKETS)


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        METRIC_REQUEST_COUNT.labels("prom-python-app", self.path).inc()
        start_time = time.perf_counter()

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("Hi :-).", "utf-8"))
        self.wfile.close()

        duration = (time.perf_counter() - start_time) * 1000

        METRIC_REQUEST_DURATION.labels(
            "prom-python-app", self.path).observe(duration)

        METRIC_REQUEST_DURATION_HIST.labels(
            "prom-python-app", self.path).observe(duration)


if __name__ == "__main__":
    start_http_server(METRICS_PORT)
    server = http.server.HTTPServer(("localhost", APP_PORT), RequestHandler)
    server.serve_forever()
