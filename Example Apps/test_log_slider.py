#!/usr/bin/python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import bszgw


if __name__ == "__main__":
    def status(*args):
        print(adjuster.value)
    adjuster = bszgw.Adjuster.new(
        "0-10000", 10, 0, 500, 1, 10, decimals=2,
        logarithmic=True, log_scale=1.5
    )
    newadj = Gtk.Adjustment.new(10, 0, 10000, 1, 10, 0)
    adjuster.adjustment = newadj
    adjuster.scale.connect("button-release-event", status)
    box_test = bszgw.App("Auto Box Test", adjuster)
    adjuster.value = 1234.56
    box_test.launch()
