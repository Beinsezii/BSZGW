#!/usr/bin/python3
import gi
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk  # noqa: F401
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: F401
import bszgw


if __name__ == "__main__":
    # Demonstrating various widgets. For more detail look in bszgw.py
    adjuster = bszgw.Adjuster.new("Adjuster", 30, 0, 1000, 5, 10,
                                  decimals=1, logarithmic=True)
    adjuster2 = bszgw.Adjuster.new("Adjuster2", 30, 0, 100, 5, 10,
                                   scale=False)

    check_button = bszgw.CheckBox("Check Box", True)

    combo_box = bszgw.ComboBox.new(
        {"Choice A": "a", "Choice B": "b", "Choice C": "c"}, "a",
        tooltip="Combo Box"
    )

    radio_buttons = bszgw.RadioButtons(
        "Radio Buttons",
        ["Choice A", "Choice B", "Choice C"], 0
    )

    entry = bszgw.Entry("Entry", "Text\nLine 2")

    # Functions called by buttons get sent the button itself
    # as the first variable.
    # Will error if function takes no args
    def get_vals(widget):
        bszgw.Message(f"""Adjuster = {adjuster.value}
Adjuster2 = {adjuster2.value}
Check = {check_button.value}
Combo Box = {combo_box.value}
Radio Buttons = {radio_buttons.value}
Entry =
{entry.value}""")

    exec_button = bszgw.Button("Execute", get_vals)

    grid = bszgw.Gri()
    # GridChild just packs a widget with some extra properties for
    # adding to the grid
    GC = bszgw.GridChild

    grid.attach_all(
        GC(adjuster, width=2),
        adjuster2, GC(radio_buttons, col_off=1, height=2),
        combo_box,
    )

    # nothing stopping you from using GridChild to attach these all at once
    # but I think it looks nicer this way.
    grid.attach_all(
        GC(entry, width=2, height=2),
        check_button, GC(exec_button, col_off=1),
        column=3
    )

    # AutoBox version:

    # adjuster2_combo = bszgw.AutoBox([
    #     adjuster2,
    #     combo_box
    # ])

    # left_side = bszgw.AutoBox([
    #     adjuster,
    #     [adjuster2_combo, radio_buttons]
    # ])

    # right_side = bszgw.AutoBox([
    #     entry,
    #     [check_button, exec_button]
    # ])

    # box = bszgw.AutoBox([[left_side, right_side]])

    app = bszgw.App("App Name", grid, hint=Gdk.WindowTypeHint.DIALOG)

    app.launch()
