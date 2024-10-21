import bpy
import os
from pathlib import Path
from sys import platform
import subprocess
from . import fn


class DEV_OT_open_external_editor(bpy.types.Operator):
    bl_idname = "devtools.open_external_editor"
    bl_label = "Open Externally"
    bl_description = "Open in external default program or software specified in addon preferences"
    bl_options = {"REGISTER"} # , "INTERNAL"

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

# WIP
class DEV_OT_open_editor_from_python_command(bpy.types.Operator):
    bl_idname = "devtools.open_editor_from_python_command"
    bl_label = "Open Editor From Python Command Copy"
    bl_description = "Open file containing python operator in external editor (set in preference)"
    bl_options = {"REGISTER"}

    identifier : bpy.props.StringProperty(default='', options={'SKIP_SAVE'})

    def invoke(self, context, event):
        prefs = fn.get_addon_prefs()
        self.editor = fn.get_external_editor()
        if not self.editor:
            mess = fn.missing_external_editor()
            self.report({'WARNING'}, mess)
            return {'CANCELLED'}

        op_name = self.identifier

        if not self.identifier:
            clip = context.window_manager.clipboard
            if not clip.startswith('bpy.ops'):
                self.report({'ERROR'}, 'Clipboard should contain a python operator command "bpy.ops..."')
                return {'CANCELLED'}

            op_name = clip.strip()
            if op_name.startswith('bpy.ops.'):
                op_name = op_name.split('.', 2)[-1].split('(')[0]
        else:
            # Create idname from identifier (which derive from bl_idname)
            if '_OT_' in op_name:
                op_name = '.'.join(op_name.split('_OT_')).lower()
                print(self.identifier, '->', op_name)

        addon_spec = fn.get_addon_from_python_command(op_name) # use_identifier=bool(self.identifier)
        if addon_spec is None:
            self.report({'ERROR'}, f'Could not found addon for operator "{op_name}"')
            return {'CANCELLED'}
        
        _name, path = addon_spec
        ## use addon module name and search for file and line containing this idname in files
        addon = Path(path)
        
        if addon.name == '__init__.py':
            file_to_search = [f for f in addon.parent.resolve().rglob('*.py') if not '.git' in f.as_posix()]
        else:
            file_to_search = [addon]
        
        print(f'Searching at {addon}')
        print(f'Looking in {len(file_to_search)} file')#Dbg
        # print('file_to_search: ', file_to_search)
        
        self.pyfiles = []
        for f in file_to_search:
            # print(f'reading: {f}')#Dbg
            with f.open('r') as fd:
                for i, l in enumerate(fd.readlines()):
                    if op_name in l and 'bl_idname' in l:
                        self.pyfiles.append((f, i))
        
        if not self.pyfiles:
            self.report({'ERROR'}, f'Could not found relevant files in addon for operator {op_name}')
            return {'CANCELLED'}
        
        # for file, line in self.pyfiles:
        #     print(file, line)

        self.report({'INFO'}, f'Found {len(self.pyfiles)} occurence(s)')
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        editor_name = Path(self.editor).stem
        for path, line in self.pyfiles:
            goto_line = f'{path}:{line}'
            box = col.box()
            boxcol = box.column()
            boxcol.alignment = 'LEFT'
            button_row = boxcol.row(align=True)
            op = button_row.operator('devtools.open_error_file', text=f'{Path(path).name} : {line}', icon='MENU_PANEL')
            op.path_line = goto_line
            op.use_external = False
            if editor_name in ('code', 'codium'):
                op = button_row.operator('devtools.open_error_file', text='', icon='TEXT')
                op.path_line = goto_line
                op.use_external = True
            else:
                # can't use line if the editor is not known
                # need formatting according to editor
                button_row.operator('devtools.open_file_in_editor', text='', icon='TEXT').filepath = str(path)
    
    def execute(self, context):
        return {"FINISHED"}

class DEV_OT_open_in_editor(bpy.types.Operator):
    """Use command set in prefs to open folder in a specific editor"""
    bl_idname = "dev.open_in_editor"
    bl_label = "Open In Editor"
    bl_options = {'REGISTER', 'INTERNAL'}

    filepath : bpy.props.StringProperty()
    use_folder : bpy.props.BoolProperty(name='always use folder',
        default=False, options={'SKIP_SAVE'})

    def execute(self, context):
        editor = fn.get_external_editor()
        if not editor:
            mess = fn.missing_external_editor()
            self.report({'WARNING'}, mess)
            return {'CANCELLED'}

        fp = self.filepath
        fpo = Path(fp)
        ## Always resolve...
        # if fpo.is_symlink():
        fpo = fpo.resolve() 
        fp = fpo.as_posix()

        if self.use_folder and fpo.is_file():
            fpo = fpo.parent
            fp = fpo.as_posix()

        subprocess.Popen([editor, fp], shell=platform.startswith('win'))

        """
        # auto launch from available editor
        from shutil import which
        if which('code'):
            subprocess.Popen(['code', '-n', fp], shell=platform.startswith('win')) # -r == reuse same editor
        elif which('codium'):
            subprocess.Popen(['codium', '-n', fp], shell=platform.startswith('win'))
        # add syntax for other editor > pycharm > sublime > atom
        else:
            self.report({'ERROR'}, "Did not found an editor that support opening a folder as workspace") """
            
        return {'FINISHED'}

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


class DEV_OT_open_file_in_editor(bpy.types.Operator):
    bl_idname = "devtools.open_file_in_editor"
    bl_label = "Open Given File With Editor"
    bl_description = "Open in external  software specified in addon preferences"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath: bpy.props.StringProperty(name='Filepath', options={'SKIP_SAVE'})

    def execute(self, context):
        fp = Path(self.filepath).resolve().as_posix()
        ret = fn.open_file(fp)
        if 'CANCELLED' in ret:
            mess = f'! Could not open: {fp} !'
        else:
            mess = f'Opened: {fp}'
        self.report({'INFO'}, mess)
        return {"FINISHED"}

class DEV_OT_open_devtools_prefs(bpy.types.Operator):
    bl_idname = "dev.open_devtools_prefs"
    bl_label = "Open Devtool Prefs"
    bl_description = "Open user preferences window in addon tab with addon name"
    bl_options = {"REGISTER", 'INTERNAL'}

    def execute(self, context):
        from .__init__ import bl_info
        fn.open_addon_prefs_by_name(name=bl_info['name'], module=__package__)
        return {'FINISHED'}

classes = (
    DEV_OT_open_external_editor,
    DEV_OT_open_in_editor,
    DEV_OT_open_script_folder,
    DEV_OT_open_filepath, # open folder
    DEV_OT_open_file_in_editor, # open file with external editor
    DEV_OT_open_editor_from_python_command,
    DEV_OT_open_devtools_prefs,
)

def python_command_open_ui(self, context):
    layout = self.layout
    # print(dir(context))
    # if getattr(context, "button_prop", None):
    #     print(context.button_prop)
    #     rna = context.button_prop.bl_rna
    #     print(f'context.button_operator.bl_rna: identifier(Class) = "{rna.identifier}", name(label) = "{rna.name}"')
    #     print(dir(context.button_prop))
    #     print(context.button_prop.path_)
    #     print(context.button_prop.identifier)
    #     print()
    #     print(dir(context.button_prop.bl_rna))
    if getattr(context, "button_operator", None):
        rna = context.button_operator.bl_rna
        # print(f'context.button_operator.bl_rna: identifier(Class) = "{rna.identifier}", name(label) = "{rna.name}"')
        layout.operator('devtools.open_editor_from_python_command', text="Open In Code Editor").identifier = rna.identifier

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    if bpy.app.version >= (3,3,0):
        bpy.types.UI_MT_button_context_menu.append(python_command_open_ui)

def unregister():
    if bpy.app.version >= (3,3,0):
        bpy.types.UI_MT_button_context_menu.remove(python_command_open_ui)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
