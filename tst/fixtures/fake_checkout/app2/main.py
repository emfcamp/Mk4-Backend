### description: Description of App2
### categories: CategoryForApp2, SecondaryCategory
### dependencies: lib2, lib3

import ugfx, pyb, buttons

ugfx.init()
ugfx.clear()
buttons.init()
ugfx.set_default_font(ugfx.FONT_NAME)
ugfx.text(27, 90, "APP1", ugfx.WHITE)
pyb.wfi()
ugfx.clear()
