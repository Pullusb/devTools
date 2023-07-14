import bpy
from os.path import join
from pathlib import Path
from . import fn


class DEV_PT_dev_tools(bpy.types.Panel):
    # bl_idname = "DEV_PT_dev_tools"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Dev"
    bl_label = "Dev Tools"

    def draw(self, context):
        layout = self.layout
        row=layout.row()
        row.prop(context.scene, 'line_in_debug_print')
        row.operator('devtools.update_debug_linum', text='', icon='FILE_REFRESH')#Update
        layout.operator('devtools.debug_print_variable')
        layout.label(text="Options")
        layout.prop(context.scene, 'enum_DebugPrint', text='', expand=False)
        layout.separator()


        col = layout.column(align=False)
        col.operator('devtools.time_selection')
        col.operator('devtools.write_classes_tuple')
        col.operator('devtools.expand_shortcut_name')
        col.operator("devtools.create_context_override")

        # When text is saved externally draw more option
        text, _override = fn.get_text(context)
        if text and text.filepath: # mask button if file is pure internal
            col.separator()
            col = layout.column(align=False)
            col.label(text='External File')
            col.operator('devtools.diff_internal_external')
            col.operator('devtools.open_script_folder')
            col.operator('devtools.open_external_editor')

        col = layout.column(align=True)
        col.separator()
        col.label(text='Open Scripts Locations')
        row = col.row(align=True)
        # local default installed addons (release)
        row.operator('devtools.open_filepath', text='Built-in addons').fp = join(bpy.utils.resource_path('LOCAL') , 'scripts', 'addons')

        # Local user addon source (usually appdata roaming)\nWhere it goes when you do an 'install from file'
        row.operator('devtools.open_filepath', text='Users addons').fp = str(Path(bpy.utils.user_resource('SCRIPTS')) / "addons")

        # layout = self.layout
        # common script (if specified)
        preferences = bpy.context.preferences

        if bpy.app.version < (3, 6, 0):
            external_script_dir = preferences.filepaths.script_directory
            if external_script_dir and len(external_script_dir) > 2:
                col.operator('devtools.open_filepath', text='External scripts folder').fp = str(Path(external_script_dir))
        else:
            for s in preferences.filepaths.script_directories:
                if s.directory:
                    col.operator('devtools.open_filepath', text=s.name).fp = str(Path(s.directory))

        ##  standard operator
        # layout.operator("wm.path_open", text='Open config location').filepath = bpy.utils.user_resource('CONFIG')
        layout.operator('devtools.open_filepath', text='Config folder').fp = str(Path(bpy.utils.user_resource('CONFIG')))
        
        ##  layout.operator(DEV_OT_backup_pref.bl_idname, text='backup user prefs')#  in addon prefs

        layout.separator()
        col = layout.column(align=False)

        # path printer
        col.operator('devtools.print_resources_path')

        # infos printer
        row = col.row(align=True)
        row.operator('devtools.insert_date', text='Insert date')
        row.operator('devtools.blender_info', text='Release infos')
        col.separator()
        col.operator('devtools.keypress_tester',)

        # Api explore
        col.separator()
        col.operator('dev.api_search', text='Explore Api', icon='FILE_TEXT')


def register():
    bpy.utils.register_class(DEV_PT_dev_tools)

def unregister():
    bpy.utils.unregister_class(DEV_PT_dev_tools)