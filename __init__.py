bl_info = {
    "name": "dev tools",
    "description": "Add tools in text editor and console to help development",
    "author": "Samuel Bernou",
    "version": (2, 2, 1),
    "blender": (3, 0, 0),
    "location": "Text editor > toolbar and console header",
    "warning": "",
    "doc_url": "https://github.com/Pullusb/devTools",
    "tracker_url": "https://github.com/Pullusb/devTools/issues",
    "category": "Text Editor" }

import bpy
import os
import re
import difflib
import subprocess
from sys import platform
from time import strftime
from pathlib import Path

from . import fn
from . import addon_listing
from . import openers
from . import error_handle
from . import api_explore
from . import console_ops
from . import ui

###---UTILITY funcs

def copy_selected(context):
    '''check for selection and not clipboard.
    more secure and possible to do more stufs around selection
    '''
    
    text = context.space_data.text
    current_line = text.current_line
    select_end_line = text.select_end_line

    current_character = text.current_character
    select_end_character = text.select_end_character

    # if there is no selected text return None
    if current_line == select_end_line:
        if current_character == select_end_character:
            return None
        else:
            return current_line.body[min(current_character, select_end_character):max(current_character, select_end_character)]

    text_return = None
    writing = False
    normal_order = True  # selection from top to bottom

    for line in text.lines:
        if not writing:
            if line == current_line:
                text_return = current_line.body[current_character:] + "\n"
                writing = True
                continue
            elif line == select_end_line:
                text_return = select_end_line.body[select_end_character:] + "\n"
                writing = True
                normal_order = False
                continue
        else:
            if normal_order:
                if line == select_end_line:
                    text_return += select_end_line.body[:select_end_character]
                    break
                else:
                    text_return += line.body + "\n"
                    continue
            else:
                if line == current_line:
                    text_return += current_line.body[:current_character]
                    break
                else:
                    text_return += line.body + "\n"
                    continue

    return text_return


def print_string_variable(clip,linum=''):
    if linum:
        line = 'print(":l {1}:{0}", {0})#Dbg'.format(clip, str(linum) )
        ## f-string '=' syntax
        # line = 'print(f":l {1}: {{{0}=}}")#Dbg'.format(clip, str(linum) )
    else:
        line = 'print("{0}", {0})#Dbg'.format(clip)
        ## f-string '=' syntax
        # line = 'print(f"{{{0}=}}")#Dbg'.format(clip)
    #'print("'+ clip + '", ' + clip + ')#Dbg'
    return (line)


def fix_indentation(Loaded_text, charPos):
    '''take text and return it indented according to cursor position'''

    FormattedText = Loaded_text
    # print("FormattedText", FormattedText)#Dbg
    if charPos > 0:
        textLines = Loaded_text.split('\n')
        if not len(textLines) == 1:
            #print("indent subsequent lines")
            indentedLines = []
            indentedLines.append(textLines[0])
            for line in textLines[1:]:
                indentedLines.append(' '*charPos + line)

            FormattedText = '\n'.join(indentedLines)
        else:
            FormattedText = ' '*charPos + FormattedText

    return (FormattedText)


def re_split_line(line):
    '''
    take a line string and return a 3 element list:
    [ heading spaces (id any), '# '(if any), rest ot the string ]
    '''
    r = re.search(r'^(\s*)(#*\s?)(.*)', line)
    return ( [r.group(1), r.group(2), r.group(3)] )

    
def update_enum_DebugPrint(self, context):

    eval('bpy.ops.%s()' % self.enum_DebugPrint)


###---TASKS

class DEV_OT_simple_print(bpy.types.Operator):
    bl_idname = "devtools.simple_print"
    bl_label = "Simple Print Text"
    bl_description = "Add a new line with debug print of selected text\n(replace clipboard)"
    bl_options = {"REGISTER"}

    quote: bpy.props.BoolProperty()
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        #get current text object
        text, override = fn.get_text(context)

        #create debug print from variable selection
        # charPos = text.current_character
        clip = copy_selected(context)
   
        if clip is None: #copy word under cursor
            bpy.ops.text.select_word()
            try:  #if nothing under cursor. paste what is in clipboard
                clip = copy_selected(context)
                assert clip is not None
            except AssertionError:
                clip = bpy.context.window_manager.clipboard

        if self.quote:
            debugPrint = f'print("{clip}")' #'print({0})#Dbg'
        else:
            debugPrint = f'print({clip})' #'print({0})#Dbg'

        ###On a new line
        # heading_spaces = re.search('^(\s*).*', text.current_line.body).group(1)
        # new = fix_indentation(debugPrint, len(heading_spaces))#to insert at selection level : charPos
        # bpy.ops.text.move(override, type='LINE_END')
        # bpy.ops.text.insert(override, text= '\n'+new)

        ### In place
        bpy.ops.text.insert(override, text=debugPrint)
        return {"FINISHED"}


class DEV_OT_quote(bpy.types.Operator):
    bl_idname = "devtools.quote"
    bl_label = "Quote Text"
    bl_description = "quote text"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = fn.get_text(context)
        # charPos = text.current_character
        clip = copy_selected()
   
        if clip is None: #copy word under cursor
            bpy.ops.text.select_word()
            try:  #if nothing under cursor. paste what is in clipboard
                clip = copy_selected(context)
                assert clip is not None
            except AssertionError:
                clip = bpy.context.window_manager.clipboard

        if '"' in clip:
            debugPrint = "'{0}'".format(clip)#'print({0})#Dbg'
        else:
            debugPrint = '"{0}"'.format(clip)

        ###On a new line
        # heading_spaces = re.search('^(\s*).*', text.current_line.body).group(1)
        # new = fix_indentation(debugPrint, len(heading_spaces))#to insert at selection level : charPos
        # bpy.ops.text.move(override, type='LINE_END')
        # bpy.ops.text.insert(override, text= '\n'+new)

        ### In place
        bpy.ops.text.insert(override, text=debugPrint)
        return {"FINISHED"}


class DEV_OT_insert_import(bpy.types.Operator):
    bl_idname = "devtools.insert_import"
    bl_label = "Insert Import Text"
    bl_description = "import text"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = fn.get_text(context)
        #create new text-block if not any
        if text == None:
            text = bpy.data.texts.new('Text')
            context.space_data.text = text
            text, override = fn.get_text(context)#reget_override
        charPos = text.current_character
        #clip = copy_selected()
        header_file = Path(__file__).with_name('imports.txt')
        if not header_file.exists():
            self.report({'ERROR'}, f'imports.txt not found in addon folder! path used : {header_file}')
            return {"CANCELLED"}
        
        import_text = header_file.read_text()

        bpy.ops.text.insert(override, text=import_text)

        ### Toggling coding space data basic feature
        # TODO (add box in pref to choose basic behavior)
        context.space_data.show_line_numbers = True
        context.space_data.show_syntax_highlight = True
        #context.space_data.show_line_highlight = True
        return {"FINISHED"}


class DEV_OT_debug_print_variable(bpy.types.Operator):
    bl_idname = "devtools.debug_print_variable"
    bl_label = "Debug Print Variable"
    bl_description = "add a new line with debug print of selected text\n(replace clipboard)"
    bl_options = {"REGISTER"}

    bpy.types.Scene.line_in_debug_print = bpy.props.BoolProperty(
    name="include line num", description='include line number in print', default=False)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        #get current text object
        text, override = fn.get_text(context)

        #create debug print from variable selection
        charPos = text.current_character
        clip = copy_selected(context)
   
        if clip is None: #copy word under cursor
            bpy.ops.text.select_word()
            try:  #if nothing under cursor. paste what is in clipboard
                clip = copy_selected(context)
                assert clip is not None
            except AssertionError:
                clip = bpy.context.window_manager.clipboard

        if bpy.context.scene.line_in_debug_print:
            debugPrint = print_string_variable(clip, linum=text.current_line_index+1)
        else:
            debugPrint = print_string_variable(clip)

        #send charpos at current indentation (number of whitespace)
        heading_spaces = re.search('^(\s*).*', text.current_line.body).group(1)

        new = fix_indentation(debugPrint, len(heading_spaces))#to insert at selection level : charPos

        #got to end of line,
        ### > current_character" from "Text" is read-only
        #text.current_character = len(text.lines[text.current_line_index].body)
        bpy.ops.text.move(override, type='LINE_END')

        #put a return and paste with indentation
        bpy.ops.text.insert(override, text= '\n'+new)
        return {"FINISHED"}
        

class DEV_OT_delete_all_debug_print(bpy.types.Operator):
    bl_idname = "devtools.delete_all_debug_print"
    bl_label = "Delete All Debug Print"
    bl_description = "Delete all debug print"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR' #not really necessary the menu is there...
        
    def execute(self, context):
        text, _override = fn.get_text(context)
        count = 0
        for i, lineOb in enumerate(text.lines):
            if lineOb.body.endswith('#Dbg'):#detect debug lines
                lineOb.body = ""

        return {"FINISHED"}


class DEV_OT_disable_all_debug_print(bpy.types.Operator):
    bl_idname = "devtools.disable_all_debug_print"
    bl_label = "Disable All Debug Print"
    bl_description = "comment all lines finishing with '#Dbg'"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, _override = fn.get_text(context)
        count = 0
        for i, lineOb in enumerate(text.lines):
            if lineOb.body.endswith('#Dbg'):#detect debug lines
                line = lineOb.body
                splitline = re_split_line(line)
                if not splitline[1]: #detect comment
                    count += 1
                    lineOb.body = splitline[0] + '# ' +  splitline[2]
                    print ('line {} commented'.format(i))
        if count:
            mess = str(count) + ' lines commented'
        else:
            mess = 'No line commented'
        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_enable_all_debug_print(bpy.types.Operator):
    bl_idname = "devtools.enable_all_debug_print"
    bl_label = "Enable All Debug Print"
    bl_description = "uncomment all lines finishing wih '#Dbg'"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, _override = fn.get_text(context)
        count = 0
        for i, lineOb in enumerate(text.lines):
            if lineOb.body.endswith('#Dbg'):#detect debug lines
                line = lineOb.body
                splitline = re_split_line(line)
                if splitline[1]: #detect comment
                    count += 1
                    lineOb.body = splitline[0] + splitline[2]
                    print ('line {} uncommented'.format(i))
        if count:
            mess = str(count) + ' lines uncommented'
        else:
            mess = 'No line uncommented'
        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_time_selection(bpy.types.Operator):
    bl_idname = "devtools.time_selection"
    bl_label = "Time Selected Code"
    bl_description = "add time prints around selection\n add import if necessary" 
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        #get current text object
        text, _override = fn.get_text(context)

        ### -/ add time import (if needed)

        #re_time_method = re.compile(r'from time import time')
        need_import = True
        for l in text.lines:
            if l.body.startswith('from time import time'): #re_time_method.match(l.body):
                need_import = False
                continue

        line_num=None
        if need_import:
            special_import = 'from time import time#Dbg-time'
            has_import = False
            for i, l in enumerate(text.lines):
                if l.body.startswith(('import ', 'from ')):
                    has_import = True
                else:
                    if has_import:
                        line_num = i
                        break

            if not has_import:
                line_num = 0
            
            #INSERT line with special_import at line_num
            text.lines[line_num].body = special_import + '\n' + text.lines[line_num].body
        #time import end /-

        charPos = text.current_character
        #get line index of selection (always in right order) only one element if not multiline
        select_range = [i for i, l in enumerate(text.lines) if l == text.current_line or l == text.select_end_line]
        start_id, end_id = select_range[0], select_range[-1]
        
        start_timer = r'start = time()#Dbg-time'

        end_timer = 'print("l{}-l{} exec time:", time() - start)#Dbg-time'.format(start_id+2, end_id+2)
        if start_id == end_id:
            end_timer = 'print("l{} exec time:", time() - start)#Dbg-time'.format(start_id+2)

        start_line = text.lines[start_id]
        end_line = text.lines[end_id]# +1 get line after to insert #OUT OF RANGE IF LAST LINE !

        heading_spaces = re.search(r'^(\s*).*', start_line.body).group(1)
        
        ### https://docs.blender.org/api/current/bpy.ops.text.html?highlight=bpy%20ops%20text%20move#bpy.ops.text.move_select

        ## add start timer
        new = fix_indentation(start_timer, len(heading_spaces))

        # start_line.body = new + '\n' + start_line.body# not working (add \n as unknown sqaure character)
        bpy.ops.text.jump(line=start_id+1)
        bpy.ops.text.move(type='LINE_BEGIN')
        text.write(new+'\n')

        
        ## add end timer
        new = fix_indentation(end_timer, len(heading_spaces))
        # end_line.body = new + '\n' + end_line.body# not working (add \n as unknown sqaure character)
        bpy.ops.text.jump(line=end_id+2)
        bpy.ops.text.move(type='LINE_END')
        text.write('\n'+new)

        #got to end of line,
        #text.current_character = len(text.lines[text.current_line_index].body)
        #bpy.ops.text.move(override, type='LINE_END')

        #Put a return and paste with indentation
        #bpy.ops.text.insert(override, text= '\n'+new)
        return {"FINISHED"}


class DEV_OT_expand_shortcut_name(bpy.types.Operator):
    bl_idname = "devtools.expand_shortcut_name"
    bl_label = "Expand Text Shortcuts"
    bl_description = "replace 'C.etc' by 'bpy.context.etc'\n and 'D.etc' by 'bpy.data.etc'"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = fn.get_text(context)
        rxc = re.compile(r'C(?=\.)')#(?<=[^A-Za-z0-9\.])C(?=\.)
        rxd = re.compile(r'D(?=\.)')#(?<=[^A-Za-z0-9\.])D(?=\.)
        for line in text.lines:
            line.body = rxc.sub('bpy.context', line.body)
            line.body = rxd.sub('bpy.data', line.body)

        return {"FINISHED"}


class DEV_OT_update_debug_linum(bpy.types.Operator):
    bl_idname = "devtools.update_debug_linum"
    bl_label = "Update_Debug Linum"
    bl_description = "update number in debug prints that are using linum print"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, _override = fn.get_text(context)
        relinum = re.compile(r'(print\(\":l) \d+(:)')
        renum = re.compile(r'print\(\":l (\d+):')
        #match element: .*print:l 12:.*
        ct = 0
        for i, line in enumerate(text.lines):
            match = relinum.search(line.body)
            if match:
                newnum = str(i)
                num = renum.search(line.body).group(1)
                if newnum != num:
                    #print('linum updated at line:', i)
                    pattern = r'\1 {}\2'.format(newnum)
                    line.body = relinum.sub(pattern, line.body)
                    ct+=1
        if ct:
            mess = str(ct) + ' print updated'
            self.report({'INFO'}, mess)
        else:
            self.report({'INFO'}, 'All good')

        return {"FINISHED"}


class DEV_OT_write_classes_tuple(bpy.types.Operator):
    bl_idname = "devtools.write_classes_tuple"
    bl_label = "Write Classes Tuple"
    bl_description = "Write a classes tuple containing all class in text"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, _override = fn.get_text(context)

        block = 'classes = (\n'
        for line in text.lines:
            if line.body.startswith('class '):
                block += '{},\n'.format(re.search(r'class (.*)\(.*', line.body).group(1))
        block += ')'
        text.write(block)

        return {"FINISHED"}


class DEV_OT_text_diff(bpy.types.Operator):
    bl_idname = "devtools.diff_internal_external"
    bl_label = "Text Diff External"
    bl_description = "print dif in console with the difference between current internal file and external saved version"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = fn.get_text(context)
        if text.filepath:
            if text.is_dirty or text.is_modified:
                print(8*'- ')

                internal = [l.body for l in text.lines]#get line from internal
                fp = text.filepath
                #print("text-filepath", fp)#Dbg
                fp = bpy.path.abspath(fp)
                #print("abs_path", fp)#Dbg
                with open(fp, 'r') as fd:
                    ext = fd.read().splitlines()

                changes = difflib.context_diff(internal,ext,fromfile='local', tofile='external')
                #changes = difflib.unified_diff(internal,ext)

                #print(linecount)
                print (str((len(internal))) + ' internal\n' + str((len(ext))) + ' external\n')

                if [c for c in changes]:#if diff generator  is not empty
                    for change in changes:
                        if not change.startswith(' '):
                            print(change)
                    mess = 'look the diff in console'
                else:
                    mess = 'no diff detected'
            else:
                mess = 'file is synced'

        else:
            mess = 'text is internal only'

        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_print_resources_paths(bpy.types.Operator):
    bl_idname = "devtools.print_resources_path"
    bl_label = "Print Ressources Filepath"
    bl_description = "Print usefull resources filepath in console"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        linesep = 10*'-'
        
        lines = []
        lines.append(linesep)
        lines.append('Ressources path'.upper())
        lines.append(linesep)
        lines.append(f"Local default installed addons (release):\n{os.path.join(bpy.utils.resource_path('LOCAL') , 'scripts', 'addons')}\n")
        lines.append('Local user addon source (usually appdata roaming)\n# Destination of "install from file":\n{}\n'.format(Path(bpy.utils.user_resource('SCRIPTS')) / 'addons') )

        preferences = bpy.context.preferences
        external_script_dir = preferences.filepaths.script_directory
        if external_script_dir and len(external_script_dir) > 2:
            lines.append(f'External scripts:\n{external_script_dir}\n')

        #config
        lines.append(f"Config path:\n{bpy.utils.user_resource('CONFIG')}\n")
        #binary path
        lines.append(f'Binary path:\n{bpy.app.binary_path}\n')

        lines.append(linesep)
        lines.append('')

        content = '\n'.join(lines)
        print(content)

        text, _override = fn.get_text(context)
        if text is None:
            text = bpy.data.texts.new('Resources paths')
            context.space_data.text = text
        
        if text.current_character > 0:
            # add a line return
            content = '\n' + content 
        text.write(content)
        
        # mess = 'Look in console'
        # self.report({'INFO'}, mess)
        return {"FINISHED"}

class DEV_OT_insert_date(bpy.types.Operator):
    bl_idname = "devtools.insert_date"
    bl_label = "Insert Date String"
    bl_description = "Insert date at current position (reclick to add details)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = fn.get_text(context)
        #create new text-block if not any
        if text == None:
            text = bpy.data.texts.new('Text')
            context.space_data.text = text
            text, override = fn.get_text(context)#reget_override

        content = strftime('%Y/%m/%d')
        #if current_line
        print( strftime('---date---\n%c\n%A %B') )
        if re.search(r'\d{4}/\d{2}/\d{2}.*\d{2}:\d{2}:\d{2}.*[A-Z]{1}[a-z]{2}', text.current_line.body):#full
            self.report({'ERROR'}, 'detected as full date')#or just pass...
            return {"CANCELLED"}
        elif re.search(r'\d{4}/\d{2}/\d{2}.*\d{2}:\d{2}:\d{2}', text.current_line.body):
            content = strftime(' %a')#abreviated month
        elif re.search(r'\d{4}/\d{2}/\d{2}', text.current_line.body):
            content = strftime(' %H:%M:%S')#add hours
        else:
            content = strftime('%Y/%m/%d')#date

        ## print detailed version -> %c: full detailed, %A %B full month and day
        bpy.ops.text.insert(override, text=content)
        return {"FINISHED"}


class DEV_OT_blender_info(bpy.types.Operator):
    bl_idname = "devtools.blender_info"
    bl_label = "Blender Infos"
    bl_description = "Insert blender release info (Date, Hash, branch).\nUsefull for bug report"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'
    
    def strip_b_str(self, s):
        if str(s).startswith("b'"):
            #is a byte string
            return s.decode()# decode to classic utf8
            #return str(s)[2:-1]# rural method
        else:
            return s

    def execute(self, context):
        text, override = fn.get_text(context)
        if text == None:
            text = bpy.data.texts.new('Text')
            context.space_data.text = text
            text, override = fn.get_text(context)

        build_text = "Date : {}\nHash : {}\nBranch : {}\nVersion: {}".format(\
        self.strip_b_str(bpy.app.build_date), self.strip_b_str(bpy.app.build_hash), self.strip_b_str(bpy.app.build_branch), bpy.app.version_string)

        bpy.ops.text.insert(override, text=build_text)

        #print in console
        print('\n---Full build infos---')
        for attr in dir(eval("bpy.app")):
            if attr.startswith('build'):
                print(attr)
                try:
                    value = str(getattr(eval("bpy.app"),attr))
                    print(self.strip_b_str(value) )
                    print()
                except AttributeError:
                    print('! ERROR !\n')

        print('--------\nMinimal infos:\n'+build_text+'\n------\n')
        self.report({'INFO'}, 'Full info Printed in console')
        return {"FINISHED"}


class DEV_OT_key_printer(bpy.types.Operator):
    bl_idname = "devtools.keypress_tester"
    bl_label = "Key Event Tester"
    bl_description = "Any key event name will be printed in console (press ESC to stop modal)\nCtrl + Click: copy name to clipboard "
    bl_options = {"REGISTER", "UNDO"}

    def modal(self, context, event):

        ### /TESTER - keycode printer (flood console but usefull to know a keycode name)
        if event.type not in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER_REPORT'}:# , 'LEFTMOUSE'# avoid flood of mouse move.
            print('key:', event.type, 'value:', event.value)
            if event.value == 'PRESS': 
                self.report({'INFO'}, event.type)
                if self.copy_key:
                    context.window_manager.clipboard = f"'{event.type}'" # quoted
        ###  TESTER/

        ### /AREA INFOS
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                print('-=-')
                screen = context.window.screen       
                for i,a in enumerate(screen.areas):
                    if (a.x < event.mouse_x < a.x + a.width
                    and a.y < event.mouse_y < a.y + a.height):
                        print("Clicked in %s area of screen %s" % (a.type, screen.name))
                        print(f'Area size {a.width}x{a.height} (corner {a.x},{a.y})')
                        print(f'mouse click {event.mouse_x}x{event.mouse_y}')
                print('-=-')
        ### AREA INFOS/

        # QUIT
        if event.type in {'ESC'}:#'RIGHTMOUSE',            
            print('--- STOPPED ---')#Dbg
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        ## Starts the modal
        self.copy_key = event.ctrl
        print('\n--- KEYCODE PRINT STARTED -- press ESC to stop---')#Dbg
        self.report({'INFO'}, 'keycode print started (ESC to stop), see console for details')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class DEV_OT_create_context_override(bpy.types.Operator):
    bl_idname = "devtools.create_context_override"
    bl_label = "Context Override"
    bl_description = "Create a context override function for text editor (quick inline in console) in related to clicked area\n(shift+clic to insert in clipboard)"
    bl_options = {"REGISTER", "INTERNAL"}

    def invoke(self, context, event):
        self.override = {'screen':context.window.screen, 'area': context.area}
        self.is_console = True if context.area.type == 'CONSOLE' else False
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set("PICK_AREA")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            screen = context.window.screen       
            for i, a in enumerate(screen.areas):
                if (a.x < event.mouse_x < a.x + a.width
                and a.y < event.mouse_y < a.y + a.height):
                    print(f"Left Clicked in screen {screen.name} area of {a.type} (coordinate {event.mouse_x}x{event.mouse_y})")

                    if self.is_console:# launched from console
                        access = f"override = {{'screen': C.window.screen, 'area': C.window.screen.areas[{i}]}}"
                        print(access)
                        if event.shift:# <- Shift click condition to paper clip
                            context.window_manager.clipboard = access
                        else:
                            bpy.ops.console.clear_line(self.override) # clear line
                            bpy.ops.console.insert(self.override, text=access)
                    
                    else:# launched from text editor
                    
                        ## Generate override function
                        access = f'''def get_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == '{a.type}':
                #for region in area.regions:
                #    if region.type == 'WINDOW':
                return {{'window': window, 'screen': screen, 'area': area}}#, 'region': region
'''                     
                        if event.shift:# <- Shift click condition to paper clip
                            context.window_manager.clipboard = access
                        else:
                            bpy.ops.text.insert(self.override, text= '\n'+access)

                    self.report({'INFO'}, f'Screen {screen.name} area of {a.type} index {i}')#WARNING, ERROR
                    break    
            
            context.window.cursor_set("DEFAULT")
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_set("DEFAULT")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}



class DEV_OT_backup_pref(bpy.types.Operator):
    bl_idname = "devtools.backup_prefs"
    bl_label = "Backup User Preferences"
    bl_description = "Backup user preferences in a subfolder of user config (also backup startup file)\nOpen folder after backup"
    bl_options = {"REGISTER"}

    def execute(self, context):
        config = Path(bpy.utils.user_resource('CONFIG'))
        mypref = config / 'userpref.blend'
        mystartup = config / 'startup.blend'

        if not mypref.exists():
            self.report({'ERROR'}, 'No pref found to backup')
            return {"CANCELLED"}

        backup_main_folder = config / 'userpref_backups'
        
        # timestamp on file : strftime('userpref_%Y-%m-%d_%H-%M-%S.blend')
        timestamp = strftime('%Y-%m-%d_%H-%M-%S')
        backup = backup_main_folder / timestamp
        backup.mkdir(parents=True, exist_ok=True)

        import shutil
        shutil.copy(mypref, backup)

        fn.open_folder(str(backup))

        if mystartup.exists():
            shutil.copy(mystartup, backup)
            
        self.report({'INFO'}, f'Pref backup at {backup}')
        return {"FINISHED"}

class DEV_OT_open_element_in_os(bpy.types.Operator):
    bl_idname = "dev.open_element_in_os"
    bl_label = "Open Element"
    bl_description = "Open location\nCtrl: Copy path\nAlt: Copy module name"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath : bpy.props.StringProperty()

    def invoke(self, context, event):
        self.ctrl = event.ctrl
        self.shift = event.shift
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        if self.ctrl: # copy path
            context.window_manager.clipboard = self.filepath
            self.report({'INFO'}, f'Copied: "{self.filepath}"')

        elif self.alt: # copy name
            f = Path(self.filepath)
            if f.name == '__init__.py': # multifile
                name = f.parent.name
            else: # single file
                name = f.stem # 'name' to include '.py'
            context.window_manager.clipboard = name
            self.report({'INFO'}, f'Copied: "{name}"')
        
        else:
            fn.open_folder(self.filepath)

        return {"FINISHED"}


###---PREF PANEL

class DEV_PT_tools_addon_pref(bpy.types.AddonPreferences):
    bl_idname = __name__

    external_editor: bpy.props.StringProperty(
            name="External Editor",
            subtype='FILE_PATH',
            )

    # copy_pressed_keys : bpy.props.BoolProperty(
    #         name="Copy key",
    #         default=False,
    #         )

    devtool_addonpack_exclude: bpy.props.StringProperty(
        name='Always Exclude',
        default='__pycache__',
        description='Additional exclusion filter for addon packing functionality (comma separated)\nFor Export Zip operator (text editor sidebar > Dev tab > Addon List > Export Zip)'
        )

    def draw(self, context):
        layout = self.layout

        layout.operator("devtools.backup_prefs", text='Backup user prefs and startup files')

        layout.separator()

        layout.prop(self, "external_editor")
        col = layout.column()
        col.label(text="Option for addon packing zip:")
        col.prop(self, "devtool_addonpack_exclude")
        
        layout.separator()
        layout.operator("wm.path_open", text='Edit text editor quick modules imports (ctrl + shift + i)').filepath = str(Path(__file__).with_name('imports.txt'))
        # layout.separator()

        box = layout.box()
        box.label(text='Shortcuts')
        col = box.column()
        col.label(text='Ctrl+Shift+I : classic import modules insertion   |  Ctrl+P : print(selection) insertion')
        col.label(text='Ctrl+Alt+P : print("selection") insertion   |  Ctrl+Shift+P : print debug variable insertion')
        col.label(text='Ctrl+L : Quote selection (with automatic quote or double quote choice)')


###---KEYMAP

addon_keymaps = []
def register_keymaps():
    wm = bpy.context.window_manager
    addon = bpy.context.window_manager.keyconfigs.addon
    km = wm.keyconfigs.addon.keymaps.new(name = "Text", space_type = "TEXT_EDITOR")

    kmi = km.keymap_items.new("devtools.simple_print", type = "P", value = "PRESS", ctrl = True)
    kmi.properties.quote = False
    kmi = km.keymap_items.new("devtools.simple_print", type = "P", value = "PRESS", ctrl = True, alt = True)
    kmi.properties.quote = True
    kmi = km.keymap_items.new("devtools.debug_print_variable", type = "P", value = "PRESS", ctrl = True, shift = True)
    kmi = km.keymap_items.new("devtools.quote", type = "L", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("devtools.insert_import", type = "I", value = "PRESS", ctrl = True, shift=True)

    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


###---REGISTER

classes = (
DEV_OT_open_element_in_os,
DEV_OT_simple_print,
DEV_OT_quote,
DEV_OT_insert_import,
DEV_OT_debug_print_variable,
DEV_OT_disable_all_debug_print,
DEV_OT_enable_all_debug_print,
DEV_OT_delete_all_debug_print,
DEV_OT_expand_shortcut_name,
DEV_OT_text_diff,
DEV_OT_update_debug_linum,
DEV_OT_write_classes_tuple,
DEV_OT_print_resources_paths,
DEV_OT_time_selection,
DEV_OT_insert_date,
DEV_OT_blender_info,
DEV_OT_key_printer,
DEV_OT_create_context_override,
DEV_OT_backup_pref,
DEV_PT_tools_addon_pref,
)


def register():
    if bpy.app.background:
        return

    openers.register()
    error_handle.register()
    api_explore.register()
    for cls in classes:
        bpy.utils.register_class(cls)
        
    register_keymaps()
            
    bpy.types.Scene.enum_DebugPrint = bpy.props.EnumProperty(
            name = "enum_DebugPrint",
            description = "options",
            items = [
                ("devtools.enable_all_debug_print", 
                "Enable all debug print", 
                "uncomment all lines finishing wih '#Dbg'"),
                
                ("devtools.disable_all_debug_print", 
                "Disable all debug print", 
                "comment all lines finishing with '#Dbg'"),
                
                ("devtools.delete_all_debug_print", 
                "Delete all debug print", 
                "Delete all debug prints"), 
            ],
            update=update_enum_DebugPrint
        )

    console_ops.register()
    addon_listing.register()
    ui.register()

def unregister():
    if bpy.app.background:
        return

    ui.unregister()
    addon_listing.unregister()
    api_explore.unregister()

    error_handle.unregister()
    console_ops.unregister()
    openers.unregister()
    
    del bpy.types.Scene.enum_DebugPrint
    
    unregister_keymaps()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
