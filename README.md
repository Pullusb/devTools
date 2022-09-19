# DevTools

Blender addon - Add development tools to blender text editor
  
**[Download latest](https://github.com/Pullusb/devTools/archive/master.zip)**

For old blender 2.7 version go [here](https://github.com/Pullusb/SB_blender_addons_old_2_7)

### [Demo Youtube](https://youtu.be/Rs4y7DeHkp8)

---

<!-- TODO 
keymap code generator
separate key event tester and keymap generator in a separate file

find a way to align left in history explore
-->

### Description

#### Text operators

> Text editor > Sidebar > Dev Tools

Helpers for your current script:

- **Print debug variable** - Add a line in text to print selected variable on next execution
- **Disable all debug** - Comment all lines terminating with "#Dbg" (like the print debug variable do)
- **Delete all debug print** (replace by blank lines)
- **Enable all debug**
- **Time selected lines** - Add two timer lines to print execution code (in seconds) of selected line (add import if necessary)
- **Expand text shortcuts** - Replace _C._ with _bpy.context._ and _D._ with _bpy.data_
- **write classes tuple** - Write a tuple at cursor containing all classes in file (for register/unregister in loop)
- **Context override** - Modal, click in any area after clicking the button to generate a context override function pointing to this area type  
- **Text diff external** - Print a diff with internal text and external source in console (appears only if file is external)
- **Open folder** - Open folder where text is located in OS browser
- **Open externally** - Open in external default editor or associated program

Opening addons places on disk:

- **Open scripts buit-in** - open addon location in the installation directory where addons shipped with blender are stored
- **Open scripts user** - open local user addon source (Where it goes when you do an "install from file", e.g: in "Appdata roaming" for windows)
- **Open scripts external** - open external scripts location if any specified (in Prefs > File)
- **Open config folder** - open local user config folder


Inserting / printing infos about blender:

- **Print usefull resources path** - Print in console and add to current text all paths relative to addons location, config path and more
- **Insert date** - Insert current date at cursor position. re-click add hour. re-re-click add abbreviated day
- **Release infos** - Insert blender release info (Date, Hash, branch), Usefull for bug report (print full build info in console)

Modal:

- **Event Keycode printer** - Modal to capture event and print event.type and event.value. Serve as quick way to know keycode to use for keymap or modals

#### Addon listing with batch operation

> Text editor > Sidebar > Addon List

Display a filterable and selectable list of all addon listed by blender:

- Button to open addon location (:file_folder:)
- Additional action with modifier+clic on folder button:
  - Ctrl + clic: copy path
  - Alt + clic: module name
- Filers to show module name and version (Search bar right buttons)

Actions:

- **Open Active Prefs** - Open addon pref of active (highlighted) line 
- **Export Addon Pack As Zip** - Export selected addons in a zip pack with include/exclude filters
- **Print Selected Infos** - Just print some infos in console
- **Batch Disable addons** - Disable all selected addons

#### Actions for interactive console:

> Interactive Console > Header bar

- **Select Area** - click in any area to write in console the path to it (in current layout). e.g: `bpy.context.screen.areas[5]`

- **Context override** - click in any area to write context override variable line (in current layout)

`Ctrl + F` - search word in API within the scope of datapath already typed in console

`Ctrl + H` - pop up a history of console lines. select some and press enter to add then to clipboard


#### Text-editor shorctut:

- `Ctrl+Shift+I` : add a quick import/classic module statement at cursor
- `Ctrl+P` : add _print(*selection*)_
- `Ctrl+Alt+P` : add _print("*selection*")_
- `Ctrl+Shift+P` : trigger *print debug variable*
- `Ctrl+L` : Quote selection (with automatic quote or double quote choice)
