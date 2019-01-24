from cc_connector_cli.connector_cli import run_connector
from red_connector_http.http import Http, HttpJson, HttpMockSend


def http_main():
    run_connector(Http)


def http_json_main():
    run_connector(HttpJson)


def http_mock_send_main():
    run_connector(HttpMockSend)
