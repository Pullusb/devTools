import bpy
import subprocess
from sys import platform
from os.path import isfile, dirname, normpath, exists
from shutil import which


def get_addon_prefs():
    import os
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return (addon_prefs)

# unused
def copy_to_clipboard():
    '''Copy selected Text to clipboard'''
    bpy.ops.text.copy()
    clip = bpy.context.window_manager.clipboard
    return (clip)

def open_file(filepath):
    '''open the file at the path given with cmd relative to user's OS'''
    # preferences = bpy.context.preferences
    # addon_prefs = preferences.addons[__name__].preferences
    addon_prefs = get_addon_prefs()
    editor = addon_prefs.external_editor

    if not filepath:
        return('No file path !')
    
    if not exists(filepath):
        return(f'Not exists: {filepath}')

    if editor:
        cmd = editor.strip()
    else:
        myOS = platform
        if myOS.startswith('linux') or myOS.startswith('freebsd'):# linux
            cmd = 'xdg-open'
        elif myOS.startswith('win'):# Windows
            cmd = 'start'
        else:# OS X
            cmd = 'open'

    mess = cmd + ' ' + filepath
    fullcmd = [cmd, filepath]

    print('Command :', fullcmd)

    try:
        # subprocess.Popen(fullcmd)
        subprocess.call(fullcmd, shell=True)
    
    except:
        print('--/traceback--')
        import traceback
        traceback.print_exc()
        print('--traceback/--')
        # mess = 'Text editor not found ' + mess
        return {'CANCELLED'}

    return mess


## Open folder and select file if pointed to one
def open_folder(folderpath):
    """open the folder at the path given
    with cmd relative to user's OS
    on window, some linux, select the file if pointed
    """

    from sys import platform
    import subprocess

    myOS = platform
    if myOS.startswith(('linux','freebsd')):
        cmd = 'xdg-open'

    elif myOS.startswith('win'):
        cmd = 'explorer'
        if not folderpath:
            return('/')
    else:
        cmd = 'open'

    if not folderpath:
        return('//')

    if isfile(folderpath): # When pointing to a file
        select = False
        if myOS.startswith('win'):
            # Keep same path but add "/select" the file (windows cmd option)
            cmd = 'explorer /select,'
            select = True

        elif myOS.startswith(('linux','freebsd')):
            if which('nemo'):
                cmd = 'nemo --no-desktop'
                select = True
            elif which('nautilus'):
                cmd = 'nautilus --no-desktop'
                select = True

        if not select:
            # Use directory of the file
            folderpath = dirname(folderpath)

    folderpath = normpath(folderpath)
    fullcmd = cmd.split() + [folderpath]
    # print('Opening command :', fullcmd)
    subprocess.Popen(fullcmd)
    return ' '.join(fullcmd)


""" ## just open folder (replaced by func above)
def openFolder(folderpath):
    myOS = platform
    if myOS.startswith(('linux','freebsd')):
        cmd = 'xdg-open'
    elif myOS.startswith('win'):
        cmd = 'explorer'
        if not folderpath:
            return('/')
    else:
        cmd = 'open'

    if not folderpath:
        return('//')

    fullcmd = [cmd, folderpath]
    print(fullcmd)
    subprocess.Popen(fullcmd)
    return ' '.join(fullcmd)
"""


def get_text(context):
    '''get current text and override for text editor operator'''
    text = getattr(bpy.context.space_data, "text", None)

    #context override for the ops.text.insert() function
    override = {'window': context.window,
                'area'  : context.area,
                'region': context.region,
                'space': context.space_data,
                'edit_text' : text
                }
    return(text, override)

def set_file_in_text_editor(filepath, linum=None, context=None):
    context = context or bpy.context
    print('context.area.type: ', context.area.type)
    for t in [t for t in bpy.data.texts if t.filepath == filepath] :
        bpy.data.texts.remove(t)

    text = bpy.data.texts.load(filepath)

    areas = []
    text_editor = None
    for area in context.screen.areas :
        if area.type == 'TEXT_EDITOR' :
            text_editor = area

        else :
            areas.append(area)
    if not text_editor :
        if context.area.type == 'TOPBAR':
            ## Topbar can't be splitted
            ## fallback to first 3d view found (usually the bigger area)
            text_editor = next((area for area in context.screen.areas if area.type == 'VIEW_3D'), None)
            if text_editor is None:
                ## fallback to any area that is not topbar
                text_editor = next((area for area in context.screen.areas if area.type != 'TOPBAR'), None)
            with bpy.context.temp_override(area=text_editor):
                bpy.ops.screen.area_split(direction = "VERTICAL")

        else:
            bpy.ops.screen.area_split(direction = "VERTICAL")

        for area in context.screen.areas :
            if area not in areas :
                text_editor = area
                text_editor.type = "TEXT_EDITOR"
                text_editor.spaces[0].show_syntax_highlight = True
                text_editor.spaces[0].show_word_wrap = True
                text_editor.spaces[0].show_line_numbers = True
                context_copy = context.copy()
                context_copy['area'] = text_editor

    text_editor.spaces[0].text = text
    if linum:
        text.cursor_set(linum-1)
        ## this also force the scroll to jump where the caret is
        ## owtherwise stay at the top of the document
        with bpy.context.temp_override(area=text_editor):
            bpy.ops.text.move(type='LINE_BEGIN')
