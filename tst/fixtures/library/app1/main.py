"""Description of App1"""
___categories___ = ["CategoryForApp1", "SecondaryCategory"]
___bootstraped___ = True
___dependencies___ = ["lib1", "lib3"]
___license___ = "MIT"

import ugfx, pyb, buttons

ugfx.init()
ugfx.clear()
buttons.init()
ugfx.set_default_font(ugfx.FONT_NAME)
ugfx.text(27, 90, "APP1", ugfx.WHITE)
pyb.wfi()
ugfx.clear()

