from cc_connector_cli.connector_cli import run_connector
from red_connector_http.http import Http, HttpJson, HttpMockSend
from red_connector_http.version import VERSION


def http_main():
    run_connector(Http, version=VERSION)


def http_json_main():
    run_connector(HttpJson, version=VERSION)


def http_mock_send_main():
    run_connector(HttpMockSend, version=VERSION)
