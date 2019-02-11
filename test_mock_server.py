# Standard library imports...
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
import io
# Third-party imports...
from nose.tools import assert_true
import requests
#import numpy as np
from bitmexwebsock import getBitmexWs


ws = getBitmexWs()
class MockServerRequestHandler(BaseHTTPRequestHandler):

    def createListFromTrades(self, listTrades):
        #arrayTrades = np.zeros(len(listTrades), 4)
        blist = []
        r=0
        for trade in listTrades:
            #arrayTrades[r, trade.]
            dic = {'price': trade['price'], 'amount':trade['size'],'date': trade['timestamp'], 'is_buy': int(trade['side'].lower()=='buy')}
            blist.append(dic)
            r = r+1
        return blist


    def do_GET(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        self.send_response(requests.codes.ok, "thanks for contacting us")
        self.end_headers()

        response = io.BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        body = ws.recent_trades()
        ltrades = self.createListFromTrades(body)

        response.write(str(ltrades))
        self.wfile.write(response.getvalue())

        return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    print('using port: '+str(port))
    return port


class TestMockServer(object):
    @classmethod
    def setup_class(cls):
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    def test_request_response(self):
        url = 'http://localhost:{port}/users'.format(port=self.mock_server_port)

        # Send a request to the mock API server and store the response.
        response = requests.get(url)

        # Confirm that the request-response cycle completed successfully.
        print(response.reason)
        assert_true(response.ok)



import time

if __name__ == "__main__":

    t=TestMockServer()
    t.setup_class()
    t.test_request_response()
    while True:
        time.sleep(1)