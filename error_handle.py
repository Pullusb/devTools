from typing import Tuple
import bpy
import os
import sys
import re
from pathlib import Path
import traceback
import subprocess
from . import fn

def get_last_traceback(to_clipboad=False) -> Tuple[int, str]:
    '''Get last traceback error details summed in string
    return a tuple'''
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
                print()
                return (1, "bad recursion")

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
        print()
        return (1, 'No error traceback found by sys module')

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
        print()
        return (1, 'No message to display')

    if message and to_clipboad:
        bpy.context.window_manager.clipboard = message

    return (0, message)


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


class DEV_OT_copy_last_traceback(bpy.types.Operator):
    bl_idname = "devtools.copy_last_traceback"
    bl_label = "Copy Last Traceback"
    bl_description = "Copy last traceback error in clipboard"
    bl_options = {"REGISTER"}

    def execute(self, context):
        error, content = get_last_traceback(to_clipboad=True)
        if error:
            self.report({'ERROR'}, content)
            return {"CANCELLED"}
        return {"FINISHED"}

class DEV_OT_artificial_error(bpy.types.Operator):
    bl_idname = "devtools.artificial_error"
    bl_label = "Artificial Error"
    bl_description = "Generate an artificial Error"
    bl_options = {"REGISTER"}

    def execute(self, context):
        ## Trigger zero Division Error
        provoked_error = 2/0
        return {"FINISHED"}

class DEV_OT_open_error_file(bpy.types.Operator):
    bl_idname = "devtools.open_error_file"
    bl_label = "Open Traceback Errors"
    bl_description = "Open the file where there as been a traceback error"
    bl_options = {"REGISTER"}

    path_line : bpy.props.StringProperty(options={'SKIP_SAVE'})
    use_external : bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})
    from_clipboard : bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    def invoke(self, context, event):
        if self.path_line:
            print('self.path_line: ', self.path_line)
            if self.use_external:
                editor = fn.get_addon_prefs().external_editor
                if not editor:
                    self.report({'ERROR'}, 'external editor need to be specified in preferences')
                    return {"CANCELLED"}
                ## Use passed line direcly when recalling operator
                cmd = [editor, '--goto', self.path_line]
                print('cmd: ', cmd)
                
                ## Note: Never get what happen with the shell argument
                ## True on windows and False on linux seem to work empirically...
                subprocess.Popen(cmd, shell=sys.platform.startswith('win'))
            else:
                # Open file in blender
                path, linum = self.path_line.rsplit(':', 1)
                linum = int(linum)
                fn.set_file_in_text_editor(path, linum=linum, context=context)
            return {"FINISHED"}

        pattern = r'[Ff]ile [\'\"](.*?)[\'\"], line (\d+),'

        self.error_desc = None
        self.error_list = []
        if self.from_clipboard:
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
            
            '''## old method
            stack = get_traceback_stack()
            if stack is None:
                self.report({'ERROR'}, 'No last traceback found using "sys.last_traceback"')
                return {"CANCELLED"}
            # first result of findall with pattern of first element of error (traceback frame)
            self.error_list = [re.findall(pattern, str(error[0]))[0] for error in stack]
            '''

            tb_list = traceback.extract_tb(sys.last_traceback)
            if not tb_list:
                self.report({'ERROR'}, 'No last traceback found using "sys.last_traceback"')
                return {"CANCELLED"}
                
            self.error_list = [(str(Path(t.filename).resolve()), t.lineno, t.line, t.name) for t in tb_list]

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
        
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for item in self.error_list:
            path, line = item[0], item[1]
                
            # print(path, '  ', line)
            goto_line = f'{path}:{line}'
            box = col.box()
            boxcol = box.column()
            boxcol.alignment = 'LEFT'
            button_row = boxcol.row(align=True)
            op = button_row.operator('devtools.open_error_file', text=f'{Path(path).name} : {line}', icon='MENU_PANEL')
            op.path_line = goto_line
            op.use_external = False
            op = button_row.operator('devtools.open_error_file', text='', icon='TEXT')
            op.path_line = goto_line
            op.use_external = True
            boxcol.label(text=path)
            if len(item) > 3 and item[3]:
                boxcol.label(text=f'in: {item[3]}')
            if len(item) > 2 and item[2]:
                boxcol.label(text=item[2])
            col.separator()
        
        if self.error_desc:
            for l in self.error_desc.split('\n'):
                row = col.row()
                row.alignment = 'LEFT'
                row.label(text=l)

    def execute(self, context):
        if self.path_line:
            return {"FINISHED"}
        return {"FINISHED"}

def help_error_menu(self, context):
    layout = self.layout
    layout.separator()
    ## titles:
    # Open Last Errors /or/ Open Last Traceback File
    # Open Errors From Clipboard /or/ Open File From Copied Error
    layout.operator('devtools.open_error_file', text='Open Traceback Errors', icon='FILE')
    layout.operator('devtools.open_error_file', text='Open Errors From Clipboard', icon='PASTEDOWN').from_clipboard = True
    # Copy is beta
    # layout.operator('devtools.copy_last_traceback', text='Copy Last Traceback', icon='COPYDOWN') 

classes = (
    DEV_OT_open_error_file,
    DEV_OT_artificial_error,
    DEV_OT_copy_last_traceback,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_help.append(help_error_menu)

def unregister():
    bpy.types.TOPBAR_MT_help.remove(help_error_menu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
