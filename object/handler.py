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


import bpy
import math
import bmesh
from liblo import Bundle, Message
from bpy.app.handlers import persistent
from ..common.libloclient import Client
from . import ops

@persistent
def object_update_handler(scene):
    # check objects updates
    for ob in scene.objects:
        if ob.is_updated:
            bundle = Bundle()
            bundle.add(Message("/bge/scene/objects/position", ob.name, ob.location[0], ob.location[1], ob.location[2]))
            bundle.add(Message("/bge/scene/objects/orientation", ob.name, ob.rotation_euler[0], ob.rotation_euler[1], ob.rotation_euler[2]))

            if ob.type in {'MESH','FONT'}:
                bundle.add(Message("/bge/scene/objects/scaling", ob.name, ob.scale[0], ob.scale[1], ob.scale[2]))

            Client().send(bundle)

        if ob.is_updated_data:
            if ob.type == 'CAMERA':
                ops.BLive_OT_osc_camera_projectionmatrix.update_projectionmatrix(ob)

            elif ob.type == 'LAMP':
                ops.BLive_OT_osc_object_lamp.update_lamp(ob)

            elif ob.type == 'MESH' and ob.mode == 'EDIT':
                ops.BLive_OT_osc_object_meshdata.update_mesh(ob)

        # workaround for object color
        for i in ob.material_slots:
            if ob.type in {'MESH','FONT'} and len(bpy.data.materials) and bpy.data.materials[i.name].use_object_color:
                Client().send(Message("/bge/scene/objects/color", ob.name, ob.color[0], ob.color[1], ob.color[2], ob.color[3]))


def register():
    print("object.handler.register")
    Client().add_apphandler('scene_update_post', object_update_handler)

def unregister():
    print("object.handler.unregister")
