#!/usr/bin/python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import bszgw


if __name__ == "__main__":
    #Demonstrating various widgets. For more detail look in bszgw.py
    test_adjuster = bszgw.Adjuster.new("Test Adjuster", 30, 0, 100, 5, 10)
    test_adjuster2 = bszgw.Adjuster.new("Test Adjuster2", 30, 0, 100, 5, 10, decimals=1, spin_button=False)
    test_check = bszgw.CheckBox("Test Check Box", True)
    test_drop_down = bszgw.DropDown("Test Drop Down", [["Choice A", "A"], ["Choice B", "B"], ["Choice C", "C"]], "A", enums=True)
    test_radio = bszgw.RadioButtons("Test Radio Buttons", ["Choice A", "Choice B", "Choice C"], 0)
    test_text_box = bszgw.TextBox("Test Text Box", "Test Text\nLine 2")

    #Functions called by buttons get sent the button itself as the first variable.
    #Will error if function takes no args
    def get_vals(widget):
        bszgw.Message(f"""Test Adjuster = {test_adjuster.value}
Test Adjuster2 = {test_adjuster2.value}
Test Check = {test_check.value}
Test Drop Down = {test_drop_down.value}
Test Radio Buttons = {test_radio.value}
Test Text Box = '''{test_text_box.value}'''""")

    exec_button = bszgw.Button("Execute", get_vals)


    adjuster2_dropdown = bszgw.AutoBox([
        test_adjuster2,
        test_drop_down
        ])

    left_side = bszgw.AutoBox([
        test_adjuster,
        [adjuster2_dropdown, test_radio]
        ])

    right_side = bszgw.AutoBox([
        test_text_box,
        [test_check, exec_button]
        ])

    final_box = bszgw.AutoBox([left_side, right_side],
            orientation=Gtk.Orientation.HORIZONTAL)

    # What creating the final box would look like all on one call.
    # Same result as above

    # final_box = bszgw.AutoBox([
    #     [test_adjuster,
    #     [[test_adjuster2,
    #     test_drop_down], test_radio]],
    #     [test_text_box,
    #     [test_check, exec_button]]
    #     ], orientation=Gtk.Orientation.HORIZONTAL)

    test_app = bszgw.App("Test App", final_box, hint=Gdk.WindowTypeHint.DIALOG)
    #Running the window as with dialog hinting because it's pretty tiny and I haven't streamlined widget scaling yet. This way i3 creates it as floating instead of tiled.


    test_app.launch()
