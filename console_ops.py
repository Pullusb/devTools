import bpy
from . import fn

class DEV_OT_console_insert_text(bpy.types.Operator):
    bl_idname = "devtools.console_insert_text"
    bl_label = "Insert Text In Console"
    bl_description = ""
    bl_options = {"REGISTER"}

    text : bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.console.insert(text=self.text)
        return {'FINISHED'}

def get_viewport_area_text(context):
    screen = bpy.context.window.screen
    for i, area in enumerate(screen.areas):
        if area.type == 'VIEW_3D':
            return f'C.window.screen.areas[{i}]'

class DEV_OT_console_gp_list_2d_pos(bpy.types.Operator):
    bl_idname = "devtools.console_gp_list_2d_pos"
    bl_label = "GP List 2D Coordinates"
    bl_description = "Set a one liner in console to list points 2D screen position in first listed 3D viewport"
    bl_options = {"REGISTER"}

    def execute(self, context):
        areatext = get_viewport_area_text(context)
        if not areatext:
            self.report({'ERROR'}, 'No 3D view editor found in areas')
            return {'CANCELLED'}
        
        # list 2D coord of last stroke of active object
        text = f'[view3d_utils.location_3d_to_region_2d({areatext}.regions[5], {areatext}.spaces[0].region_3d, C.object.matrix_world @ p.co) for p in C.object.data.layers.active.active_frame.strokes[-1].points]'
        bpy.ops.console.insert(text=text)
        return {'FINISHED'}

class DEV_OT_console_gp_2d_to_3d(bpy.types.Operator):
    bl_idname = "devtools.console_gp_2d_to_3d"
    bl_label = "GP 2D to 3D"
    bl_description = "GP console 2d (region) to 3d (location)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        areatext = get_viewport_area_text(context)
        if not areatext:
            self.report({'ERROR'}, 'No 3D view editor found in areas')
            return {'CANCELLED'}

        text = f'view3d_utils.region_2d_to_location_3d({areatext}.regions[5], {areatext}.spaces[0].region_3d, co2d,  Vector((0,0,0)))'
        bpy.ops.console.insert(text=text)
        return {'FINISHED'}

class DEV_OT_console_gp_3d_to_2d(bpy.types.Operator):
    bl_idname = "devtools.console_gp_3d_to_2d"
    bl_label = "GP 3D to 2D"
    bl_description = "GP console 3d (location) to 2d (region)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        areatext = get_viewport_area_text(context)
        if not areatext:
            self.report({'ERROR'}, 'No 3D view editor found in areas')
            return {'CANCELLED'}
        
        text = f'view3d_utils.location_3d_to_region_2d({areatext}.regions[5], {areatext}.spaces[0].region_3d, co)'
        bpy.ops.console.insert(text=text)
        return {'FINISHED'}

###---FUNC PANEL

class DEV_MT_console_gp_menu(bpy.types.Menu):
    bl_label = "GPencil Templates"
    bl_idname = "DEV_MT_console_gp_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("devtools.console_insert_text", text='GP Point Access').text='C.object.data.layers.active.active_frame.strokes[-1].points[0]' # , icon='GP_SELECT_POINTS'
        layout.separator()
        layout.operator("devtools.console_insert_text", text='Import view3d_utils').text='from bpy_extras import view3d_utils'
        # layout.label(text='Using view3d_utils:')
        layout.operator("devtools.console_gp_list_2d_pos", text='GP List 2D Coordinates') # , icon='STICKY_UVS_DISABLE'
        layout.operator("devtools.console_gp_2d_to_3d", text='GP 2D to 3D') # , icon='VIEW3D'
        layout.operator("devtools.console_gp_3d_to_2d", text='GP 3D to 2D') # , icon='STICKY_UVS_LOC'
        
        # call another menu
        # layout.operator("wm.call_menu", text="Unwrap").name = "VIEW3D_MT_uv_map"

def devtool_console(self, context):
    layout = self.layout
    layout.menu('DEV_MT_console_gp_menu')
    layout.operator('devtools.console_context_area_access')
    layout.operator("devtools.create_context_override")

classes = (
    DEV_OT_console_insert_text,
    DEV_OT_console_gp_list_2d_pos,
    DEV_OT_console_gp_2d_to_3d,
    DEV_OT_console_gp_3d_to_2d,
    DEV_MT_console_gp_menu,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.CONSOLE_HT_header.append(devtool_console)

def unregister():
    bpy.types.CONSOLE_HT_header.remove(devtool_console)
    for cls in classes:
        bpy.utils.unregister_class(cls)
