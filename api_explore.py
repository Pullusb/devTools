import bpy, mathutils

exclude = (
### add lines here to exclude specific attribute
'bl_rna', 'identifier','name_property','rna_type','properties', 'id_data', 'id_library',#basic

## To avoid recursion/crash on direct object call (comment for API check on deeper props)
'data', 'edges', 'faces', 'edge_keys', 'polygons', 'loops', 'face_maps', 'original',

##  Avoid some specific properties
'CustomShelf', 'context', 'libmv',
#'matrix_local', 'matrix_parent_inverse', 'matrix_basis','location','rotation_euler', 'rotation_quaternion', 'rotation_axis_angle', 'scale', 'translation',
)

## starting with 'id_' ?

class DEV_OT_api_search(bpy.types.Operator):
    bl_idname = "dev.api_search"
    bl_label = "Api Search"
    bl_description = "Explore API in console at specified datapath and return found names"
    bl_options = {"REGISTER"}

    data_path : bpy.props.StringProperty(name='Data Path',
    description='Api data path to start searching in')
    
    dump_api_tree : bpy.props.BoolProperty(name='Dump Tree in Clipboard',
    description='Traverse api at given path and copy into clipboard, else search mode')

    search : bpy.props.StringProperty(name='Search',
    description='Word to search in api paths')

    from_console : bpy.props.BoolProperty(name='From Console', default=False,
    description='Pop a panel', options={'SKIP_SAVE'})

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        if not self.from_console:
            row.activate_init = True # place cursor in field so user can start taping right away
        row.prop(self, 'data_path', text='Data Path')
        
        col.prop(self, 'dump_api_tree', text='Dump Api Tree To Clipboard')
        
        row = col.row()
        row.active = not self.dump_api_tree
        if self.from_console:
            row.activate_init = True # place cursor in field so user can start taping right away
        row.prop(self, 'search', text='Search')

    def list_attr(self, path, ct=0, search_mode=False):
        self.runned.append(path)

        for attr in dir(eval(path)):
            self.looped += 1
            if not attr.startswith('__') and not attr in exclude:
                try:
                    value = getattr(eval(path),attr)
                except AttributeError:
                    value = None

                if value != None:
                    if not callable(value):
                        if type(value) in ( type(0), type(0.0), type(True), type('str'), type(mathutils.Vector()), type(mathutils.Color()), type(mathutils.Matrix()) ):
                            if search_mode:
                                if self.search in attr:
                                    self.found.append(f'{path}.{attr} : {value}')
                                    print(ct*'  ' + attr, value)
                            else:
                                self.found.append(ct*'  ' + f'{attr} : {value}')
                                
                        else:
                            if not search_mode:
                                self.found.append(ct*'  ' + f'{attr} : {value} (type: {type(value)})')
                            ct+=1
                            # recursion
                            self.list_attr('%s.%s'%(path,attr), ct, search_mode=search_mode)

    def execute(self, context):
        self.found = []
        self.runned = []
        self.looped = 0

        dt = self.data_path
        if not dt:
            self.report({'ERROR'}, 'no data path given')
            return {"CANCELLED"}
        
        dt = dt.rstrip('. ')
        self.list_attr(dt, search_mode = not self.dump_api_tree)
        print ('\nDone')
        print('checked', len(self.runned))

        if self.dump_api_tree:
            context.window_manager.clipboard = '\n'.join(self.found)
            self.report({'INFO'}, f'Api elements copied to clipboard')
            # and / or Write on a text data block ?
            return {"FINISHED"}
        
        if self.found:
            self.report({'INFO'}, f'{len(self.found)} elements copied, see console')
            for f in self.found:
                print(f)
            
            context.window_manager.clipboard = '\n'.join(self.found)
            # if self.from_console:
            #     pass # TODO: trigger a panel with insert choice result
            # else:
            #     # Copy to clipboard
            #     context.window_manager.clipboard = '\n'.join(self.found)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(DEV_OT_api_search)

def unregister():
    bpy.utils.unregister_class(DEV_OT_api_search)