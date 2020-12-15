#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""BeinSeZii Gtk Wrapper
Provides replacements for common GTK widgets intended to make dialog and
simple program creation take significantly less effort. Basically I got tired
of 70% of my lines being UI code and thought 'how can I be lazier'

Brief overview:
 - Data-entry widgets *all* have a read/write 'value' property and
   have reset() methods.
 - Tooltips for everything, labels where it makes sense.
 - Widgets are created more 'artistically'
   - Widgets can be created on initialization with common properties as kwargs.
   - The 'new()' method, if present, will create a fully functional widget
     entirely from regular Python types, generating buffers/models as needed.
     Create an entire ComboBox from a dict!
"""


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk
from gi.repository import GObject
import math


# TODO:
# Settle on App's scope and move it out of experimental


# ### MIX-INS ### #
# {{{

class WidgetMixIn(GObject.Object):
    # {{{
    """Mix-in providing various properties for BSZGW widgets."""
    def __init__(self, tooltip: str = ""):
        """Shorthand way to set initial settings."""
        self.tooltip = tooltip

    @property
    def tooltip(self):
        """Tooltip for widget."""
        return self.props.tooltip_text

    @tooltip.setter
    def tooltip(self, value):
        self.props.tooltip_text = value
    # }}}


class DataWidgetMixIn(WidgetMixIn):
    # {{{
    """Mix-in providing additional properties and methods on top of
WidgetMixIn designed for data-entry fields."""
    def __init__(self, value, tooltip: str = ""):
        """Shorthand way to set initial settings.
Also sets reset_value used in reset()"""
        super().__init__(tooltip=tooltip)
        self.value = value
        self.reset_value = value

    def connect_value_changed(self, function: callable, *args):
        """Connects to the widget's value change signal."""
        raise NotImplementedError

    def reset(self):
        self.value = self.reset_value

    @property
    def value(self):
        """Value of the main data field."""
        raise NotImplementedError

    @value.setter
    def value(self, value):
        raise NotImplementedError
    # }}}


# }}}
# ### CONTAINER TYPES ### #
# {{{

class App(Gtk.Window):
    # {{{
    """DOCSTRING TODO
EXPERIMENTAL"""
    def __init__(self, label, widget, width=-1, height=-1,
                 hint=Gdk.WindowTypeHint.NORMAL):
        super(App, self).__init__()
        self.connect("destroy", Gtk.main_quit)
        self.props.title = label
        self.props.type_hint = hint
        self.add(widget)
        self.props.default_width = width
        self.props.default_height = height

    def launch(self, *prelaunch):
        self.present()
        self.show_all()
        for x in prelaunch:
            if len(x) == 1:
                x[0]()

            else:
                x[0](*x[1:])

        Gtk.main()
    # }}}


def AutoBox(widgets: list, vspacing=10, hspacing=10, orientation=1) -> Gtk.Box:
    # {{{
    """Automatically packs widgets into a box with recursion depth.
Every sub-list inside the main widgets list flips packing orientation.
This allows you to visually build your boxes:
[
 [a, b, c]
     d,
     e,
]"""

    box = Gtk.Box.new(
        orientation,
        vspacing if orientation == Gtk.Orientation.VERTICAL else hspacing
    )

    sub_orientation = 1 - orientation
    for x in widgets:
        if isinstance(x, list):
            x = AutoBox(x, vspacing, hspacing, sub_orientation)

        if len(widgets) == 1:
            return x

        if isinstance(x, Gtk.Widget):
            box.pack_start(x, True, True, 0)

    if not box.get_children():
        return None

    return box
    # }}}


class GridChild():
    # {{{
    """GridChild can be given to bszgw.Grid's multi-widget functions in place of
regular widgets. This allows the child to have many custom placement properties
in a relatively compact fashion.

col_off, row_off: offsets for column and row.
width, height: if not None, overrides default dimension[s] when attaching."""
    def __init__(
        self, widget: Gtk.Widget,
        col_off: int = 0, row_off: int = 0,
        width: int = None, height: int = None,
    ):
        self.widget = widget
        self.col_off = col_off
        self.row_off = row_off
        self.width = width
        self.height = height
    # }}}


class Grid(Gtk.Grid):
    # {{{
    """Gtk.Grid with easier widget attachment functions.
Also has some common props in init."""
    def __init__(self,
                 column_spacing: int = 10, row_spacing: int = 10,
                 column_homogeneous: bool = False,
                 row_homogeneous: bool = False):
        super(Gtk.Grid, self).__init__()
        self.props.column_spacing = column_spacing
        self.props.row_spacing = row_spacing
        self.props.column_homogeneous = column_homogeneous
        self.props.row_homogeneous = row_homogeneous

    def attach_all(self, *children,  # noqa: C901 Really? Only like 30 lines...
                   column: int = 0, row: int = 0,
                   base_width: int = 1, base_height: int = 1,
                   direction: Gtk.DirectionType = Gtk.DirectionType.DOWN):
        """Attaches multiple children at once.

children: must be either instance of Gtk.Widget or bszgw.GridChild
column and row: starting coordinates.
base_width and base_height: size of widgets if not specified in GridChild
direction: direction to 'push' widgets when they try to occupy the same space.
Note all children's coords start at column, row instead of starting from the
previous child's place."""

        for child in children:
            # for automation purposes.
            if child is None:
                continue

            if isinstance(child, Gtk.Widget):
                child = GridChild(child)

            if not isinstance(child, GridChild):
                raise TypeError(f"Child {child} is not an instance of "
                                "Gtk.Widget or GridChild")

            if child.width is None:
                child.width = base_width
            if child.height is None:
                child.height = base_height

            left = column + child.col_off
            top = row + child.row_off

            # collision detection.
            # increment a grid cell in orientation if occupied
            # if there's a use case where widgets should be over
            # other widgets that should be done manually.
            while True:
                if not self.get_child_at(left, top):
                    break
                if direction == Gtk.DirectionType.DOWN:
                    top += 1
                elif direction == Gtk.DirectionType.RIGHT:
                    left += 1
                elif direction == Gtk.DirectionType.UP:
                    top -= 1
                elif direction == Gtk.DirectionType.LEFT:
                    left -= 1
                else:
                    raise TypeError("Invalid direction")

            self.attach(child.widget, left, top, child.width, child.height)
    # }}}


# }}}
# ### WIDGETS ### #
# {{{

class Adjuster(Gtk.Box):
    # {{{
    """Widget for adjusting integers or floats.
Adjuster() takes a label and Gtk.Adjustment,
while Adjuster.new() builds a Gtk.Adjustment from values inputted.
If logarithmic=True, the scale (slider)'s adjustment will be changed
according to log(x, log_scale).  This means the scale will 'accelerate'
as you get closer to higher values."""
    def __init__(self,
                 label: str,
                 adjustment: Gtk.Adjustment,
                 decimals: int = 0,
                 orientation: Gtk.Orientation = Gtk.Orientation.HORIZONTAL,
                 tooltip: str = None,
                 expand=True,
                 spin_button: bool = True,
                 scale: bool = True,
                 spin_accel: float = 0.0,
                 logarithmic: bool = False,
                 log_scale: int = 2,
                 scale_min_size: int = 200,
                 ):
        super(Adjuster, self).__init__()

        # Main box always vertical for label on top
        self.props.orientation = Gtk.Orientation.VERTICAL

        # log is a one-stop shop. Must have both widgets and can't be reverted.
        # probably possible to make it changeable-on-the-fly but I've written
        # enough code for now.
        assert spin_button or scale
        if logarithmic:
            assert spin_button and scale and log_scale > 1
        self.log = logarithmic
        self.ls = log_scale

        # label doesn't grow
        self.label = Gtk.Label.new(label)
        self.pack_start(self.label, False, True, 0)

        adjuster_box = Gtk.Box.new(orientation, 0)
        self.pack_start(adjuster_box, True, True, 0)

        if scale:
            self.scale = Gtk.Scale.new(orientation, adjustment)
            # disable value pop-up if spin_button used.
            self.scale.props.draw_value = not spin_button

            # min size request, either horizontally or vertically.
            # I had one of my scales get compressed into a single pixel before
            # so this is necessary
            if orientation == Gtk.Orientation.HORIZONTAL:
                width = scale_min_size
                height = -1

            else:
                self.scale.props.value_pos = Gtk.PositionType.LEFT
                width = -1
                height = scale_min_size

            self.scale.set_size_request(width, height)
            adjuster_box.pack_start(self.scale, True, True, 0)

            if tooltip:
                self.scale.props.tooltip_text = tooltip

        if spin_button:
            self.spin_button = Gtk.SpinButton.new(adjustment, spin_accel, 0)
            # if scale present, don't expand
            adjuster_box.pack_start(self.spin_button, not scale, True, 0)

            if tooltip:
                self.spin_button.props.tooltip_text = tooltip

        self.decimals = decimals
        self.adjustment = adjustment
        self.expand = expand

    def set_main_log(self, *args):
        """Internal function runs when a logarithmic scale is changed,
to update the spin button."""
        if self.log:
            self.adjustment.props.value = \
                self.ls ** self.scale.props.adjustment.props.value

    def set_log_main(self, *args):
        """Internal function runs when a spin button is changed,
to update the logarithmic scale."""
        if self.log:
            self.scale.props.adjustment.props.value = \
                math.log(self.adjustment.props.value, self.ls)

    def new(label,
            value, min_value, max_value, step_increment, page_increment,
            decimals=0, orientation=Gtk.Orientation.HORIZONTAL,
            tooltip=None, spin_button=True, scale=True, expand=True,
            spin_accel=0.0, logarithmic=False, log_scale=2,
            scale_min_size=200):

        return Adjuster(
            label=label,
            adjustment=Gtk.Adjustment.new(value, min_value, max_value,
                                          step_increment, page_increment, 0),
            decimals=decimals,
            orientation=orientation,
            tooltip=tooltip,
            expand=expand,
            spin_button=spin_button,
            scale=scale,
            spin_accel=spin_accel,
            logarithmic=logarithmic,
            log_scale=log_scale,
            scale_min_size=scale_min_size,
        )

    def reset(self):
        self.value = self.initial

    @property
    def adjustment(self):
        if hasattr(self, 'spin_button'):
            return self.spin_button.props.adjustment
        elif hasattr(self, 'scale'):
            return self.scale.props.adjustment
        # don't need log check.

    @adjustment.setter
    def adjustment(self, new_adjust):
        if hasattr(self, 'spin_button'):
            self.spin_button.set_adjustment(new_adjust)
        if hasattr(self, 'scale'):
            # if log, create a separate Gtk.Adjustment connected to
            # set_main_log()
            if self.log:
                low = new_adjust.props.lower
                # only log the lower limit if above 0
                if low > 0:
                    newlow = math.log(low, self.ls)
                else:
                    newlow = low

                # logs the upper, possibly lower (above), and value.
                # to base self.ls
                log_adjust = Gtk.Adjustment.new(
                    value=math.log(new_adjust.props.value, self.ls),
                    lower=newlow,
                    upper=math.log(new_adjust.props.upper, self.ls),
                    step_increment=new_adjust.props.step_increment,
                    page_increment=new_adjust.props.page_increment,
                    page_size=new_adjust.props.page_size
                )
                log_adjust.connect("value-changed", self.set_main_log)
                self.adjustment.connect("value-changed", self.set_log_main)
                self.scale.props.adjustment = log_adjust
            else:
                self.scale.adjustment = new_adjust
        self.initial = self.value

    @property
    def decimals(self):
        if hasattr(self, 'spin_button'):
            return self.spin_button.props.digits
        elif hasattr(self, 'scale'):
            return self.scale.props.digits

    @decimals.setter
    def decimals(self, new_decimals):
        if hasattr(self, 'spin_button'):
            self.spin_button.props.digits = new_decimals
        if hasattr(self, 'scale'):
            self.scale.props.digits = new_decimals

    @property
    def expand(self):
        return self.__expand

    @expand.setter
    def expand(self, expand: bool):
        if hasattr(self, 'scale'):
            if self.scale.props.orientation == Gtk.Orientation.HORIZONTAL:
                self.scale.props.hexpand = expand
                self.scale.props.vexpand = False
            else:
                self.scale.props.vexpand = expand
                self.scale.props.hexpand = False

        elif hasattr(self, 'spin_button'):
            self.spin_button.props.hexpand = expand
        self.__expand = expand

    @property
    def value(self):
        if self.decimals > 0:
            return float(f'%.{self.decimals}f' % (self.adjustment.props.value))

        else:
            return int(f'%.{self.decimals}f' % (self.adjustment.props.value))

    @value.setter
    def value(self, new_value):
        self.adjustment.props.value = new_value
        if self.log:
            self.scale.props.adjustment.props.value = \
                math.log(new_value, self.ls)
    # }}}


class Button(Gtk.Button, WidgetMixIn):
    # {{{
    """Gtk.Button. Has connect('clicked') built into init."""
    def __init__(self, label, function, *args, tooltip=None):
        super().__init__(label=label)
        WidgetMixIn.__init__(self, tooltip=tooltip)
        self.connect('clicked', function, *args if args else ())
    # }}}


class CheckButton(Gtk.CheckButton, DataWidgetMixIn):
    # {{{
    """Basically just a normal GTK checkbutton with the 'value' property
and other tiny additions.  Possibly overkill."""
    def __init__(self, label, value, tooltip=None, expand: bool = False):
        super().__init__(label=label)
        DataWidgetMixIn.__init__(self, value, tooltip=tooltip)

    def connect_value_changed(self, function, *args):
        self.connect("toggled", function, *args if args else ())

    @property
    def value(self):
        return self.props.active

    @value.setter
    def value(self, value):
        self.props.active = value
    # }}}


class ComboBox(Gtk.ComboBox):
    # {{{
    """Widget for selecting values in a drop-down list.
Right now basically exclusively made for text. I want to implement more
ComboBox/CellRenderer/TreeModel features but I'm not sure how to do that
all in one or if it's even possible. Tempted to rename this ComboBoxText and
just make new ComboBoxes for other types."""
    def __init__(self, model: Gtk.TreeModel, value,
                 tooltip: str = None, column: int = 0, id_column: int = 0,
                 expand: bool = True, show_ids: bool = False, wrap: int = 0):
        super(ComboBox, self).__init__()

        if tooltip:
            self.props.tooltip_text = tooltip
        self.props.model = model

        self.renderer = Gtk.CellRendererText()
        self.pack_start(self.renderer, True)
        self.add_attribute(self.renderer, "text", column)

        if show_ids:
            self.id_renderer = Gtk.CellRendererText()
            self.pack_start(self.id_renderer, True)
            self.add_attribute(self.id_renderer, "text", id_column)

        self.props.wrap_width = wrap
        self.props.id_column = id_column
        self.value = value
        self.initial_value = value
        self.expand = expand

    def new(dictionary: dict, value,
            tooltip: str = None, expand: bool = True,
            show_ids: bool = True, wrap: int = 0):
        """Creates a new ComboBox from a dictionary.
Value types must be uniform among keys and among values"""
        # is there a better way to get the first key and val?
        key_type = type(list(dictionary)[0])
        val_type = type(dictionary[list(dictionary)[0]])
        model = Gtk.ListStore(key_type, val_type)
        for key in dictionary.keys():
            model.append((key, dictionary[key]))

        return ComboBox(
            model=model, value=value, tooltip=tooltip, expand=expand,
            id_column=1, show_ids=show_ids, wrap=wrap,
        )

    def reset(self):
        self.value = self.initial_value

    @property
    def expand(self):
        return self.__expand

    @expand.setter
    def expand(self, expand):
        self.props.hexpand = expand
        self.__expand = expand

    @property
    def value(self):
        return self.props.active_id

    @value.setter
    def value(self, new_value):
        self.props.active_id = new_value
    # }}}


class Entry(Gtk.Box):
    # {{{
    """Creates a scrollable text entry widget.
For self.entry, multi-line uses Gtk.TextView and single-line uses Gtk.Entry.
No .new() method, as the widgets create their own buffers on creation.
Use the text_buffer property to set new buffers instead."""
    def __init__(self, label, value, tooltip: str = None,
                 multi_line=True, expand: bool = True,
                 min_width=200, min_height=100):
        super(Entry, self).__init__()

        self.__multi_line = multi_line
        self.props.orientation = Gtk.Orientation.VERTICAL
        self.label = Gtk.Label.new(label)
        self.pack_start(self.label, False, True, 0)

        self.scrolled_window = Gtk.ScrolledWindow.new(None, None)
        self.pack_start(self.scrolled_window, True, True, 0)

        if self.__multi_line:
            self.entry = Gtk.TextView.new()

        else:
            self.entry = Gtk.Entry.new()
            self.scrolled_window.props.vscrollbar_policy = Gtk.PolicyType.NEVER

        self.scrolled_window.add(self.entry)

        self.expand = expand
        self.min_width = min_width
        self.min_height = min_height
        self.tooltip = tooltip
        self.value = value

    @property
    def expand(self):
        return self.__expand

    @expand.setter
    def expand(self, expand):
        if self.__multi_line:
            self.scrolled_window.props.expand = expand
        else:
            self.scrolled_window.props.hexpand = expand
        self.__expand = expand

    @property
    def min_height(self):
        return self.__min_height

    @min_height.setter
    def min_height(self, min_height):
        if self.__multi_line:
            self.scrolled_window.props.min_content_height = min_height
        self.__min_height = min_height

    @property
    def min_width(self):
        return self.__min_width

    @min_width.setter
    def min_width(self, min_width):
        self.scrolled_window.props.min_content_width = min_width
        self.__min_width = min_width

    @property
    def text_buffer(self):
        return self.entry.props.buffer

    @text_buffer.setter
    def text_buffer(self, text_buffer):
        self.entry.props.buffer = text_buffer

    @property
    def tooltip(self):
        return self.entry.props.tooltip_text

    @tooltip.setter
    def tooltip(self, new):
        self.entry.props.tooltip_text = new

    @property
    def value(self):
        return self.text_buffer.props.text

    @value.setter
    def value(self, new_value):
        self.text_buffer.props.text = new_value
    # }}}


def Message(message):
    # {{{
    """Opens a pop-op displaying a message."""
    dialog = Gtk.MessageDialog(text=str(message),
                               buttons=Gtk.ButtonsType.CLOSE)
    dialog.run()
    dialog.destroy()
    # }}}


class RadioButtons(Gtk.Box):
    # {{{
    """DOCSTRING TODO"""
    def __init__(self, label, buttons, value,
                 orientation=Gtk.Orientation.VERTICAL,
                 enums=False, tooltip=None):
        assert len(buttons) > 1
        super(RadioButtons, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.enums = enums
        self.buttons_box = Gtk.Box.new(orientation, 5)
        self.label = Gtk.Label.new(label)
        self.pack_start(self.label, False, True, 0)
        self.pack_start(self.buttons_box, True, True, 0)
        self.radio_buttons = []
        if self.enums:
            self.values = []
        for num, var in enumerate(buttons):
            self.radio_buttons.append(Gtk.RadioButton.new_with_label(
                None, str(var) if not self.enums else str(var[0])))
            self.buttons_box.pack_start(self.radio_buttons[num], True, True, 0)

            if num > 0:
                self.radio_buttons[num].join_group(self.radio_buttons[0])

            if self.enums:
                self.values.append(var[1])

            if tooltip:
                self.radio_buttons[num].props.tooltip_text = tooltip

        self.value = value

    @property
    def value(self):
        for x in self.radio_buttons:
            if x.get_active():
                if self.enums:
                    return self.values[self.radio_buttons.index(x)]

                else:
                    return self.radio_buttons.index(x)

    @value.setter
    def value(self, new_value):
        for x in self.radio_buttons:
            if self.enums:
                if self.values[self.radio_buttons.index(x)] == new_value:
                    x.set_active(1)
                    return

            else:
                if self.radio_buttons.index(x) == new_value:
                    x.set_active(1)
                    return
    # }}}


# }}}
