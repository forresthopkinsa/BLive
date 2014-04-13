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

# TODO: use only playlist, current title is automatic appended to playlist

import bpy

class BLive_PT_texture_player(bpy.types.Panel):
    bl_label = "BLive Videoplayer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(self, context):
        try:
            return bool(context.active_object.active_material.active_texture.image)
        except AttributeError:
            return False

    def draw_source_type(self, context, player):
        layout = self.layout
        layout.row().label("Choose Source Type")
        row = layout.row(align=True)
        row.prop(player, "sourcetype", expand=True)

    def draw_controls(self, player):
        layout = self.layout
        row = layout.row()

        box = row.box()
        box.label('Controls')
        row = box.row(align=True)
        row.scale_x = 2
        row.scale_y = 2
        row.alignment = 'CENTER'

        row.operator("blive.videotexture_playlist_prev_entry", text="", icon="REW")
        row.operator("blive.videotexture_pause", text="", icon="PAUSE")
        row.operator("blive.videotexture_play", text="", icon="PLAY")

        row.operator("blive.videotexture_stop", text="", icon="MESH_PLANE")
        row.operator("blive.videotexture_playlist_next_entry", text="", icon="FF")
        row.operator("blive.videotexture_close", text="", icon="PANEL_CLOSE")

        row = box.row()
        row.prop(player, "volume", slider=True)
        row = box.row()
        ob = bpy.context.active_object
        row.prop(ob, "color", text='Alpha', slider=True, index=3)
        row = box.row()
        row.prop(player, "loop", toggle=True)

    def draw_playlist(self, player):
        layout = self.layout
        row = layout.row()
        row.template_list("UI_UL_list", "playlist", player, "playlist", player, "active_playlist_entry", rows=4, maxrows=8)

        col = row.column(align=True)
        col.operator('blive.videotexture_playlist_add_entry', icon='ZOOMIN', text='')
        col.operator('blive.videotexture_playlist_delete_entry', icon='ZOOMOUT', text='')

    def draw_playlist_entry(self, player):
        entry = player.playlist[player.active_playlist_entry]
        box = self.layout.box()
        box.label('Current Playlist Entry')
        if entry.sourcetype == 'Movie':
            row = box.row(align=True)
            row.prop(entry, "inpoint", text="in")
            row.prop(entry, "outpoint", text="out")
            row = box.row(align=True)
            row.prop(entry, "preseek", text="preseek")
            row = box.row(align=True)
            row.prop(entry, "audio", text="sound")
            row.prop(entry, "loop", text="loop")

        elif entry.sourcetype == 'Camera':
            row = box.row()
            row.prop(entry, "filepath", text="Device")
            row = box.row()
            row.prop(entry, "deinterlace", text="deinterlace")
        elif entry.sourcetype == 'Stream':
            row = box.row()
            row.prop(entry, "filepath", text="URL")
            row = box.row()
            row.prop(entry, "audio", text="sound")
            row.prop(entry, "deinterlace", text="deinterlace")

        # TODO: handle follow actions (needs notification from bge)
        #row = self.layout.row(align=True)
        #row.prop(entry, "follow", text="follow action")

    def draw(self, context):
        ob = context.active_object
        image = ob.active_material.active_texture.image
        player = image.player
        layout = self.layout

        self.draw_source_type(context, player)

        if player.sourcetype == 'Movie':
            if 'FILE_BROWSER' in [i.type for i in context.screen.areas]:
                narea = [i.type for i in context.screen.areas].index('FILE_BROWSER')
                nspace = [i.type for i in context.screen.areas[narea].spaces].index('FILE_BROWSER')
                space = context.screen.areas[narea].spaces[nspace]
                row = layout.row(align=True)
                col = row.column(align=True)
                col.enabled = False
                col.prop(space.params, "filename", text="", expand=True)
            else:
                row = layout.row()
                row.label("add one filebrowser to your workspace")

        self.draw_playlist(player)

        if player.active_playlist_entry < len(player.playlist):
            self.draw_playlist_entry(player)

        self.draw_controls(player)

#def enumerate_images():
    #image_list = list()
    #for index,image in enumerate(bpy.data.images):
        #image_list.append((str(index), image.name, image.name))
    #bpy.context.object['images'] = bpy.props.EnumProperty(items=image_list, default=0)

#class BLive_PT_texture_player(bpy.types.Panel):
    #bl_label = "BLive Videoplayer"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    #bl_context = "texture"

    #@classmethod
    #def poll(self, context):
        #try:
            #return bool(context.active_object.active_material.active_texture.image)
        #except AttributeError:
            #return False

    #def draw_control(self, context):
        #layout = self.layout
        #layout.row().label("Controls")
        #row = layout.row(align=True)
        #row.scale_x = 2
        #row.scale_y = 2
        #row.alignment = 'CENTER'
        #row.operator("blive.videotexture_play", text="", icon="PLAY")
        #row.operator("blive.videotexture_pause", text="", icon="PAUSE")
        #row.operator("blive.videotexture_stop", text="", icon="MESH_PLANE")
        #row.operator("blive.videotexture_close", text="", icon="PANEL_CLOSE")

    #def draw_source_properties(self, context):
        #ob = context.active_object
        #image = ob.active_material.active_texture.image
        #player = image.player
        #layout = self.layout

        #source = player.source
        ##if player.mode == "playlist" and len(player.playlist):
            ##source = player.playlist[player.playlist_entry]

        #if source.sourcetype == "Movie":
            #row = self.layout.row(align=True)
            #row.prop(source, "inpoint", text="in")
            #row.prop(source, "outpoint", text="out")
            #row = self.layout.row(align=True)
            #row.prop(source, "preseek", text="preseek")
            #row = self.layout.row(align=True)
            #row.prop(source, "audio", text="sound")
            #row.prop(source, "loop", text="loop")

        #if source.sourcetype == "Camera":
            #row = self.layout.row(align=True)
            #row.prop(source, "width", text="width")
            #row.prop(source, "height", text="height")
            #row = self.layout.row(align=True)
            #row.prop(source, "deinterlace", text="deinterlace")
            #row.prop(source, "rate", text="framerate")

        #if source.sourcetype == "Stream":
            #row = self.layout.row(align=True)
            #row.prop(source, "audio", text="sound")
            #row.prop(source, "loop", text="loop")

    #def draw_playlist(self, context, player):
        #layout = self.layout
        #row = layout.row(align=True)
        #row.label("Playlist:")

        #try:
            ## get source from playlist collection
            #source = player.playlist[player.playlist_entry]

            ## draw playlist
            #row = layout.row()
            #row.template_list("UI_UL_list", "playlist_entry", player, "playlist", player, "playlist_entry", rows=2, maxrows=8)
        #except IndexError:
            #pass

    #def draw_source_type(self, context, player):
        #layout = self.layout
        #layout.row().label("Choose Source Type")
        #row = layout.row(align=True)
        #row.prop(player.source, "sourcetype", expand=True)

    #def draw(self, context):
        #ob = context.active_object
        #image = ob.active_material.active_texture.image
        #player = image.player
        #layout = self.layout

        #layout.row().label("Switch between single media or playlist")

        #row = layout.row(align=True)
        #row.prop(player, "mode", expand=True)

        ## mode Playlist
        #if player.mode == "playlist":
            #self.draw_playlist(context, player)

        ## draw source type switch
        #self.draw_source_type(context, player)

        #source = player.source

        #row = layout.row(align=True)
        #row.prop(source, "filepath", text="")
        #row.operator("blive.videotexture_filebrowser", text="", icon="FILESEL")

        #if player.mode == "playlist":
            #row.operator("blive.videotexture_playlist_add", icon="ZOOMIN", text="")
            #row.operator("blive.videotexture_playlist_remove", icon="ZOOMOUT", text="")

        ## draw controls
        #self.draw_control(context)

        ## source properties
        #self.draw_source_properties(context)

def register():
    print("texture.ui.register")
    bpy.utils.register_class(BLive_PT_texture_player)

def unregister():
    print("texture.ui.unregister")
    bpy.utils.unregister_class(BLive_PT_texture_player)
