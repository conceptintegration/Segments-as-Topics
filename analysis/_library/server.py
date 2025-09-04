#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner, Matt Martin'
__copyright__   = 'Copyright 2025, Roy Gardner, Sally Gardner, Matt Martin'

from packages import *

def server_is_running(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0
    
class CheckboxState:
    def __init__(self):
        self.selected_ids = set()

class CheckboxHandler(BaseHTTPRequestHandler):
    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        # Make sure we don't see log messages in the notebook
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        # The checked state is always true whether or not the checkbox is checked or unchecked!
        selected_id = data['id']
        if selected_id in self.state.selected_ids:
            self.state.selected_ids.discard(selected_id)
        else:
            self.state.selected_ids.add(selected_id)
        self.end_headers()
