from typing import Tuple
import bpy
import os
import sys
import re
import time
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
        last = sys.last_traceback.tb_next
        tbo = None
        while last:
            i+=1
            tbo = last
            last = last.tb_next
            if i>100:
                print()
                return (1, "bad recursion")

        if not tbo:
            tbo = sys.last_traceback

        if hasattr(sys, "last_type") and sys.last_type:
            error_type = str(sys.last_type)
            error_type = error_type.replace("<class '", "").replace("'>","")
            # message += f'{error_type}\n'
            message += f'type : {error_type}\n'

        if hasattr(sys, "last_value") and sys.last_value:
            # message += f'{sys.last_value}\n'
            message += f'error: {sys.last_value}\n'


        # linum = sys.last_traceback.tb_lineno # first linum # Added to message in frame below
        # message += f'from line {str(linum)}\n'

        ## Simple and naive extraction method from traceback as str: elements 1 is the file path, 2 is the line number
        # frame = str(tbo.tb_frame)
        # if frame:
        #     ## Example of a frame as str: <frame at 0x000001EEE07530F0, file 'C:\\Users\\samue\\AppData\\Roaming\\Blender Foundation\\Blender\\4.4\\scripts\\addons\\storytools\\keymaps.py', line 221, code execute>
        #     if 'file ' in frame:
        #         # frame = 'file: ' + frame.split('file ')[1]
        #         frame = '\n'.join(frame.split(', ')[1:3])
        
        if frame := tbo.tb_frame:
            ## line is either in tbo.tb_lineno or in tbo.tb_frame.f_lineno
            ## file url is in "tbo.tb_frame.f_code.co_filename"
            message += f"file : {Path(frame.f_code.co_filename).as_posix()}\n"
            message += f"line : {frame.f_lineno}\n"

            ## Frame contains local variables as dict in "tb_frame.f_locals" can be useful to debug 
            if frame.f_locals:
                message += '\nLocals:\n'
                for k, v in frame.f_locals.items():
                    message += f'  {k} : {v}\n'
    else:
        print()
        return (1, 'No error traceback found by sys module')

        # if not linum and hasattr(sys.last_value, "lineno"): # already set in frame alanysis
        #     print('use "last_value" line num')
        #     message += f'\nline {str(sys.last_value.lineno)}\n'

    if not message :
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

class DEV_OT_hello_world(bpy.types.Operator):
    bl_idname = "devtools.hello_world"
    bl_label = "Hello World"
    bl_description = "Write Hello World message in console (help find associated console when multiple ones are open)"
    bl_options = {"REGISTER"}

    def execute(self, context):

        print(f"\n***\nHello world! - Blender {bpy.app.version_string}({bpy.app.version_cycle}) - {time.strftime('%H:%M:%S')}\n***")
        return {"FINISHED"}

class DEV_OT_clear_last_traceback(bpy.types.Operator):
    bl_idname = "devtools.clear_last_traceback"
    bl_label = "Clear Last Traceback"
    bl_description = "Clear last traceback infos (deleting sys.last_traceback, etc)"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        if hasattr(sys, 'last_traceback') and sys.last_traceback is not None:
            del sys.last_traceback
        if hasattr(sys, 'last_value') and sys.last_value is not None:
            del sys.last_value
        if hasattr(sys, 'last_type') and sys.last_type is not None:
            del sys.last_type
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
            # print('self.path_line: ', self.path_line)#Dbg
            if self.use_external:
                editor = fn.get_external_editor()
                if not editor:
                    mess = fn.missing_external_editor()
                    self.report({'WARNING'}, mess)
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


            ## TODO: Handle case when started from Blender and have a script
 
            ## sometimes resolve() give a too long -not needed- url.
            ## Always resolve with list comprehension
            # self.error_list = [(str(Path(t.filename).resolve()), t.lineno, t.line, t.name) for t in tb_list]

            always_resolve = False # Only resolve on symlink
            for t in tb_list:

                ## available in t (summary traceback frame):
                ## '_line', '_original_line', 'colno', 'end_colno', 'end_lineno', 'filename', 'line', 'lineno', 'locals', 'name'
                # if bpy.data.filepath and t.filename.startswith(bpy.data.filepath):

                file_path = Path(t.filename)
                current_blend = Path(bpy.data.filepath).name
                
                # Case when script executed from blend and is loaded externally
                if file_path.parent.name == current_blend:
                    txt = bpy.data.texts.get(file_path.name)
                    if txt:
                        if txt.filepath:
                            file_path = Path(os.path.abspath(bpy.path.abspath(txt.filepath)))

                if always_resolve or (file_path.exists() and file_path.is_symlink()):
                    file_path = file_path.resolve() # resolve symlink

                self.error_list.append((str(file_path), t.lineno, t.line, t.name))

            ## add error type and description
            error_type = str(sys.last_type)
            error_type = error_type if error_type else "Error"
            error_type = error_type.replace("<class '", "").replace("'>","")

            error_value = sys.last_value
            if error_value:
                self.error_desc = f'{error_type} : {str(error_value)}\n'
            
            # Get locals
            self.locals_as_text = None
            if last_traceback := sys.last_traceback:
                if frame := last_traceback.tb_frame:
                    if locals := frame.f_locals:
                        self.locals_as_text = '\n'.join([f'{k} : {v}' for k, v in locals.items()])

        if not self.error_list:
            self.report({'ERROR'}, 'No filepath and line number found in clipboard')
            return {"CANCELLED"}
        
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        # error_clipboard = []
        for item in self.error_list:
            # 0:file_path, 1:line_num, 2:line_content, 3:func_name
            path, line = item[0], item[1]
                
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
                # function name
                boxcol.label(text=f'in: {item[3]}')
            if len(item) > 2 and item[2]:
                # line body
                boxcol.label(text=item[2])

            col.separator()

        row = layout.row()
        row.alignment = 'LEFT'
        row.operator('devtools.clear_last_traceback', text='Clear Traceback', icon='CANCEL')
        row.operator('devtools.copy_last_traceback', text='Copy Traceback', icon='COPYDOWN')
        
        ## Show locals
        op = row.operator('devtools.info_note', text='Locals', icon='INFO')
        op.title = 'Locals'
        op.text = self.locals_as_text

        if self.error_desc:
            for l in self.error_desc.split('\n'):
                row = col.row()
                row.alignment = 'LEFT'
                row.label(text=l)

    def execute(self, context):
        if self.path_line:
            return {"FINISHED"}
        return {"FINISHED"}

def help_error_top_bar(self, context):
    layout = self.layout
    if hasattr(sys, 'last_traceback') and sys.last_traceback:
        region = context.region
        if region.alignment == 'RIGHT':
            layout.operator("devtools.open_error_file", text = "", icon = 'ERROR')

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
    DEV_OT_hello_world,
    DEV_OT_copy_last_traceback,
    DEV_OT_clear_last_traceback,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_HT_upper_bar.append(help_error_top_bar)
    bpy.types.TOPBAR_MT_help.append(help_error_menu)

def unregister():
    bpy.types.TOPBAR_MT_help.remove(help_error_menu)
    bpy.types.TOPBAR_MT_help.remove(help_error_top_bar)

    for cls in classes:
        bpy.utils.unregister_class(cls)
