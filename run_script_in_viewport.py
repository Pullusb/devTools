import bpy

# Run text data block from viewport (allow to run in a 3D view context, without the neede of an override)

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
    exec(compile(text_body, text_name, 'exec'))

## -- Operators --

class DEV_OT_run_script_in_viewport(bpy.types.Operator):
    bl_idname = "dev.run_script_in_viewport"
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
    bl_description = "Execute the biggest visible script (area size) in viewport context"
    bl_options = {"REGISTER", "INTERNAL"}

    all_windows : bpy.props.BoolProperty(default=True, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return len(bpy.data.texts) and opened_text_editor_poll()

    def execute(self, context):
        text = find_biggest_opened_text_block(all_windows=self.all_windows)
        if not text:
            self.report({'ERROR'}, 'No script found. A text editor need to be open with some text')
            return {'CANCELLED'}

        # print(f'Executing script: {text.name}')
        self.report({'INFO'}, f'Execute script: "{text.name}"')
        exec_text_datablock(text)
        return {"FINISHED"}

## -- Panel --

def opened_text_editor_poll():
    ## in all windows
    # for window in bpy.context.window_manager.windows 
    #     for area in window.screen.areas:
    #         if area.type == 'TEXT_EDITOR':
    #             return True

    ## in active window
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            return True

## -- Run Opened Scripts UI --
def run_opened_script_ui(layout, context):
        if len(bpy.data.texts) == 1:
            ## expose the sole script
            name = bpy.data.texts[0].name
            layout.operator('dev.run_script_in_viewport', text=f'Run: {name}', icon='PLAY').txt_name = name
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

    def draw(self, context):
        run_opened_script_ui(self.layout, context)


## -- Script List UI --
def script_list_ui(layout, context):
    col = layout.column(align=False)
    for text in bpy.data.texts:
        ## Skip empty text
        if len(text.lines) == 1 and not text.lines[0].body.strip():
            continue
        col.operator('dev.run_script_in_viewport', text=text.name, icon='PLAY').txt_name = text.name

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
    if not opened_text_editor_poll():
        return
    self.layout.operator('dev.run_opened_script', text='', icon='PLAY')

classes = (
DEV_OT_run_script_in_viewport,
DEV_OT_run_opened_script,
DEV_PT_run_text_scripts_ui,
DEV_PT_script_list_ui,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.types.VIEW3D_HT_header.append(run_opened_script_header_ui) # add to viewport header

def unregister():
    # bpy.types.VIEW3D_HT_header.remove(run_opened_script_header_ui) # add to viewport header
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
