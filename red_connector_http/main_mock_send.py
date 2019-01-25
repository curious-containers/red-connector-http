from cc_connector_cli.connector_cli import run_connector
from red_connector_http.http import HttpMockSend
from red_connector_http.version import VERSION


def main():
    run_connector(HttpMockSend, version=VERSION)


if __name__ == '__main__':
    main()
