#!/usr/bin/env python3
# coding: utf-8

import argparse
import os

from tornado import gen
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
import struct

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host_port", nargs='?', default="127.0.0.1:9999")
    host, port = parser.parse_args().host_port.split(":")
    
    lantern = argparse.Namespace(
        is_on = False,
        color = 0xffffff, # white
    )
    
    prefix_fmt = ">BH"
    prefix_sz = struct.calcsize(prefix_fmt)

    class LCommand:
        ON    = 0x12
        OFF   = 0x13
        COLOR = 0x20
    
    def read_bytes_or_close(stream, num_bytes, callback):
        assert num_bytes
        
        if stream.closed():
            callback(None)
        else:
            def handle_read_end(data):
                stream.set_close_callback(None)
                callback(data)
            stream.read_bytes(num_bytes, handle_read_end)
            
            def handle_close():
                callback(None)
            stream.set_close_callback(handle_close)
    
    class Server(TCPServer):
        @gen.engine
        def handle_stream(self, stream, address):
            print("Connection is opened")
            while True:
                #prefix = yield gen.Task(stream.read_bytes, prefix_sz)
                prefix = yield gen.Task(read_bytes_or_close, stream, prefix_sz)
                if prefix is None:
                    # 6. При завершении работы фонарь корректно закрывает соединение с сервером.
                    print("Connection is closed")
                    break
                cmd, length = struct.unpack(prefix_fmt, prefix)
                #length = 3
                data = (yield gen.Task(stream.read_bytes, length)) if length else b''
                
                if cmd == LCommand.ON:
                    lantern.is_on = True
                elif cmd == LCommand.OFF:
                    lantern.is_on = False
                elif cmd == LCommand.COLOR and length == 3:
                    r, g, b = struct.unpack(">BBB", data)
                    lantern.color = (r << 16) + (g << 8) + b
                    
                # отрисовка фонаря
                print(lantern)
        
    Server().listen(port, host)
    
    IOLoop.instance().start()
    