import bpy
from pathlib import Path
from . import fn

from bpy.props import (
                BoolProperty,
                StringProperty,
                CollectionProperty,
                )

def get_viewport_area_text(context):
    screen = bpy.context.window.screen
    for i, area in enumerate(screen.areas):
        if area.type == 'VIEW_3D':
            return f'C.window.screen.areas[{i}]'


class DEV_OT_console_context_area_access(bpy.types.Operator):
    bl_idname = "devtools.console_context_area_access"
    bl_label = "Access Clicked Area"
    bl_description = "Launch then clic in any area to write access to it in console (with current layout)\nshift+clic on area to copy to clipboard"
    bl_options = {"REGISTER", "INTERNAL"}

    def invoke(self, context, event):
        self.console_override = None
        if context.area.type == 'CONSOLE':
            self.console_override = {'screen':context.window.screen, 'area': context.area}
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set("PICK_AREA")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            screen = context.window.screen       
            for i, a in enumerate(screen.areas):
                if (a.x < event.mouse_x < a.x + a.width
                and a.y < event.mouse_y < a.y + a.height):
                    print(f"Clicked in screen {screen.name} area of {a.type}")
                    access = f'bpy.context.screen.areas[{i}]'
                    print(access)
                    if event.shift:# <- Shift click condition to paper clip
                        context.window_manager.clipboard = access
                    self.report({'INFO'}, f'Screen {screen.name} area of {a.type} index {i}')#WARNING, ERROR
                    break
            
            # check for console in another area if not started from console
            if not self.console_override:
                for i, a in enumerate(screen.areas):
                    if a.type == 'CONSOLE':
                        self.console_override = {
                                    'screen':screen,
                                    'area'  :a,
                                    }
                        break    
            
            if self.console_override:
                context.window.cursor_set("DEFAULT") # reset cursor
                # bpy.ops.console.clear_line(self.console_override) # clear line ?
                bpy.ops.console.insert(self.console_override, text=access)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_set("DEFAULT")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

class DEV_OT_console_insert_and_exec(bpy.types.Operator):
    bl_idname = "devtools.console_insert_and_exec"
    bl_label = "Console Insert And Exec"
    bl_description = "Insert and execute text in console"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'
    
    text : bpy.props.StringProperty(default='', options={'SKIP_SAVE'})

    def execute(self, context):
        fn.console_write_and_execute_multiline(self.text, clear_line=True)
        return {"FINISHED"}

class DEV_OT_console_insert_import(bpy.types.Operator):
    bl_idname = "devtools.console_insert_import"
    bl_label = "Console Insert Import Text"
    bl_description = "Insert and execute predefined imports in console"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):
        filename = 'console_imports.txt'
        header_file = Path(__file__).with_name(filename)
        if not header_file.exists():
            self.report({'ERROR'}, f'{filename} not found in addon folder! path used : {header_file}')
            return {"CANCELLED"}

        import_text = header_file.read_text()
        fn.console_write_and_execute_multiline(import_text, clear_line=True, context=context)
        return {"FINISHED"}

class DEV_OT_console_gp_list_2d_pos(bpy.types.Operator):
    bl_idname = "devtools.console_gp_list_2d_pos"
    bl_label = "GP List 2D Coordinates"
    bl_description = "Set a one liner in console to list points 2D screen position in first listed 3D viewport"
    bl_options = {"REGISTER", "INTERNAL"}

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
    bl_options = {"REGISTER", "INTERNAL"}

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
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        areatext = get_viewport_area_text(context)
        if not areatext:
            self.report({'ERROR'}, 'No 3D view editor found in areas')
            return {'CANCELLED'}
        
        text = f'view3d_utils.location_3d_to_region_2d({areatext}.regions[5], {areatext}.spaces[0].region_3d, co)'
        bpy.ops.console.insert(text=text)
        return {'FINISHED'}

class DEV_OT_console_api_search(bpy.types.Operator):
    bl_idname = "dev.console_api_search"
    bl_label = "Console Api Search"
    bl_description = "Explore API in console at specified datapath and return found names"
    bl_options = {"REGISTER"}

    search : StringProperty(name='Search',
    description='Word to search in api paths')

    def invoke(self, context, event):
        self.line = context.area.spaces.active.history[-1].body
        self.line = self.line.strip().rstrip('.').replace('C.', 'bpy.context.').replace('D.', 'bpy.data.')
        if not self.line:
            self.report({'ERROR'} , 'Empty line')
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.activate_init = True # place cursor in field
        row.prop(self, 'search', text='Search')
        col.label(text=f"In: {self.line}")

    def execute(self, context):
        if not self.search:
            self.report({'ERROR'}, 'Need search term')
            return {"CANCELLED"}

        bpy.ops.dev.api_search(
            'EXEC_DEFAULT', # no need invoke if from console is used
            data_path=self.line,
            dump_api_tree=False,
            search=self.search,
            from_console=True
            )
        return {"FINISHED"}

###---FUNC PANEL

class DEV_PG_history_line(bpy.types.PropertyGroup):
    select : BoolProperty(default=False)
    line : StringProperty()

class DEV_OT_copy_console_history_select(bpy.types.Operator):
    bl_idname = "dev.copy_console_history_select"
    bl_label = "Copy Console History"
    bl_description = "Copy multiple lines from console history"
    bl_options = {"REGISTER"}
    # bl_ui_units_x = 38

    search : StringProperty(name='Search',
    description='Word to search in api paths')
    
    history_lines : CollectionProperty(type=DEV_PG_history_line)
    
    block_breaks : BoolProperty(name='Use Block breaks',
        description='Add a blank line between each selected code block',
        default=True)

    def invoke(self, context, event):
        # self.history_lines.clear()
        for l in context.area.spaces.active.history[:-1]:
            if not l.body.strip():
                continue

            item = self.history_lines.add()
            item.line = l.body.rstrip() # keep indent
        if not self.history_lines:
            self.report({'ERROR'} , 'Empty Console History')
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        # TODO: add Bool at bottom of the list to add line retun between blocks
        # col.operator("console.insert", text='Test')

        layout = self.layout
        col = layout.column()
        row = col.row()
        row.prop(self, 'block_breaks', icon='FILE_TEXT')

        for item in self.history_lines:
            row = col.row()
            row.alignment = 'LEFT'
            row.prop(item, 'select', text='')
            # label, or insert ops ?
            row.operator("console.insert", text=item.line, emboss=False).text=item.line
            # row.prop(item, 'select', text=item.line)
        

    def execute(self, context):
        if self.block_breaks:
            print('with block')
            ## with block separation
            lines = []
            prev_select = False
            for i in self.history_lines:
                if i.select:
                    prev_select = True
                    lines.append(i.line)
                else:
                    if prev_select:
                        print('break')
                        lines.append('')
                        prev_select = False
        else:
            ## Without block separation
            lines = [i.line for i in self.history_lines if i.select]
        
        print(lines)
        context.window_manager.clipboard = '\n'.join(lines)
        self.history_lines.clear()
        return {"FINISHED"}

""" 
class DEV_PT_console_history_lines(bpy.types.Panel):
    bl_space_type = 'TOPBAR' # dummy
    bl_region_type = 'HEADER'
    bl_category = "Dev"
    bl_label = "Console History"
    bl_ui_units_x = 38

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        col = layout.column()
        for l in context.area.spaces.active.history[:-1]:
            if not l.body:
                continue
            row = col.row()
            row.alignment = 'LEFT'
            ## \n not trigger console enter, need intermediate ops
            # row.operator("console.insert", text='', icon='EVENT_RETURN').text=l.body + '\n'

            ## execute shortcut
            row.operator("console.insert", text=l.body, emboss=False).text=l.body
            # row.operator("console.execute", text='', icon='EVENT_RETURN')
"""

class DEV_MT_console_gp_template_menu(bpy.types.Menu):
    bl_label = "GPencil Templates"

    def draw(self, context):
        layout = self.layout
        layout.operator("console.insert", text='GP Point Access').text='C.object.data.layers.active.active_frame.strokes[-1].points[0]' # , icon='GP_SELECT_POINTS'
        layout.separator()
        layout.operator("console.insert", text='Import view3d_utils').text='from bpy_extras import view3d_utils'
        
        # layout.label(text='Using view3d_utils:')
        layout.operator("devtools.console_gp_list_2d_pos", text='GP List 2D Coordinates') # , icon='STICKY_UVS_DISABLE'
        layout.operator("devtools.console_gp_2d_to_3d", text='GP 2D to 3D') # , icon='VIEW3D'
        layout.operator("devtools.console_gp_3d_to_2d", text='GP 3D to 2D') # , icon='STICKY_UVS_LOC'

class DEV_MT_console_path_template_menu(bpy.types.Menu):
    bl_label = "GPencil Templates"

    def draw(self, context):
        layout = self.layout
        ## List all links (blend_path utils)
        layout.operator("console.insert", text='List blend_paths').text='for p in bpy.utils.blend_paths(absolute=False, packed=False, local=False): print(p)'
        ## List all libraries filepath
        layout.operator("console.insert", text='List libraries Filepath').text="for lib in bpy.data.libraries: print(lib.filepath) # print(f'{lib.name}: {lib.filepath}')"
        ## pprint list by type (augment pprint width to get datablock name + filepath on same line)
        layout.operator("console.insert", text='List Libs By Types').text="pp({name: [f'{b.name} : {b.filepath}' for b in getattr(bpy.data, name)] for name in ['images', 'movieclips', 'sounds', 'fonts', 'sounds', 'libraries']}, width=160)"

class DEV_MT_console_template(bpy.types.Menu):
    bl_label = "Templates"

    def draw(self, context):
        layout = self.layout
        # layout.operator("wm.call_menu", text="Gpencil").name = "DEV_MT_console_gp_template_menu"
        layout.menu("DEV_MT_console_gp_template_menu", text="Gpencil")
        layout.menu("DEV_MT_console_path_template_menu", text="List Path")
        # layout.operator("devtools.console_insert_and_exec", text='Classic Imports').text='import os, re, fnmatch, glob\nfrom pathlib import Path\nfrom pprint import pprint as pp'
        layout.operator("devtools.console_insert_import", text='Usual Imports')

class DEV_MT_console_dev(bpy.types.Menu):
    bl_label = "Dev"

    def draw(self, context):
        layout = self.layout
        ## Api explorer
        
        # layout.operator_context = 'INVOKE_DEFAULT' # INVOKE_REGION_WIN
        ops = layout.operator('dev.api_search', text='Search At Datapath')
        ops.data_path = context.area.spaces.active.history[-1].body.rstrip('. ')
        ops.dump_api_tree = False
        ops.from_console = True
        
        ## Dump Tree in clipboard
        ops = layout.operator('dev.api_search', text='Copy Api Tree At Datapath')
        ops.data_path = context.area.spaces.active.history[-1].body.rstrip('. ') if context.area.spaces.active.history[-1].body else 'bpy'
        ops.dump_api_tree = True
        ops.from_console = True

        
        ## History
        # layout.operator("wm.call_panel", text="History").name = "DEV_PT_console_history_lines" # old direct panel
        layout.operator("dev.copy_console_history_select", text="Select History")

        ## close after insertion
        # ops = layout.operator("wm.call_panel", text="History")
        # ops.name = "DEV_PT_console_history_lines" # old direct panel
        # ops.keep_open = False


## --- HEADER MENU

def devtool_console(self, context):
    layout = self.layout
    layout.menu('DEV_MT_console_template')
    layout.menu('DEV_MT_console_dev')
    layout.operator('devtools.console_context_area_access', text='Select Area')
    layout.operator("devtools.create_context_override")
    

## --- KEYMAP

addon_keymaps = []

def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    ## Console shortcuts

    km = addon.keymaps.new(name = "Console", space_type = "CONSOLE", region_type='WINDOW')

    ## simple pnael history
    # kmi = km.keymap_items.new('wm.call_panel', type='H', value='PRESS', ctrl=True)
    # kmi.properties.name ='DEV_PT_console_history_lines'

    ## history select
    kmi = km.keymap_items.new('dev.copy_console_history_select', type='H', value='PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('dev.console_api_search', type='F', value='PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("devtools.console_insert_import", type = "I", value = "PRESS", ctrl = True, shift=True)
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)    
    addon_keymaps.clear()


classes = (
    DEV_OT_console_context_area_access,
    DEV_OT_console_api_search,
    DEV_OT_console_gp_list_2d_pos,
    DEV_OT_console_gp_2d_to_3d,
    DEV_OT_console_gp_3d_to_2d,
    DEV_OT_console_insert_import,
    DEV_OT_console_insert_and_exec,

    DEV_PG_history_line,
    DEV_OT_copy_console_history_select,
    # DEV_PT_console_history_lines, # direct panel

    DEV_MT_console_path_template_menu,
    DEV_MT_console_gp_template_menu,
    DEV_MT_console_dev,
    DEV_MT_console_template
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.CONSOLE_HT_header.append(devtool_console)
    if not bpy.app.background:
        register_keymaps()

def unregister():
    if not bpy.app.background:
        unregister_keymaps()
    bpy.types.CONSOLE_HT_header.remove(devtool_console)
    for cls in classes:
        bpy.utils.unregister_class(cls)
