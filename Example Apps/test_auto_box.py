#!/usr/bin/python3
"""A GTK simplifier."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import bszgw


TEST_ARRAY = [
        #first row including a 50x50 blank
[Gtk.Label("1"), Gtk.Label("2"), "50x50", Gtk.Label("3")],
        #second row including a sub-groups
[Gtk.Label("4"), Gtk.Label("5"), Gtk.Label("6"), [Gtk.Label("a"),
                                     [Gtk.Label("b"), Gtk.Label("c")],
                                                  Gtk.Label("d")]],
        #final row
[Gtk.Label("7"), Gtk.Label("8"), Gtk.Label("9")]
]

if __name__ == "__main__":
    box_test = bszgw.App("Auto Box Test", bszgw.AutoBox(TEST_ARRAY))
    box_test.launch()
