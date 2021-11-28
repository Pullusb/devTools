# Changelog

1.7.3 - 2021-11-28

- fix: path to addon api change in 3.0.0
- doc: moved log from _readme_ to a _changelog_ file

1.7.2 - 2021-09-11:

- feat: `ctrl+clic` on key event tester (key printer) will copy each print to clipboard
- fix: register for blender background launch


1.7.1 - 2021-01-16:

- fix: error in report on _open file externally_ ops
- code: added tracker url


1.7.0 - 2020-09-21:

- feat/fix: new copyselected method and clip handling by [1C0D](https://github.com/1C0D) ([link to changes](https://github.com/Pullusb/devTools/pull/7)):
  - if selection, copy the selection
  - if no selection copy word under cursor
  - if no selection and no word under cursor copy what is in the clipboard
  - possible to copy something, go to an empty text zone and do e.g print


1.6.0 - 2020-09-03:

- feat: Create some context override code  


1.5.0 - 2020-09-03:

- Added by [1C0D](https://github.com/1C0D):
  - feat: add direct print statement on selection "quoted" on ctrl+alt+P
  - pref: added preference to disable click area button in console
  - pref: added shortcut list

- fix: external script location now using correct path separator (os.sep) according to user OS (using pathlib)
- change: Changed import insert (added pathlib import and deleted obsolete "coding utf-8" statement)


1.4.0 - 2020-07-22:

- code: Passing 'wiki_url' to 'doc_url' in bl_infos to comply with 2.83
- new: operator erase debug prints with new UI enum integration (thanks to [1C0D](https://github.com/1C0D)) for his [pull request](https://github.com/Pullusb/devTools/pull/3))
- new: operator to backup userpref and startup files in config folder
- typos


1.3.0 - 2020-07-04:

- New keycode printer operator
- update readme


1.2.0 - 2020-07-01:

- fix: time selected now works
- feat: new console head button to clic in any area to quickly write access to it in current console
- code: renamed to `__init__` do pass in folder addon mode (for 2.8 version)


1.1.0 - 22-06-2019:

- added insert date and insert build infos


1.0.9 - 21-06-2019:

- added buttons to open easily all addons sources folder used by blender 
- open function now use subprocess instead of os.system (more robust on all platform and no risk to block UI)
- bug fixing for 2.8 version
 


1.0.8 - 19-02-2019:

- version 2.8
- added button write classes tuple (helper to create the register class)
- added button to update linum in debug prints
- added shortcut ctrl+shift+N to create a new text block - ! EDIT ! removed : Alt+N default shortcut does this


1.0.7 - 17-06-2018:

- added button to open folder location in OS browser
- Bugfix, open in external exditor now work in windows


1.0.6 - 19-12-2017 :

- Fix problem when file seems unsync to blender but there is no difference (print 'no diff detected')
  

01-12-2017:

- Ctrl+Shift+I create the text block if not any (it does the "ctrl+n" for you ;) )


06-10-2017:

- add button to open in external default editor


31-08-2017:

- add button to print difference between internal and external code in console


20-06-2017:

- add text-editor shorctut: Ctrl+Shift+I : write a quick import/classic module statement


13-06-2017:

- add C and D text shortcut expansion


26-04-2017:

- add text-editor shortcut:
  - Ctrl+P : add "print(*selection*)"
  - Ctrl+shift+P : trigger *print debug variable*
  - Ctrl+L : Quote selection (with automatic quote or double quote selection)


05/04/2017:

- checkbox to enable/disable hardcode line number in print