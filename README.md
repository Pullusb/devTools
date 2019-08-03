# devTools
Blender addon - add developpement tools to blender texte editor
  
**[Download latest](https://raw.githubusercontent.com/Pullusb/devTools/master/SB_devTools.py)** (right click, save Target as)

**[Download old (2.7 version)](https://raw.githubusercontent.com/Pullusb/devTools/master/SB_devTools_279.py)** (right click, save Target as)

---

### Description

#### Add buttons to text-editor toolbar:

Helpers for your current script:
- Print debug variable - Add a line in text to print selected variable on next execution
- Disable all debug - Comment all lines terminating with "#Dbg" (like the print debug variable do)
- Enable all debug
- Expand text shortcuts - Replace _C._ with _bpy.context._ and _D._ with _bpy.data_
- write classes tuple - Write a tuple at cursor containing all classes in file (for register/unregister in loop)
- Text diff external - Print a diff with internal text and external source in console (appears only if file is external)
- Open folder - Open folder where text is located in OS browser
- Open externally - Open in external default editor or associated program

Opening addons places on disk:
- Open scripts buit-in - open addon location in the installation directory where addons shipped with blender are stored
- Open scripts user - open local user addon source (Where it goes when you do an "install from file", e.g: in "Appdata roaming" for windows)
- Open scripts external -  open external scripts location if any specified (in Prefs > File)

Inserting / printing infos about blender:
- Print usefull resources path - Print in console all paths relative to addons location, config path and more
- Insert date - Insert current date at cursor position. re-clic add hour. re-re-clic add abbreviated day
- Release infos - Insert blender release info (Date, Hash, branch), Usefull for bug report (print full build info in console)

#### Add text-editor shorctut:

- Ctrl+Shift+I : add a quick import/classic module statement at cursor
- Ctrl+P : add "print(*selection*)"
- Ctrl+Shift+P : trigger *print debug variable*
- Ctrl+L : Quote selection (with automatic quote or double quote choice)

---

### Updates

22/06/2019 - 1.1.0:
  - added insert date and insert build infos

21/06/2019 - 1.0.9:
  - added buttons to open easily all addons sources folder used by blender 
  - open function now use subprocess instead of os.system (more robust on all platform and no risk to block UI)
  - bug fixing for 2.8 version
 

19/02/2019 - 1.0.8:
  - version 2.8
  - added button write classes tuple (helper to create the register class)
  - added button to update linum in debug prints
  - added shortcut ctrl+shift+N to create a new text block - ! EDIT ! removed : Alt+N default shortcut does this

17/06/2018 - 1.0.7:
  - added button to open folder location in OS browser
  - Bugfix, open in external exditor now work in windows

19/12/2017 - 1.0.6 :  
  - Fix problem when file seems unsync to blender but there is no difference (print 'no diff detected')
  
01/12/2017:  
  - Ctrl+Shift+I create the text block if not any (it does the "ctrl+n" for you ;) )

06/10/2017:
  - add button to open in external default editor

31/08/2017
  - add button to print difference between internal and external code in console

20/06/2017:
  - add text-editor shorctut: Ctrl+Shift+I : write a quick import/classic module statement

13/06/2017:
  - add C and D text shortcut expansion

26/04/2017:
  - add text-editor shorctut:

    - Ctrl+P : add "print(*selection*)"
    - Ctrl+shift+P : trigger *print debug variable*
    - Ctrl+L : Quote selection (with automatic quote or double quote selection)

05/04/2017:

  - checkbox to enable/disable hardcode line number in print
