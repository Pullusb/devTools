import bpy
from . import fn

class DEV_OT_install_pip_module(bpy.types.Operator):
    bl_idname = "devtools.install_pip_module"
    bl_label = "Install Pip Module"
    bl_description = "Ensure Pip and install pip module from string"
    bl_options = {"REGISTER"} # , "INTERNAL"

    # @classmethod
    # def poll(cls, context):
    #     return context.area.type == 'TEXT_EDITOR'

    module_name : bpy.props.StringProperty(name='Module Name')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'module_name')
        layout.separator()
        row = layout.row(align=True)
        row.operator('wm.url_open', text='Search on Pypi',icon='VIEWZOOM').url = f'https://pypi.org/search/?q={self.module_name}'
        row.operator('wm.url_open', text='Open Pypi page').url = f'https://pypi.org/project/{self.module_name}'

    def execute(self, context):
        if not self.module_name:
            self.report({'ERROR'}, 'Need to specify a module name')
            return {'CANCELLED'}
        self.report({'INFO'}, f'Installing {self.module_name}')
        fn.install_pip_module(self.module_name)
        return {"FINISHED"}

def install_pip_module_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('devtools.install_pip_module', icon='FILE_SCRIPT')

classes = (DEV_OT_install_pip_module,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_help.append(install_pip_module_menu)

def unregister():
    bpy.types.TOPBAR_MT_help.remove(install_pip_module_menu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
