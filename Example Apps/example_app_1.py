#!/usr/bin/python3
import gi, bszgw
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


if __name__ == "__main__":
    test_adjuster = bszgw.Adjuster("Test Adjuster", 30, 0, 100, 5, 10)
    test_adjuster2 = bszgw.Adjuster("Test Adjuster2", 30, 0, 100, 5, 10, decimals = 1, slider=False)
    test_check = bszgw.CheckBox("Test Check Box", True)
    test_drop_down= bszgw.DropDown("Test Drop Down", [["Choice A", "A"], ["Choice B", "B"], ["Choice C", "C"]], "A", enums=True)
    test_radio = bszgw.RadioButtons("Test Radio Buttons", ["Choice A", "Choice B", "Choice C"], 0)
    test_text_box = bszgw.TextBox("Test Text Box", "Test Text\nLine 2")
    def get_vals(widget):
        for x in [test_adjuster, test_adjuster2, test_check, test_drop_down, test_radio, test_text_box]:
            print(x.value)
    execbutton = Gtk.Button("Execute")
    execbutton.connect("clicked", get_vals)
    test_app = bszgw.App("Test App", 
        bszgw.QuantumBox([
            [test_adjuster,
            [[test_adjuster2,
            test_drop_down],test_radio]],
            [test_text_box,
            [test_check, execbutton]]
            ], orientation=Gtk.Orientation.HORIZONTAL))
    test_app.launch()
