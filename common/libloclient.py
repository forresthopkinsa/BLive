# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


# Script copyright (C) 2012 Thomas Achtner (offtools)

#TODO:
#   stop Client Thread not from inside, stop it on, load blendfile, ...
#   remove sleep statement by better solution

import bpy
import liblo
import threading
import time
from liblo import make_method

class LibloClient(liblo.ServerThread):
    def __init__(self):
        super().__init__()
        self.appHandler = dict()
        self.__await_connect = False
        self.__thread_started = False

    class ConnectRequest(threading.Thread):
        def __init__(self, client):
            threading.Thread.__init__(self)
            self.client = client

        def run(self):
            while self.client.is_connecting() == True:
                liblo.send(self.client.target, "/bge/connect")
                time.sleep(1)

    @make_method('/bge/srvinfo', 'sii')
    def cb_srvinfo(self, path, args, types, source, user_data):
        print ("CLIENT: connected - got server reply: ", args[0])
        self.__await_connect = False
        del self.__conreq

        # save bge Window size
        settings = bpy.context.window_manager.blive_settings
        settings.bge_window_width = args[1]
        settings.bge_window_height = args[2]

        self._start_apphandler()

        # Update Viewports
        bpy.ops.blive.osc_update_viewports()

        #send init data, like projection matrix after connect for every viewport
        for ob in bpy.context.scene.objects:
            if ob.type == 'CAMERA' and ob.data.viewport.active:
                bpy.ops.blive.osc_camera_projectionmatrix().camera = ob.name

    @make_method('/bge/error', 'is')
    def cb_error(self, path, args, types, source, user_data):
        if args[0] == 0:
            print ("CLIENT: received unknown message: ", args)
        elif args[0] == 1:
            print ("CLIENT: out of sync: ", args)
            # TOOD: caution may crash the gameengine
            #bpy.ops.wm.save_as_mainfile(filepath=bpy.context.blend_data.filepath)
            #bpy.ops.blive.gameengine_reload()

    @make_method('/bge/logic/endGame', 's')
    def cb_shutdown(self, path, args, types, source, user_data):
        print ("CLIENT: received shutdown - closing client", args)
        #self.close() #TODO: dont close thread from inside thread, just notify blender

    @make_method(None, None)
    def cb_fallback(self, path, args, types, source, user_data):
        print ("CLIENT: received unhandled message: ", path, args, types, source.url, user_data)

    def add_apphandler(self, apphandler, func):
        '''register an apphandler, will be activated on connect'''
        if not apphandler in self.appHandler:
            self.appHandler[apphandler] = set()
        self.appHandler[apphandler].add(func)

    def _start_apphandler(self):
        '''activate registered apphandler'''
        for handler in self.appHandler.keys():
            for func in self.appHandler[handler]:
                getattr(bpy.app.handlers, handler).append(func)

    def _stop_apphandler(self):
        '''deactivate apphandler'''
        for handler in self.appHandler.keys():
            try:
                for func in self.appHandler[handler]:
                    getattr(bpy.app.handlers, handler).remove(func)
            except ValueError:
                print("AppHandler %s already removed" %func)

    def is_connecting(self):
        return self.__await_connect

    def connect(self, host, port, proto=liblo.UDP):
        '''connect to a osc server'''
        print("CLIENT: connecting")

        try:
            self.target = liblo.Address(host, port, proto)
            self.start()
            self.__await_connect = True
            self.__conreq = LibloClient.ConnectRequest(self)
            self.__conreq.start()
        except liblo.AddressError as err:
            print("TODO Error Handling", err)
            return

    def send(self, path, *args):
        try:
            super().send(self.target, path, *args)
        except AttributeError:
            print("Not connected - no messages send")

    def receive(self):
        while self.recv(0):
            pass

    def disconnect(self):
        try:
            liblo.send(self.target, "/bge/disconnect")
            self.close()
        except AttributeError:
            pass

    def shutdown(self):
        try:
            liblo.send(self.target, "/bge/shutdown")
        except AttributeError:
            pass

    def start(self):
        self.stop()
        super().start()
        self.__thread_started = True
        print("CLIENT: libloclient thread started")

    def stop(self):
        if self.__thread_started:
            super().stop()
            self.__thread_started = False
            print("CLIENT: libloclient thread stopped")

    def close(self):
        self._stop_apphandler()
        self.stop()
        try:
            del self.target
        except AttributeError:
            print("Not connected")

__client = LibloClient()

Client = lambda : __client

def register():
    print("client.register")
    pass

def unregister():
    print("client.unregister")
    pass
