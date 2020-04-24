#!/usr/bin/python3
"""MAIN STRING TODO"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk
import math  # noqa: F401


class App(Gtk.Window):
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


def AutoBox(big_list, vspacing=5, hspacing=15,
            orientation=Gtk.Orientation.VERTICAL):
    """DOCSTRING TODO"""
    sub_orientation = 1 if orientation == 0 else 0
    box = Gtk.Box.new(
        orientation,
        vspacing if orientation == Gtk.Orientation.VERTICAL else hspacing
    )

    for x in big_list:
        exp = True
        fill = True
        pad = 0
        if isinstance(x, list):
            x = AutoBox(x, vspacing, hspacing, sub_orientation)

        elif isinstance(x, tuple):
            x, exp, fill, pad = x

        elif isinstance(x, str):
            dimensions = x.casefold().split('x')
            x = Gtk.Label.new(None)
            x.set_size_request(int(dimensions[0]), int(dimensions[1]))

        if len(big_list) == 1:
            return x

        if x is not None:
            box.pack_start(x, exp, fill, pad)

    if not box.get_children():
        return None

    return box


class Adjuster(Gtk.Box):
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
                 spin_button: bool = True,
                 scale: bool = True,
                 spin_accel: float = 0.0,
                 logarithmic: bool = False,
                 log_scale: int = 2,
                 scale_min_size: int = 200):
        super(Adjuster, self).__init__()

        # Main box always vertical for label on top
        self.props.orientation = Gtk.Orientation.VERTICAL

        # log is a one-stop shop. Must have both widgets and can't be reverted.
        # probably possible to make it changeable-on-the-fly but I've written
        # enough code for now.
        assert spin_button or scale
        if logarithmic:
            assert spin_button and scale and log_scale > 1
        self.__log = logarithmic
        self.__ls = log_scale

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

    def __log_update(self, *args):
        """Internal function runs when a logarithmic scale is changed,
to update the non-logarithmic scale."""
        if self.__log:
            self.adjustment.props.value = \
                self.__ls ** self.scale.get_adjustment().props.value

    @property
    def adjustment(self):
        if hasattr(self, 'spin_button'):
            return self.spin_button.get_adjustment()
        elif hasattr(self, 'scale'):
            return self.scale.get_adjustment()
        # don't need log check.

    @adjustment.setter
    def adjustment(self, new_adjust):
        if hasattr(self, 'spin_button'):
            self.spin_button.set_adjustment(new_adjust)
        if hasattr(self, 'scale'):
            # if log, create a separate Gtk.Adjustment connected to
            # __log_update()
            if self.__log:
                low = new_adjust.props.lower
                # only log the lower limit if above 0
                if low > 0:
                    newlow = math.log(low, self.__ls)
                else:
                    newlow = low

                # logs the upper, possibly lower (above), and value.
                # to base self.__ls
                log_adjust = Gtk.Adjustment.new(
                    value=math.log(new_adjust.props.value, self.__ls),
                    lower=newlow,
                    upper=math.log(new_adjust.props.upper, self.__ls),
                    step_increment=new_adjust.props.step_increment,
                    page_increment=new_adjust.props.page_increment,
                    page_size=new_adjust.props.page_size
                )
                log_adjust.connect("value-changed", self.__log_update)
                self.scale.set_adjustment(log_adjust)
            else:
                self.scale.set_adjustment(new_adjust)

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
    def value(self):
        if self.decimals > 0:
            return float(f'%.{self.decimals}f' % (self.adjustment.props.value))

        else:
            return int(f'%.{self.decimals}f' % (self.adjustment.props.value))

    @value.setter
    def value(self, new_value):
        self.adjustment.props.value = new_value
        if self.__log:
            self.scale.get_adjustment().props.value = \
                math.log(new_value, self.__ls)

    def new(label,
            value, min_value, max_value, step_increment, page_increment,
            decimals=0, orientation=Gtk.Orientation.HORIZONTAL,
            tooltip=None, spin_button=True, scale=True, spin_accel=0.0,
            logarithmic=False, log_scale=2, scale_min_size=200):

        return Adjuster(label, Gtk.Adjustment.new(value, min_value, max_value,
                        step_increment, page_increment, 0),
                        decimals, orientation, tooltip, spin_button, scale,
                        spin_accel, logarithmic, log_scale, scale_min_size)


class Button(Gtk.Button):
    """Basically just a normal GTK button with connect() built in"""
    def __init__(self, label, value, tooltip=None):
        super(Button, self).__init__(label)
        if tooltip:
            self.set_tooltip_text(tooltip)
        self.value = value

    @property
    def value(self):
        pass

    @value.setter
    def value(self, new_value):
        if callable(new_value):
            self.connect("clicked", new_value)
        else:
            print(f"'{new_value}' not callable.")
            raise ValueError


class CheckBox(Gtk.CheckButton):
    """Basically just a normal GTK checkbutton with the 'value' property
and other tiny additions.  Possibly overkill."""
    def __init__(self, label, value, tooltip=None):
        super(CheckBox, self).__init__(label)
        if tooltip:
            self.set_tooltip_text(tooltip)
        self.value = value

    @property
    def value(self):
        return self.get_active()

    @value.setter
    def value(self, new_value):
        self.set_active(new_value)


class DropDown(Gtk.ComboBoxText):
    """DOCSTRING TODO"""
    def __init__(self, tooltip, vals_list, value, enums=False):
        super(DropDown, self).__init__()
        self.enums = enums
        self.set_tooltip_text(tooltip)
        if self.enums:
            self.values = []
        for x in vals_list:
            if self.enums:
                if isinstance(vals_list, dict):
                    x = [x, vals_list[x]]
                elif not isinstance(x, (list, tuple)):
                    x = [x, x]
                self.values.append(x[1])
                self.append_text(str(x[0]))
            else:
                self.append_text(str(x))
        self.value = value

    @property
    def value(self):
        if self.get_active() == -1:
            return None
        if self.enums:
            return self.values[self.get_active()]
        else:
            return self.get_active()

    @value.setter
    def value(self, new_value):
        if self.enums:
            self.set_active(self.values.index(new_value))
        else:
            self.set_active(new_value)


def Message(message):
    dialog = Gtk.MessageDialog(text=message, buttons=Gtk.ButtonsType.CLOSE)
    dialog.run()
    dialog.destroy()


class RadioButtons(Gtk.Box):
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
                self.radio_buttons[num].set_tooltip_text(tooltip)

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


class TextBox(Gtk.Box):
    """DOCSTRING TODO"""
    def __init__(self, label, value, multi_line=True, size="200x100"):
        super(TextBox, self).__init__()
        self.multi_line = multi_line
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.label = Gtk.Label.new(label)
        self.pack_start(self.label, False, True, 0)

        if self.multi_line:
            self.text_box = Gtk.TextView.new()

        else:
            self.text_box = Gtk.Entry.new()

        self.text_buffer = self.text_box.get_buffer()
        self.scroll_box = Gtk.ScrolledWindow.new(None, None)
        self.scroll_box.add(self.text_box)
        self.pack_start(self.scroll_box, True, True, 0)
        sizes = size.casefold().split("x")
        self.scroll_box.set_min_content_width(int(sizes[0]))

        if self.multi_line:
            self.scroll_box.set_min_content_height(int(sizes[1]))

        self.value = value

    @property
    def value(self):
        if self.multi_line:
            bounds = self.text_buffer.get_bounds()
            return self.text_buffer.get_text(bounds[0], bounds[1], True)

        else:
            return self.text_buffer.get_text()

    @value.setter
    def value(self, new_value):
        self.text_buffer.set_text(new_value, -1)
