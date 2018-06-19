### description: Description of App1
### categories: CategoryForApp1, SecondaryCategory
### built-in: yes
### dependencies: lib1, lib3
### license: MIT

import ugfx, pyb, buttons

ugfx.init()
ugfx.clear()
buttons.init()
ugfx.set_default_font(ugfx.FONT_NAME)
ugfx.text(27, 90, "APP1", ugfx.WHITE)
pyb.wfi()
ugfx.clear()

