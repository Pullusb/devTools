from typing import DefaultDict
import bpy, os, re, fnmatch
import addon_utils
import time
from bpy_extras.io_utils import ExportHelper

import zipfile
from pathlib import Path

from . import fn
from bpy.props import (
                    StringProperty,
                    BoolProperty,
                    EnumProperty,
                    IntProperty,
                    CollectionProperty,
                    )

from bpy.types import (
                    Operator,
                    UIList,
                    PropertyGroup,
                    Panel
                    )


def get_addon_location(fp) -> str:
    '''get addon filepath and return a name of the addon location'''
    # fp = str(Path(fp))
    if fp.startswith( str(Path(bpy.utils.user_resource('SCRIPTS')) / 'addons') ):
        return 'user'

    if fp.startswith( str(Path(bpy.utils.resource_path('LOCAL')) / 'scripts' / 'addons') ):
        return 'native'

    external_scripts = bpy.context.preferences.filepaths.script_directory
    if external_scripts:
        if fp.startswith( str(Path(external_scripts)) ):
            return 'external'

    return 'other'

def get_addons_modules_infos(active_filter="ALL", support_filter='ALL'):
    '''Return a list of tuples ([0] diskpath, [1] bl_info name (with source if conflict), [2] Diskname)
    active_filter in (ALL, ACTIVE, INACTIVE)
    support_filter in (ALL, OFFICIAL, COMMUNITY, TESTING)
    '''

    addon_list = []
    module_list = []
    remodule = re.compile(r"<module '(.*?)' from '(.*?)'>")
    
    for i, m in enumerate(addon_utils.modules()):
        n = m.bl_info.get('name','')

        res = remodule.search(str(m))
        if not res:
            continue
        
        support = m.bl_info.get('support','COMMUNITY') # default is community
        version = m.bl_info.get('version','') # version to string
        if version:
            version = '.'.join([str(i) for i in version])
        else:
            version = ''

        diskname, fp = res.group(1), Path(res.group(2))
        

        if not diskname or not n or not fp:
            continue
        
        ## Filters
        if active_filter != 'ALL':
            installed, current = addon_utils.check(diskname)
            if active_filter == 'ACTIVE' and not current: # (installed or current)
                continue
            elif active_filter == 'INACTIVE' and current: # (installed or current)
                continue

        if support_filter != 'ALL':
            if support != support_filter:
                continue

        # [0] diskpath, [1] bl_info name, [2] Diskname, [3] Support, [4] version
        addon_list.append((str(fp), n, diskname, support, version))
        # module (can access m.bl_info['version']...etc)
        module_list.append(m)

    ## / treat duplicate name (check for infos on conflict)
    # find duplicate indexes
    namelist = [x[1] for x in addon_list]
    dup_index = list(set(i for i, x in enumerate(namelist) if namelist.count(x) > 1))

    # add version and location name
    for idx in dup_index:
        loc = get_addon_location(addon_list[idx][0])
        version = str(module_list[idx].bl_info.get('version', '')).replace(" ", "").strip('()')
        # replace with new tuple
        addon_list[idx] = (addon_list[idx][0], f'{addon_list[idx][1]} ({loc} {version})', addon_list[idx][2], addon_list[idx][3], version)    

    return addon_list

# def get_addon_list(self, context):
#     '''return (identifier, name, description) of enum content'''
#     return get_addons_modules_infos() # self.all_addons_l
#     # return [(i.path, basename(i.path), "") for i in self.blends]

## Manual reloading

def reload_addon_list(self, context):
    scn = context.scene
    pl_prop = scn.devpack_props
    uilist = scn.devpack_props.addon_list
    uilist.clear()
    pl_prop['idx'] = 0 # reset idx to zero

    addon_tuples = get_addons_modules_infos(active_filter=pl_prop.filter_state, support_filter=pl_prop.filter_support)
    # [0] diskpath, [1] bl_info name, [2] Diskname, [3] Support

    for adn in addon_tuples: # populate list
        item = uilist.add()
        # scn.devpack_props['idx'] = len(uilist) - 1 # don't trigger updates
        item.addon_path = adn[0]
        item.name = adn[1]
        item.addon_module = adn[2]
        item.addon_support = adn[3]
        item.addon_version = adn[4]

    scn.devpack_props.idx = len(uilist) - 1 # trigger update

class DEV_OT_reload_addon_list(Operator):
    bl_idname = "dev.reload_addon_list"
    bl_label = "Reload Palette Blends"
    bl_description = "Reload the blends in UI list of palettes linker"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        reload_addon_list(self, context)
        return {"FINISHED"}

#--- UI List

class DEV_UL_addon_list(UIList):

    show_diskname : BoolProperty(name="Show Diskname", default=False,
    description="display diskname (containing folder name) in additional column")

    show_version : BoolProperty(name="Show Version", default=False,
    description="display version in additional column")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # self.use_filter_show = True # force open the search feature
        row = layout.row(align=True)
        row.prop(item, 'select', text='')
        row.label(text=item.name)
        if self.show_diskname:
            row.label(text=item.addon_module)
        if self.show_version:
            row.label(text=item.addon_version)
        row.operator('dev.open_element_in_os', text='', icon='FILE_FOLDER').filepath = item.addon_path

    def draw_filter(self, context, layout):
        row = layout.row()
        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="") # Only show items matching this name (use ‘*’ as wildcard)

        # reverse order
        subrow.prop(self, "show_diskname", text="", icon='SYNTAX_OFF') # built-in reverse
        subrow.prop(self, "show_version", text="", icon='QUESTION') # built-in reverse
        icon = 'SORT_DESC' if self.use_filter_sort_reverse else 'SORT_ASC'
        subrow.prop(self, "use_filter_sort_reverse", text="", icon=icon) # built-in reverse

    def filter_items(self, context, data, propname):
        collec = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name.lower(), self.bitflag_filter_item, collec, "name",
                                                          reverse=self.use_filter_sort_reverse)#self.use_filter_name_reverse)
        return flt_flags, flt_neworder

#--- PROPERTIES

class DEV_PG_addon_prop(PropertyGroup):
    name : StringProperty() # name
    addon_module : StringProperty() # folder/file name
    addon_path : StringProperty() # full path
    addon_support : StringProperty() # support in official
    addon_version : StringProperty() # version number
    select : BoolProperty(default=False)

# def do_something(self, context):
#     pl_prop = context.scene.devpack_props
#     blend_uil = pl_prop.addon_list
#     print(f"index is now {pl_prop['idx']} on {len(blend_uil)} elements")

class DEV_PG_addon_list_props(PropertyGroup):
    ## UI list
    idx : IntProperty() # update=do_something update_on_index_change to reload object
    addon_list : CollectionProperty(type=DEV_PG_addon_prop)

    filter_support : EnumProperty(name='Support Filter',
        default='ALL',
        items=(
            ('ALL', 'All', 'Show all addons'),
            ('OFFICIAL', 'Official', 'Official addons only'),
            ('COMMUNITY', 'Community', 'Community addons'),
            ('TESTING', 'Testing', 'Testing support addons'),
        ),
        update=reload_addon_list,
    )
    
    filter_state : EnumProperty(name='State Filter',
        default='ALL',
        items=(
            ('ALL', 'All', 'Both enabled and disabled addons'),
            ('ACTIVE', 'Active', 'Only enabled addons'),
            ('INACTIVE', 'Inactive', 'Only disabled addons'),
        ),
        update=reload_addon_list,
    ) # Or use export helper
    # Other props
    
    # export_path : BoolProperty() # Or use export helper


#--- PANEL

class DEV_PT_addon_list_ui(Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Dev"
    bl_label = "Addon List"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        pl_prop = context.scene.devpack_props
        col= layout.column()
        row=col.row()

        # refresh button above
        # row.label(text='Blends in folder')
        # row.operator("dev.reload_addon_list", icon="FILE_REFRESH", text="")

        col= layout.column()
        row = col.row()
        row.prop(pl_prop, 'filter_support', expand=True)
        row = col.row()
        row.prop(pl_prop, 'filter_state', expand=True)
        row = col.row()

        minimum_row = 5 # default number of line showes
        row.template_list("DEV_UL_addon_list", "", pl_prop, "addon_list", pl_prop, "idx", 
            rows=minimum_row)

        # refresh button above in UIlist right side
        subcol = row.column(align=True)
        subcol.operator("dev.reload_addon_list", icon="FILE_REFRESH", text="")
        
        col.label(text=f'{len([a for a in pl_prop.addon_list if a.select])}/{len(pl_prop.addon_list)} Selected')

        col.operator("dev.open_addon_prefs", icon="PREFERENCES", text="Open Active Prefs")
        
        col.separator()
        col.operator("dev.export_addon_zip_pack", icon="FILE_ARCHIVE", text="Export Addon Pack As Zip")
        col.operator("dev.print_addon_list", icon="CONSOLE", text="Print Selected Infos")
        
        ## problem with batch enable. internal targeted addons __name__ variable seem to be wrong when enabling from here
        # col.operator("dev.toggle_marked_addons", icon="CHECKBOX_HLT", text="Batch Enable addons").enable = True
        col.operator("dev.toggle_marked_addons", icon="CHECKBOX_DEHLT", text="Batch Disable addons").enable = False

#--- ACTION OPS

class DEV_OT_print_addon_list(Operator):
    bl_idname = "dev.print_addon_list"
    bl_label = "Print Selected list"
    bl_description = "Print Selected list in console"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        print('\nSelected addons:')
        pl_prop = context.scene.devpack_props.addon_list
        for ad in pl_prop:
            if not ad.select:
                continue
            print(ad.name)
            print(ad.addon_version)
            print(ad.addon_module)
            print(ad.addon_path)
            print(ad.addon_support)
            print()
        return {"FINISHED"}

class DEV_OT_export_addon_zip_pack(Operator, ExportHelper):
    bl_idname = "dev.export_addon_zip_pack"
    bl_label = "Export As Zip Pack"
    bl_description = "Export selected addons as zip pack with custom filters"
    # bl_options = {"REGISTER", "INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     return context.object and context.object.type == 'GPENCIL'

    filter_glob: StringProperty(default='*.zip', options={'HIDDEN'}) #*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp
    
    filename_ext = '.zip'

    filepath : StringProperty(
        name="File Path",
        # default='addon_pack.zip',
        description="File path used for export", 
        maxlen= 1024)

    exclude_git_files : BoolProperty(
        name='Exclude Git files',
        description='Add following to exclude filter: [.git, *.pyc, .gitignore]',
        default=True,
        )

    exclude_filter : StringProperty(
        name='Exclude', 
        default='',
        description='Exclusion filter (dirs and files) to avoid zipping some items (can use *wildcards)\nex: *.blend, badname, *.md\nNote: you can set permanent exclusions filter in preferences'
        )

    include_filter : StringProperty(
        name='Include', 
        default='',
        description='Include only file matching this comma separated rules (can use *wildcard)\nex: *py, *.md\nnote: exclusion filter is executed before'
        )

    compressed : BoolProperty(
        name='Compressed Zip',
        description='Choose if zip is made in compress mode or store mode',
        default=True)

    def invoke(self, context, event):
        self.filepath = f'//addon_pack-{time.strftime("%Y_%m_%d")}.zip' # with date: 2022_01_28
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        prefs = fn.get_addon_prefs()
        pl_prop = context.scene.devpack_props
        ad_list = pl_prop.addon_list
        # pathes = [Path(ad.addon_path) for ad in ad_list if ad.select]
        pathes = []
        print('Packing')
        for ad in ad_list:
            if ad.select:
                if ad.addon_path.endswith('__init__.py'):
                    pathes.append(Path(ad.addon_path).parent)
                else:
                    pathes.append(Path(ad.addon_path))
                print(f'- {ad.name} ({ad.addon_module})')

        ## pathes to addon.py for single file and __init__.py on mutilfile
        if not pathes:
            self.report({'ERROR'}, f'Nothing to zip')
            return {"CANCELLED"}


        ## list addon path to zip
        includes = []
        excludes = []
        if self.include_filter:
            includes = [i.strip() for i in self.include_filter.split(',')] # ['*.doc', '*.odt'] # for files only
        if self.exclude_filter:
            excludes = [i.strip() for i in self.exclude_filter.split(',')] # for dirs and files

        if self.exclude_git_files:
            excludes += ['.git', '*.pyc', '.gitignore']

        # add preferences exclusions
        if prefs.devtool_addonpack_exclude:
            permanent_exclude = [i.strip() for i in prefs.devtool_addonpack_exclude.split(',')]
            excludes += permanent_exclude
            excludes = list(set(excludes))

        # replace by regex translation
        if includes:
            includes = r'|'.join([fnmatch.translate(x) for x in includes])
        if excludes:
            excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'

        arc_root_dir =  'addons/'
        
        compress_type = zipfile.ZIP_DEFLATED if self.compressed else zipfile.ZIP_STORED
        with zipfile.ZipFile(self.filepath, 'w',compress_type) as zipObj:        
            for fp in pathes:
                if not fp.exists():
                    print(f'Not exists: {fp.name}')
                    continue
                
                if fp.is_file():
                    arcname = arc_root_dir + fp.name
                    print(f'adding: {arcname}')
                    zipObj.write(str(fp), arcname)
                
                else: # Zip addon structure
                    start = fp.parent.as_posix()
                    # BONUS option: Also respect .gitignore if any
                    for root, dirs, files in os.walk(str(fp)):
                        # exclude dirs
                        if excludes:
                            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
                        
                        # exclude/include files
                        if excludes:
                            files = [f for f in files if not re.match(excludes, f)]
                        
                        if includes:
                            files = [f for f in files if re.match(includes, f)]

                        for fname in files:
                            full_path = Path(root) / fname
                            # remove head start in path
                            arcname = full_path.as_posix().replace(start, '').lstrip('/')
                            arcname = arc_root_dir + arcname
                            # if not '.git/' in arcname and not '__pycache__' in arcname :
                            #     # don't print all git and cache stuff
                            #     print(f'adding: {arcname}')
                            print(f'adding: {arcname}')
                            zipObj.write(str(full_path), arcname)
                print()
        print('End of pack')
        self.report({'INFO'}, f'Zip saved at: {self.filepath}')
        return {"FINISHED"}


class DEV_OT_toggle_marked_addons(Operator):
    bl_idname = "dev.toggle_marked_addons"
    bl_label = "Enable Addons"
    bl_description = "Enable marked addon in list"
    bl_options = {"REGISTER", "INTERNAL"}

    enable : BoolProperty(options={'SKIP_SAVE'})

    def execute(self, context):
        pl_prop = context.scene.devpack_props.addon_list
        for ad in pl_prop:
            if not ad.select:
                continue
            if self.enable:
                print(f'Enabling {ad.name} -> {ad.addon_module}')
                addon_utils.enable(ad.addon_module)
            else:
                print(f'Disabling {ad.name} -> {ad.addon_module}')
                addon_utils.disable(ad.addon_module)

        return {"FINISHED"}

def open_addon_prefs_by_name(name='', module=''):
    '''Open addon prefs windows with focus on current addon'''
    if not name:
        print('error: in open_addon_prefs_by_name : No name specified')
        return
    # from .__init__ import bl_info
    wm = bpy.context.window_manager
    wm.addon_filter = 'All'
    if not 'COMMUNITY' in  wm.addon_support: # reactivate community
        wm.addon_support = set([i for i in wm.addon_support] + ['COMMUNITY'])
    wm.addon_search = name
    bpy.context.preferences.active_section = 'ADDONS'
    if module:
        bpy.ops.preferences.addon_expand(module=module)
    bpy.ops.screen.userpref_show('INVOKE_DEFAULT')

class DEV_OT_open_addon_prefs(Operator):
    bl_idname = "dev.open_addon_prefs"
    bl_label = "Open Addon Prefs"
    bl_description = "Open user preferences window in addon tab and prefill the search with addon name"
    bl_options = {"REGISTER", 'INTERNAL'}

    # name : StringProperty(options={'SKIP_SAVE'})
    # module : StringProperty(options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.scene.devpack_props.addon_list

    def execute(self, context):
        pr = context.scene.devpack_props
        # if not len(pr.addon_list):
        #     self.report({'ERROR'}, 'No items')
        #     return {'CANCELLED'}
        ad = pr.addon_list[pr.idx]
        open_addon_prefs_by_name(name=ad.name, module=ad.addon_module)
        return {'FINISHED'}

classes = (
# action ops
DEV_OT_toggle_marked_addons,
DEV_OT_open_addon_prefs,
DEV_OT_print_addon_list,
DEV_OT_export_addon_zip_pack,

# addon list
DEV_OT_reload_addon_list,
DEV_PG_addon_prop,
DEV_UL_addon_list,

# prop containing the one above
DEV_PG_addon_list_props,
DEV_PT_addon_list_ui,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.devpack_props = bpy.props.PointerProperty(type=DEV_PG_addon_list_props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.devpack_props

if __name__ == "__main__":
    register()
