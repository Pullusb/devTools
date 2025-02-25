import bpy

# Run text data block from viewport (allow to run in a 3D view context, without the neede of an override)
## FIXME: can fail with imports in scripts, ex: from mathutils import Vector. try to launch using run_script with override

def find_biggest_opened_text_block(all_windows=True):
    '''get text used in the biggest visible text editor area, skip empty texts
    all_windows: bool, if True search in all windows, otherwise search in the active one

    return: Text datablock or None
    '''

    if all_windows:
        text_areas = [area for win in bpy.context.window_manager.windows 
                    for area in win.screen.areas if area.type == 'TEXT_EDITOR']
    else:
        text_areas = [area for area in bpy.context.screen.areas if area.type == 'TEXT_EDITOR']

    if len(text_areas) > 1:
        text_areas.sort(key=lambda area: area.width * area.height, reverse=True)

    for area in text_areas:
        for space in area.spaces:
            if space.type == 'TEXT_EDITOR':
                text = space.text
                if text:
                    ## Skip if text is empty
                    text_body = ''.join([line.body for line in text.lines]).strip()
                    if not text_body:
                        break
                    return text

def exec_text_datablock(text):
    text_name = text.name
    text_body = '\n'.join([line.body for line in text.lines])
    ## Error, some import or function are ignored using this method, missing context
    # exec(compile(text_body, text_name, 'exec'))
    ## Adding globals
    namespace = {}
    namespace.update(globals())
    exec(compile(text_body, text_name, 'exec'), namespace, namespace)

## -- Operators --

class DEV_OT_run_script_by_name(bpy.types.Operator):
    bl_idname = "dev.run_script_by_name"
    bl_label = "Run Script In Viewport"
    bl_description = "Execute script in 3D Viewport context"
    bl_options = {"REGISTER", "INTERNAL"}

    txt_name : bpy.props.StringProperty(options={'SKIP_SAVE'})

    def execute(self, context):
        if not self.txt_name:
            self.report({'ERROR'}, 'No text block name provided')
            return {'CANCELLED'}

        text = bpy.data.texts.get(self.txt_name)
        if not text:
            self.report({'ERROR'}, f'Text block "{self.txt_name}" not found')
            return {'CANCELLED'}
        
        exec_text_datablock(text)
        return {"FINISHED"}

class DEV_OT_run_opened_script(bpy.types.Operator):
    bl_idname = "dev.run_opened_script"
    bl_label = "Run Opened Script"
    bl_description = "Execute the biggest (area size) displayed script in viewport context\
        \nIf no visible script, popup script list\
        \nCtrl + Click to force popup script list"
    bl_options = {"REGISTER", "INTERNAL"}

    all_windows : bpy.props.BoolProperty(default=True, options={'SKIP_SAVE'})

    show_info : bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    @classmethod
    def description(cls, context, properties):
        if opened_text_editor_poll():
            return f'Run biggest displayed script: "{find_biggest_opened_text_block(properties.all_windows).name}"\
                \nCtrl + Click to select a script from list'
        elif len(bpy.data.texts) == 1:
            return f'Run the only script: "{bpy.data.texts[0].name}"\
                \nCtrl + Click to select a script from list'
        else:
            return "Popup script list"
        # return cls.bl_description

    @classmethod
    def poll(cls, context):
        return len(bpy.data.texts) # and opened_text_editor_poll()

    def invoke(self, context, event):
        self.text = find_biggest_opened_text_block(all_windows=self.all_windows)
        if event.ctrl:
            ## Force call list
            if len(bpy.data.texts) == 1:
                self.report({'WARNING'}, 'Only one text block in Blend, use the button without Ctrl to run it')
                return {'CANCELLED'}

            bpy.ops.wm.call_panel('INVOKE_DEFAULT', name='DEV_PT_script_list_ui')
            return {'CANCELLED'}
        
        if not self.text:
            if len(bpy.data.texts) == 1:
                ## No text visible but only one available, use it
                self.text = bpy.data.texts[0]
            else:
                ## No text visible but multiple available, show list 
                bpy.ops.wm.call_panel('INVOKE_DEFAULT', name='DEV_PT_script_list_ui')
                return {'CANCELLED'}
        
        ## At this point, a text is found.
        ## Either it's the biggest visible or there is only one in Blend
        return self.execute(context)

    def execute(self, context):
        if not self.text:
            self.report({'ERROR'}, 'No script found. A text editor need to be open with some text')
            return {'CANCELLED'}

        # print(f'Executing script: {self.text.name}')
        if self.show_info:
            self.report({'INFO'}, f'Execute script: "{self.text.name}"')
        exec_text_datablock(self.text)
        return {"FINISHED"}

## -- Panel --

def opened_text_editor_poll():
    ## in all windows
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'TEXT_EDITOR':
                return True

    ## in active window
    # for area in bpy.context.screen.areas:
    #     if area.type == 'TEXT_EDITOR':
    #         return True

## -- Run Opened Scripts UI --
def run_opened_script_ui(layout, context):
        if len(bpy.data.texts) == 1:
            ## expose the sole script
            name = bpy.data.texts[0].name
            layout.operator('dev.run_script_by_name', text=f'Run: {name}', icon='PLAY').txt_name = name
            return

        ## Hide button when no text editor opened ?
        # if opened_text_editor_poll():
        layout.operator('dev.run_opened_script', text='Run Opened Script', icon='PLAY').all_windows = False

class DEV_PT_run_text_scripts_ui(bpy.types.Panel):
    bl_label = "Run Scripts"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    @classmethod
    def poll(cls, context):
        return len(bpy.data.texts)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.popover('DEV_PT_editor_list_ui', text='', icon='PRESET')

    def draw(self, context):
        run_opened_script_ui(self.layout, context)


## -- Script List UI --
def script_list_ui(layout, context):
    col = layout.column(align=False)
    for text in bpy.data.texts:
        ## Skip empty text
        if len(text.lines) == 1 and not text.lines[0].body.strip():
            continue
        col.operator('dev.run_script_by_name', text=text.name, icon='PLAY').txt_name = text.name

class DEV_PT_script_list_ui(bpy.types.Panel):
    bl_label = "Script List"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_parent_id = "DEV_PT_run_text_scripts_ui"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return len(bpy.data.texts) > 1

    def draw(self, context):
        script_list_ui(self.layout, context)


## --- Editor list to enable single script button

## Popup to show visibility
class DEV_PT_editor_list_ui(bpy.types.Panel):
    bl_label = "Editor List"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_options = {'INSTANCED'}

    @classmethod
    def poll(cls, context):
        return len(bpy.data.texts)

    def draw(self, context):
        draw_editor_visibility_ui(self.layout, context)

## TODO add an update to all properties to refresh the whole UI

## Properties as a separate file ?
class DEV_PG_editor_visibility(bpy.types.PropertyGroup):
    view_3d : bpy.props.BoolProperty(name="View 3d", default=False, description="Display Run script button in View 3d")
    image_editor : bpy.props.BoolProperty(name="Image Editor", default=False, description="Display Run script button in Image Editor")
    node_editor : bpy.props.BoolProperty(name="Node Editor", default=False, description="Display Run script button in Node Editor")
    sequence_editor : bpy.props.BoolProperty(name="Sequence Editor", default=False, description="Display Run script button in Sequence Editor")
    clip_editor : bpy.props.BoolProperty(name="Clip Editor", default=False, description="Display Run script button in Clip Editor")
    dopesheet_editor : bpy.props.BoolProperty(name="Dopesheet Editor", default=False, description="Display Run script button in Dopesheet Editor")
    graph_editor : bpy.props.BoolProperty(name="Graph Editor", default=False, description="Display Run script button in Graph Editor")
    nla_editor : bpy.props.BoolProperty(name="Nla Editor", default=False, description="Display Run script button in Nla Editor")
    console : bpy.props.BoolProperty(name="Console", default=False, description="Display Run script button in Console")
    info : bpy.props.BoolProperty(name="Info", default=False, description="Display Run script button in Info")
    topbar : bpy.props.BoolProperty(name="Topbar", default=False, description="Display Run script button in Topbar")
    statusbar : bpy.props.BoolProperty(name="Statusbar", default=False, description="Display Run script button in Statusbar")
    outliner : bpy.props.BoolProperty(name="Outliner", default=False, description="Display Run script button in Outliner")
    properties : bpy.props.BoolProperty(name="Properties", default=False, description="Display Run script button in Properties")
    file_browser : bpy.props.BoolProperty(name="File Browser", default=False, description="Display Run script button in File Browser")
    preferences : bpy.props.BoolProperty(name="Preferences", default=False, description="Display Run script button in Preferences")
    text_editor : bpy.props.BoolProperty(name="Text Editor", default=False, description="Display Run script button in Text Editor")
    ## TODO: add a "All" property with an update to toggle all the others (assign without retriggering their own update)

def draw_editor_visibility_ui(layout, context):
    col = layout.column(align=True)
    # for editor in dir(context.scene.dev_editor_visibility):
    #     if editor.startswith(('__', 'name', 'rna_type', 'bl_rna')):
    #         continue
    #     col.prop(context.scene.dev_editor_visibility, editor)
    for editor_prop in context.scene.dev_editor_visibility.bl_rna.properties:
        if editor_prop.identifier in ('rna_type', 'name'):
            continue
        col.prop(context.scene.dev_editor_visibility, editor_prop.identifier)

## Add in existing "View cat > View panel"...
# def run_scripts_ui(self, context):
#     """Show button to launch biggset visible script in header"""
#     if not len(bpy.data.texts):
#         return
#     if opened_text_editor_poll():
#         run_opened_script_ui(self.layout, context)
#     script_list_ui(self.layout, context)

## Add to header (need a poll to hide when no text editor is opened)
def run_opened_script_header_ui(self, context):
    """Show button to launch biggset visible script in header"""

    ## Custom UI behavior
    # if not opened_text_editor_poll():
    #     if not len(bpy.data.texts):
    #         return
    #     elif len(bpy.data.texts) == 1:
    #         self.layout.operator('dev.run_script_by_name', text='', icon='PLAY').txt_name = bpy.data.texts[0].name
    #     else:
    #         self.layout.operator('wm.call_panel', text='', icon='PLAY').name = 'DEV_PT_script_list_ui'
    #     return

    ## Behavior to call script list is handled by the operator
    self.layout.operator('dev.run_opened_script', text='', icon='FILE_SCRIPT') # PLAY

## Global list of editor type (Unused)
# [
# 'VIEW_3D',
# 'IMAGE_EDITOR',
# 'NODE_EDITOR',
# 'SEQUENCE_EDITOR',
# 'CLIP_EDITOR',
# 'DOPESHEET_EDITOR',
# 'GRAPH_EDITOR',
# 'NLA_EDITOR',
# 'TEXT_EDITOR',
# 'CONSOLE',
# 'INFO',
# 'TOPBAR',
# 'STATUSBAR',
# 'OUTLINER',
# 'PROPERTIES',
# 'FILE_BROWSER',
# 'PREFERENCES'
# ]


# Or all in the same function comparing type:
def editor_header(self, context):
    area = bpy.context.area
    if getattr(bpy.context.scene.dev_editor_visibility, area.type.lower()):
        run_opened_script_header_ui(self, context)

classes = (
    # properties
    DEV_PG_editor_visibility,
    # Operators
    DEV_OT_run_script_by_name,
    DEV_OT_run_opened_script,
    # UI
    DEV_PT_editor_list_ui,
    DEV_PT_run_text_scripts_ui,
    DEV_PT_script_list_ui,
)

header_type = [
'VIEW3D_HT_header',
'PROPERTIES_HT_header',
'DOPESHEET_HT_header',
'SEQUENCER_HT_header',
'OUTLINER_HT_header',
'CLIP_HT_header',
'CONSOLE_HT_header',
'FILEBROWSER_HT_header',
'GRAPH_HT_header',
'IMAGE_HT_header',
'INFO_HT_header',
'NODE_HT_header',
'NLA_HT_header',
'SPREADSHEET_HT_header',
'STATUSBAR_HT_header',
'USERPREF_HT_header',
'TEXT_HT_header',
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dev_editor_visibility = bpy.props.PointerProperty(type=DEV_PG_editor_visibility)

    for header_name in header_type:
        if header := getattr(bpy.types, header_name):
            header.append(editor_header)

def unregister():
    for header_name in header_type:
        if header := getattr(bpy.types, header_name):
            header.remove(editor_header)

    del bpy.types.Scene.dev_editor_visibility
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
