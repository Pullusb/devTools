import bpy
from sys import platform
import subprocess
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