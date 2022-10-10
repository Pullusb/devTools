import bpy
import os
import sys
import re
from pathlib import Path
import subprocess
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

"""
def get_last_traceback(to_clipboad=False):
    '''Get last traceback error details summed in string'''
    import sys
    message = ''
    linum = ''

    if hasattr(sys, "last_traceback") and sys.last_traceback:
        i = 0
        last=sys.last_traceback.tb_next
        tbo = None
        while last:
            i+=1
            tbo = last
            last = last.tb_next
            if i>100:
                print("bad recursion")
                return False

        if not tbo: tbo = sys.last_traceback

        linum = sys.last_traceback.tb_lineno# first linum
        message += f'from line {str(linum)}\n'

        frame = str(tbo.tb_frame)
        if frame:
            if 'file ' in frame:
                # frame = 'file: ' + frame.split('file ')[1]
                frame = '\n'.join(frame.split(', ')[1:3])
            message += f'{frame}\n'

    else:
        print('No error traceback found by sys module')
        return

    if hasattr(sys, "last_type") and sys.last_type:
        error_type = str(sys.last_type)
        error_type = error_type.replace("<class '", "").replace("'>","")
        message =  f'type {error_type}\n{message}'

    if hasattr(sys, "last_value") and sys.last_value:
        message += f'error : {str(sys.last_value)}\n'

        if not linum and hasattr(sys.last_value, "lineno"):# maybe not usefull
            print('use "last_value" line num')
            message += f'line {str(sys.last_value.lineno)}\n'

    if not message :
        print('No message to display')
        return

    if message and to_clipboad:
        bpy.context.window_manager.clipboard = message

    return message
"""

def get_traceback_stack(tb=None):
    if tb is None:
        tb = sys.last_traceback
    stack = []
    if tb and tb.tb_frame is None:
        tb = tb.tb_next
    while tb is not None:
        stack.append((tb.tb_frame, tb.tb_lineno))
        tb = tb.tb_next
    return stack


# error = get_last_traceback()

class DEV_OT_open_error_file(bpy.types.Operator):
    bl_idname = "devtools.open_error_file"
    bl_label = "Open Error"
    bl_description = "Open the file where there as been a traceback error"
    bl_options = {"REGISTER"}

    # @classmethod
    # def poll(cls, context):
    #     return context.area.type == 'TEXT_EDITOR'

    path_line : bpy.props.StringProperty(options={'SKIP_SAVE'})


    def open_path_line(self):
        pathline = ':'.join(self.chosen_file)
        cmd = [self.external_editor, '--goto', pathline]
        print('cmd: ', cmd)
        subprocess.Popen(cmd, shell=False)

    def invoke(self, context, event):
        
        self.external_editor = fn.get_addon_prefs().external_editor
        # TODO add solution to open file in blender at line
        if not self.external_editor:
            self.report({'ERROR'}, 'external editor need to be specified in preferences')
            return {"CANCELLED"}

        if self.path_line:
            ## use passed line direcly
            cmd = [self.external_editor, '--goto', self.path_line]
            print('cmd: ', cmd)
            subprocess.Popen(cmd, shell=False)
            return {"FINISHED"}
        # pattern = r'[Ff]ile \"(.*?)\", line (\d+),'
        pattern = r'[Ff]ile [\'\"](.*?)[\'\"], line (\d+),'

        from_clipboard = False
        self.error_desc = None
        self.error_list = []
        if from_clipboard:
            clip = context.window_manager.clipboard
            try:
                self.error_list = re.findall(pattern, clip)
            except:
                self.report({'ERROR'}, 'Failed to parse clipboard for filepath and line number')
                return {"CANCELLED"}

        else:
            if not hasattr(sys, "last_traceback"):
                self.report({'ERROR'}, 'No last traceback found with sys"')
                return {"CANCELLED"}
            stack = get_traceback_stack()
            # print('stack: ', stack)
            if stack is None:
                self.report({'ERROR'}, 'No last traceback found using "sys.last_traceback"')
                return {"CANCELLED"}

            # first result of findall with pattern of first element of error (traceback frame)
            self.error_list = [re.findall(pattern, str(error[0]))[0] for error in stack]
            # for error in stack:
            #     print('error', error)
            #     str_file = str(error[0])
            #     error_file = re.findall(pattern, str_file)[0]
            #     print('error_file: ', error_file)
            #     self.error_list.append(error_file)
            #     print('linum: ', error[1])

            ## add error type and description
            error_type = str(sys.last_type)
            error_type = error_type if error_type else "Error"
            error_type = error_type.replace("<class '", "").replace("'>","")

            error_value = sys.last_value
            if error_value:
                self.error_desc = f'{error_type} : {str(error_value)}\n'

        if not self.error_list:
            self.report({'ERROR'}, 'No filepath and line number found in clipboard')
            return {"CANCELLED"}

        if len(self.error_list) == 1:
            return self.execute(context)
        
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for path, line in self.error_list:
            # print(path, '  ', line)
            goto_line = f'{path}:{line}'
            box = col.box()
            boxcol = box.column()
            boxcol.operator('devtools.open_error_file', text=f'{Path(path).name} ({line})').path_line = goto_line
            boxcol.label(text=path)
            col.separator()
        
        if self.error_desc:
            for l in self.error_desc.split('\n'):
                row = col.row()
                row.alignment = 'LEFT'
                row.label(text=l)

    def execute(self, context):
        if self.path_line:
            return {"FINISHED"}
        # In this case there is only one, open_
        self.chosen_file = self.error_list[-1]        
        self.open_path_line()

        self.report({'INFO'}, f'opening file {Path(self.chosen_file[0]).name} at line {self.chosen_file[1]}')
        return {"FINISHED"}

classes = (
    DEV_OT_open_external_editor,
    DEV_OT_open_error_file,
    DEV_OT_open_script_folder,
    DEV_OT_open_filepath,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
