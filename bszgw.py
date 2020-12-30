#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""BeinSeZii Gtk Wrapper 1.0.1
Provides replacements for common GTK widgets intended to make dialog and
simple program creation take significantly less effort. Basically I got tired
of 70% of my lines being UI code and thought 'how can I be lazier'

Brief overview:
 - Data-entry widgets have many extra features courtesy of the DataWidget mixin
   - `value` property
   - `reset` method
   - `connect_changed` method
 - Labels for everything
 - Widgets are created more 'artistically'
   - The 'new()' method, if present, will create a fully functional widget
     entirely from regular Python types, generating buffers/models as needed
"""


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk  # noqa: F401
from gi.repository import GObject
import math


# TODO:
# figure out why certain widgets dont like to super() self when
# using the mixin.


# ### MIX-INS ### #


class DataWidget(GObject.Object):
    # {{{
    """Mix-in containing additional methods and properties
for data-entry widgets"""
    def __init__(self, value, widget: Gtk.Widget, signal: str):
        """Shorthand way to set initial settings.
Also sets reset_value used in reset()"""
        super().__init__()
        self.value = value
        self.reset_value = value
        self.value_widget = widget
        self.value_signal = signal

    def connect_changed(self, function: callable, *args):
        """Connects to the widget's value change signal."""
        self.value_widget.connect(self.value_signal, function,
                                  *args if args else ())

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


# ### CONTAINER TYPES ### #


class App(Gtk.Window):
    # {{{
    """Simple wrapper around Gtk.Window intended to take a widget then
launch the Gtk main loop with it."""
    def __init__(self, title: str, widget: Gtk.Widget,
                 width: int = -1, height: int = -1):
        super().__init__()
        self.connect("destroy", Gtk.main_quit)
        self.props.title = title
        self.add(widget)
        self.props.default_width = width
        self.props.default_height = height

    def launch(self, *prelaunch: [callable, [callable, list]], show_all=True):
        """Launches the Gtk main engine, optoinally running prelaunch callables
after showing all the widgets.
Prelaunch entries may be a sub-list containing the callable and args.
If show_all=False, widgets are not shown by default on launch."""
        self.present()
        if show_all:
            self.show_all()
        for x in prelaunch:
            if len(x) == 1:
                x[0]()
            else:
                x[0](*x[1:])
        Gtk.main()
    # }}}


def AutoBox(
        widgets: [Gtk.Widget], vspacing: int = 10, hspacing: int = 10,
        orientation: Gtk.Orientation = Gtk.Orientation.VERTICAL) -> Gtk.Box:
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
        #  TODO: figure out why this is fucky with the mixin
        # super().__init__()
        Gtk.Grid.__init__(self)
        self.props.column_spacing = column_spacing
        self.props.row_spacing = row_spacing
        self.props.column_homogeneous = column_homogeneous
        self.props.row_homogeneous = row_homogeneous

    def attach_all(self, direction: Gtk.DirectionType, *children,  # noqa: C901
                   column: int = 0, row: int = 0,
                   base_width: int = 1, base_height: int = 1):
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

    def attach_all_down(self, *children, column: int = 0, row: int = 0,
                        base_width: int = 1, base_height: int = 1):
        self.attach_all(Gtk.DirectionType.DOWN, *children,
                        column=column, row=row,
                        base_width=base_width, base_height=base_height)

    def attach_all_left(self, *children, column: int = 0, row: int = 0,
                        base_width: int = 1, base_height: int = 1):
        self.attach_all(Gtk.DirectionType.LEFT, *children,
                        column=column, row=row,
                        base_width=base_width, base_height=base_height)

    def attach_all_right(self, *children, column: int = 0, row: int = 0,
                         base_width: int = 1, base_height: int = 1):
        self.attach_all(Gtk.DirectionType.RIGHT, *children,
                        column=column, row=row,
                        base_width=base_width, base_height=base_height)

    def attach_all_up(self, *children, column: int = 0, row: int = 0,
                      base_width: int = 1, base_height: int = 1):
        self.attach_all(Gtk.DirectionType.UP, *children,
                        column=column, row=row,
                        base_width=base_width, base_height=base_height)
    # }}}


def Message(message: str, buttons: [str] = [],
            modal=False, close_button=True) -> int:
    # {{{
    """Opens a pop-op displaying a message.  Returns the index of the
button pressed. Buttons may be str or a stock ID.
If close_button, also appends Gtk.STOCK_CLOSE with a response of -1"""
    dialog = Gtk.MessageDialog(text=str(message))
    for n, b in enumerate(buttons):
        dialog.add_button(b, n)
    dialog.add_button(Gtk.STOCK_CLOSE, -1)
    dialog.props.modal = modal
    result = dialog.run()
    dialog.destroy()
    return result
    # }}}


# ### WIDGETS ### #


class Button(Gtk.Button):
    # {{{
    """Gtk.Button. Has connect('clicked') built into init."""
    def __init__(self, label: str, function: callable, *args):
        super().__init__(label=label)
        self.connect('clicked', function, *args if args else ())
    # }}}


class CheckButton(Gtk.CheckButton, DataWidget):
    # {{{
    """Basically just a normal GTK checkbutton with the DataWidget mixin"""
    def __init__(self, label: str, value: bool):
        super().__init__(label=label)
        DataWidget.__init__(self, value, self, "toggled")

    @property
    def value(self) -> bool:
        return self.props.active

    @value.setter
    def value(self, value: bool):
        self.props.active = value
    # }}}


class ComboBox(Gtk.ComboBox, DataWidget):
    # {{{
    """Widget for selecting values in a drop-down list.
If id_column == column, it operates on indicies,
else it operates on the id_column text.

Right now basically exclusively made for text. I want to implement more
ComboBox/CellRenderer/TreeModel features but I'm not sure how to do that
all in one or if it's even possible. Tempted to rename this ComboBoxText and
just make new ComboBoxes for other types."""
    def __init__(self, model: Gtk.TreeModel, value,
                 column: int = 0, id_column: int = 0,
                 show_ids: bool = False, wrap: int = 0):
        # TODO: genuinely though why is this fucky in some widgets
        # super().__init__()
        Gtk.ComboBox.__init__(self)

        self.props.model = model
        self.column = column

        self.renderer = Gtk.CellRendererText()
        self.pack_start(self.renderer, True)
        self.add_attribute(self.renderer, "text", column)

        if show_ids:
            self.id_renderer = Gtk.CellRendererText()
            self.pack_start(self.id_renderer, True)
            self.add_attribute(self.id_renderer, "text", id_column)

        self.props.wrap_width = wrap
        self.props.id_column = id_column
        DataWidget.__init__(self, value, self, "changed")

    def new(items: [str], value: int, wrap: int = 0) -> 'ComboBox':
        """Creates a new ComboBox from a list/tuple of strings"""
        model = Gtk.ListStore(str)
        for item in items:
            model.append([item])

        return ComboBox(
            model=model, value=value, wrap=wrap
        )

    def new_dict(dictionary: {str: str}, value: str,
                 show_ids: bool = True, wrap: int = 0) -> 'ComboBox':
        """Creates a new ComboBox from a dictionary of strings."""
        # is there a better way to get the first key and val?
        model = Gtk.ListStore(str, str)
        for key in dictionary.keys():
            model.append((key, dictionary[key]))

        return ComboBox(
            model=model, value=value,
            id_column=1, show_ids=show_ids, wrap=wrap,
        )

    @property
    def value(self):
        if self.props.id_column == self.column:
            return self.props.active
        else:
            return self.props.active_id

    @value.setter
    def value(self, value):
        if self.props.id_column == self.column:
            self.props.active = value
        else:
            self.props.active_id = value
    # }}}


class Entry(Grid, DataWidget):
    # {{{
    """Creates a scrollable text entry widget.
For self.entry, multi-line uses Gtk.TextView and single-line uses Gtk.Entry.
No .new() method, as the widgets create their own buffers on creation.
Use the text_buffer property to set new buffers instead."""
    def __init__(self, value: str, label: str = "", multi_line: bool = False,
                 min_width: int = 200, min_height: int = 100):
        super().__init__()

        self.__multi_line = multi_line
        if label:
            self.label = Gtk.Label.new(label)
            self.attach_all_down(self.label)

        self.scrolled_window = Gtk.ScrolledWindow.new(None, None)
        self.attach_all_down(self.scrolled_window)

        if self.__multi_line:
            self.entry = Gtk.TextView.new()
            self.scrolled_window.props.expand = True

        else:
            self.entry = Gtk.Entry.new()
            self.scrolled_window.props.vscrollbar_policy = Gtk.PolicyType.NEVER
            self.scrolled_window.props.hexpand = True

        self.scrolled_window.add(self.entry)

        self.min_width = min_width
        self.min_height = min_height
        DataWidget.__init__(self, value, self.text_buffer, "changed")

    @property
    def min_height(self) -> int:
        return self.__min_height

    @min_height.setter
    def min_height(self, min_height: int):
        if self.__multi_line:
            self.scrolled_window.props.min_content_height = min_height
        self.__min_height = min_height

    @property
    def min_width(self) -> int:
        return self.__min_width

    @min_width.setter
    def min_width(self, min_width: int):
        self.scrolled_window.props.min_content_width = min_width
        self.__min_width = min_width

    @property
    def text_buffer(self) -> Gtk.TextBuffer:
        return self.entry.props.buffer

    @text_buffer.setter
    def text_buffer(self, text_buffer: Gtk.TextBuffer):
        self.entry.props.buffer = text_buffer

    @property
    def value(self) -> str:
        return self.text_buffer.props.text

    @value.setter
    def value(self, value: str):
        self.text_buffer.props.text = value
    # }}}


class RadioButtons(Grid, DataWidget):
    # {{{
    """Widget for choosing an option from a list.
Limited alternate to ComboBox"""
    def __init__(self, buttons: [str], value: int, label="",
                 orientation=Gtk.Orientation.VERTICAL):
        assert len(buttons) > 1
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        if label:
            self.label = Gtk.Label.new(label)
            self.attach_all_down(self.label)
        self.radio_buttons = []
        for num, var in enumerate(buttons):
            self.radio_buttons.append(Gtk.RadioButton.new_with_label(
                None, var))

            if num > 0:
                self.radio_buttons[num].join_group(self.radio_buttons[0])

        if orientation == Gtk.Orientation.VERTICAL:
            self.attach_all_down(*self.radio_buttons)
        elif orientation == Gtk.Orientation.HORIZONTAL:
            self.attach_all_right(*self.radio_buttons, row=1)

        DataWidget.__init__(self, value,
                            self.radio_buttons[0], "group-changed")

    @property
    def value(self) -> int:
        for x in self.radio_buttons:
            if x.get_active():
                return self.radio_buttons.index(x)

    @value.setter
    def value(self, value: int):
        self.radio_buttons[value].set_active(1)
    # }}}


class SpinScale(Grid, DataWidget):
    # {{{
    """Widget for adjusting integers or floats.
SpinScale() takes a Gtk.Adjustment,
while SpinScale.new() builds a Gtk.Adjustment from values inputted.
If logarithmic=True, the scale's adjustment will be changed
according to log(x, log_scale). This means the scale will 'accelerate'
as you get closer to extreme values."""
    def __init__(self,
                 adjustment: Gtk.Adjustment,
                 label: str = "",
                 digits: int = 0,
                 orientation: Gtk.Orientation = Gtk.Orientation.HORIZONTAL,
                 spin_accel: float = 0.0,
                 logarithmic: bool = False,
                 log_scale: int = 2,
                 scale_min_size: int = 200,
                 ):
        super().__init__()

        if label:
            self.label = Gtk.Label.new(label)
            self.attach_all_down(self.label, base_width=2)

        self.scale = Gtk.Scale.new(orientation, adjustment)
        self.scale.props.draw_value = False

        self.spin_button = Gtk.SpinButton.new(adjustment, spin_accel, 0)

        if orientation == Gtk.Orientation.HORIZONTAL:
            self.scale.props.hexpand = True
            direction = Gtk.DirectionType.RIGHT

            width = scale_min_size
            height = -1
        else:
            self.scale.props.vexpand = True
            self.spin_button.props.hexpand = True

            width = -1
            height = scale_min_size

            direction = Gtk.DirectionType.DOWN

        # min size request, either horizontally or vertically.
        # I had one of my scales get compressed into a single pixel before
        # so this is necessary
        self.scale.set_size_request(width, height)

        self.attach_all(direction, self.scale, self.spin_button, row=1)

        self.digits = digits
        self.__log = logarithmic
        self.__log_scale = log_scale
        self.adjustment = adjustment
        DataWidget.__init__(self, self.adjustment.props.value,
                            self.adjustment, 'value-changed')

    def new(
        value: float, min_value: float, max_value: float,
        step_increment: float, page_increment: float,
        label: str = "",
        digits: int = 0,
        orientation: Gtk.Orientation = Gtk.Orientation.HORIZONTAL,
        spin_accel: float = 0.0,
        logarithmic: bool = False,
        log_scale: float = 2,
        scale_min_size: int = 200,
    ) -> 'SpinScale':
        """Creates a new SpinScale, generating the Adjustment from vals"""

        return SpinScale(
            adjustment=Gtk.Adjustment.new(value, min_value, max_value,
                                          step_increment, page_increment, 0),
            label=label,
            digits=digits,
            orientation=orientation,
            spin_accel=spin_accel,
            logarithmic=logarithmic,
            log_scale=log_scale,
            scale_min_size=scale_min_size,
        )

    def set_main_from_log(self, *args):
        """Internal function runs when a logarithmic scale is changed,
to update the spin button."""
        if self.logarithmic:
            self.adjustment.props.value = \
                self.smart_unlog(self.scale.props.adjustment.props.value)

    def set_log_from_main(self, *args):
        """Internal function runs when a spin button is changed,
to update the logarithmic scale."""
        if self.logarithmic:
            self.scale.props.adjustment.props.value = \
                self.smart_log(self.adjustment.props.value)

    def smart_log(self, value: float) -> float:
        """Internal function that returns a value 'smartly' logarithmicized,
accounting for negatives and 0"""
        if value > 0:
            return math.log(value, self.log_scale)
        elif value == 0:
            return 0
        elif value < 0:
            return -(math.log(abs(value), self.log_scale))

    def smart_unlog(self, value: float) -> float:
        """Internal function that returns a logarithmicized value 'smartly'
de-logarithmicized, accounting for negatives and 0"""
        if value > 0:
            return self.log_scale ** value
        elif value == 0:
            return 0
        elif value < 0:
            return -(self.log_scale ** abs(value))

    @property
    def adjustment(self) -> Gtk.Adjustment:
        return self.spin_button.props.adjustment

    @adjustment.setter
    def adjustment(self, adjustment: Gtk.Adjustment):
        self.spin_button.props.adjustment = adjustment
        self.reset_value = adjustment.props.value
        self.logarithmic = self.logarithmic  # sets scale adj

    @property
    def digits(self) -> int:
        return self.spin_button.props.digits

    @digits.setter
    def digits(self, digits: int):
        self.spin_button.props.digits = digits
        self.scale.props.digits = digits

    @property
    def logarithmic(self) -> bool:
        return self.__log

    @logarithmic.setter
    def logarithmic(self, value: bool):
        self.__log = value
        if value:
            self.__log_adj = Gtk.Adjustment.new(
                value=self.smart_log(self.adjustment.props.value),
                lower=self.smart_log(self.adjustment.props.lower),
                upper=self.smart_log(self.adjustment.props.upper),
                step_increment=self.smart_log(
                    self.adjustment.props.step_increment),
                page_increment=self.smart_log(
                    self.adjustment.props.page_increment),
                page_size=self.smart_log(self.adjustment.props.page_size),
            )
            self.__log_adj.connect("value-changed", self.set_main_from_log)
            self.adjustment.connect("value-changed", self.set_log_from_main)
            self.scale.props.adjustment = self.__log_adj
        else:
            self.scale.props.adjustment = self.adjustment

    @property
    def log_scale(self) -> float:
        return self.__log_scale

    @log_scale.setter
    def log_scale(self, value: float):
        """Must be > 1"""
        assert value > 1
        self.__log_scale = value
        self.logarithmic = self.logarithmic

    @property
    def value(self) -> float:
        if self.digits > 0:
            return float(f'%.{self.digits}f' % (self.adjustment.props.value))

        else:
            return int(f'%.{self.digits}f' % (self.adjustment.props.value))

    @value.setter
    def value(self, value: float):
        self.adjustment.props.value = value
        if self.logarithmic:
            self.scale.props.adjustment.props.value = \
                math.log(value, self.log_scale)
    # }}}
