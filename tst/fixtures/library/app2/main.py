"""Description of App2"""
___categories___ = ["CategoryForApp1", "SecondaryCategory"]
___bootstraped___ = True
___dependencies___ = ["lib/lib2.py", "lib/lib3.py"]
___license___ = "MIT"

import ugfx, pyb, buttons

ugfx.init()
ugfx.clear()
buttons.init()
ugfx.set_default_font(ugfx.FONT_NAME)
ugfx.text(27, 90, "APP1", ugfx.WHITE)
pyb.wfi()
ugfx.clear()
