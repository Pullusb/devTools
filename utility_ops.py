import bpy
from bpy.types import Operator
from . import fn

class DEVTOOLS_OT_copy_text_to_clipboard(Operator):
    bl_idname = "devtools.copy_text_to_clipboard"
    bl_label = "Copy String"
    bl_description = "Copy passed string to clipboard"
    bl_options = {"REGISTER", "INTERNAL"}

    text : bpy.props.StringProperty(options={'SKIP_SAVE'})
    
    report_info : bpy.props.BoolProperty(name="Report Info", default=True)
    
    def execute(self, context):
        if not self.text:
            self.report({'WARNING'}, f'Nothing to copy!')
            return {"CANCELLED"}
        bpy.context.window_manager.clipboard = self.text
        if self.report_info:
            self.report({'INFO'}, f'Copied: {self.text}')
        return {"FINISHED"}

class DEVTOOLS_OT_info_note(Operator):
    bl_idname = "devtools.info_note"
    bl_label = "Info Note"
    bl_description = "Info Note"
    bl_options = {"REGISTER", "INTERNAL"}

    text : bpy.props.StringProperty(default='', options={'SKIP_SAVE'})
    title : bpy.props.StringProperty(default='Help', options={'SKIP_SAVE'})
    icon : bpy.props.StringProperty(default='INFO', options={'SKIP_SAVE'})

    @classmethod
    def description(self, context, properties):
        return properties.text

    def execute(self, context):
        ## Split text in list of lines
        lines = self.text.split('\n')
        fn.show_message_box(_message=lines, _title=self.title, _icon=self.icon)
        return {"FINISHED"}

classes = (
DEVTOOLS_OT_info_note,
DEVTOOLS_OT_copy_text_to_clipboard,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
