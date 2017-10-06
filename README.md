# devTools
Blender addon - add developpement tools to blender texte editor

---

### Description

Add buttons to text-editor toolbar:

- Print debug variable - Add a line in text to print selected variable on next execution
- Disable all debug - Comment all lines terminating with "#Dbg" (like the print debug variable do)
- Enable all debug
- Expand text shortcuts - Replace _C._ with _bpy.context._ and _D._ with _bpy.data_
- Text diff external - Print a diff with internal text and external source in console (appears only if file is external)
- Open externally - Open in external default editor or associated program

Add text-editor shorctut:

- Ctrl+Shift+I : add a quick import/classic module statement at cursor
- Ctrl+P : add "print(*selection*)"
- Ctrl+shift+P : trigger *print debug variable*
- Ctrl+L : Quote selection (with automatic quote or double quote choice)


### Updates

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
