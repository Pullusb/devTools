# devTools
Blender addon - add developpement tools to blender texte editor
  
**[Download latest](https://raw.githubusercontent.com/Pullusb/devTools/master/SB_devTools.py)** (right click, save Target as)

**[Download old (2.7 version)](https://raw.githubusercontent.com/Pullusb/devTools/master/SB_devTools_279.py)** (right click, save Target as)

---

### Description

Add buttons to text-editor toolbar:

- Print debug variable - Add a line in text to print selected variable on next execution
- Disable all debug - Comment all lines terminating with "#Dbg" (like the print debug variable do)
- Enable all debug
- Expand text shortcuts - Replace _C._ with _bpy.context._ and _D._ with _bpy.data_
- write classes tuple - Write a tuple at cursor containing all classes in file (for register/unregister in loop)
- Text diff external - Print a diff with internal text and external source in console (appears only if file is external)
- Open folder - Open folder where text is located in OS browser
- Open externally - Open in external default editor or associated program

Add text-editor shorctut:

- Ctrl+Shift+I : add a quick import/classic module statement at cursor
- Ctrl+P : add "print(*selection*)"
- Ctrl+shift+P : trigger *print debug variable*
- Ctrl+L : Quote selection (with automatic quote or double quote choice)


### Updates

19/02/2019 - 1.0.8:
  - version 2.8
  - added button write classes tuple (helper to create the register class)
  - added button to update linum in debug prints

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
