import bpy
import os
from pathlib import Path
from . import fn


class DEV_OT_open_external_editor(bpy.types.Operator):
    bl_idname = "devtools.open_external_editor"
    bl_label = "Open Externally"
    bl_description = "Open in external default program or software specified in addon preferences"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, _override = fn.get_text(context)
        if text.filepath: # condition only if call from search (ui button masked if no external data)
            fp = Path(text.filepath).resolve().as_posix()
            ret = fn.open_file(fp) # resolve links
            if 'CANCELLED' in ret:
                mess = f'! Could not open: {fp}'
            else:
                mess = f'Opened: {fp}'
        else:
            mess = 'Text is internal only'

        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_open_script_folder(bpy.types.Operator):
    bl_idname = "devtools.open_script_folder"
    bl_label = "Open Folder"
    bl_description = "Open text folder in OS browser"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = fn.get_text(context)
        if text.filepath:
            mess = fn.open_folder(os.path.dirname(text.filepath))
        else:
            mess = 'Text is internal only'

        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_open_filepath(bpy.types.Operator):
    bl_idname = "devtools.open_filepath"
    bl_label = "Open Folder At Given Filepath"
    bl_description = "Open given filepath in OS browser"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    fp : bpy.props.StringProperty()

    def execute(self, context):
        filepath = self.fp
        if not filepath:
            print('Problem ! No filepath was received in operator')
            return {"CANCELLED"}

        if not os.path.exists(filepath):
            print('Filepath not found', filepath)
            return {"CANCELLED"}

        mess = fn.open_folder(filepath)

        self.report({'INFO'}, mess)
        return {"FINISHED"}


classes = (
    DEV_OT_open_external_editor,
    DEV_OT_open_script_folder,
    DEV_OT_open_filepath,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
