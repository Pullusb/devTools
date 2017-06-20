# devTools
Blender addon - add developpement tools to blender texte editor

---

### Description

Add buttons to texte-ditor toolbar:

- Print debug variable - Add a line in text to print selected variable on next execution
- Disable all debug - Comment all lines terminating with "#Dbg" (like the print debug variable do)
- Enable all debug
- Expand text shortcuts - Replace _C._ with _bpy.context._ and _D._ with _bpy.data_

Add text-editor shorctut:

- Ctrl+Shift+I : add a quick import/classic module statement at cursor
- Ctrl+P : add "print(*selection*)"
- Ctrl+shift+P : trigger *print debug variable*
- Ctrl+L : Quote selection (with automatic quote or double quote choice)


### Updates

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
