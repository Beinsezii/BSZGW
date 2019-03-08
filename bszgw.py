#!/usr/bin/python3
"""A GTK simplifier."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk




class App(Gtk.Window):
    def __init__(self, label, widget):
        super(App, self).__init__()
        self.connect("destroy", Gtk.main_quit)
        self.props.title = label
        self.add(widget)

    def launch(self, *prelaunch):
        self.present()
        self.show_all()
        for x in prelaunch:
            if len(x) == 1:
                x[0]()
            else:
                x[0](*x[1:])
        Gtk.main()




TEST_ARRAY = [
[Gtk.Label("1"), Gtk.Label("2"), "50x50", Gtk.Label("3")],
[Gtk.Label("4"), Gtk.Label("5"), Gtk.Label("6"), [Gtk.Label("a"),
                                                 [Gtk.Label("b"), Gtk.Label("c")],
                                                  Gtk.Label("d")]],
[Gtk.Label("7"), Gtk.Label("8"), Gtk.Label("9")]
]


def AutoBox(big_list, vspacing = 5, hspacing = 15, orientation=Gtk.Orientation.VERTICAL):
    sub_orientation = 1 if orientation == 0 else 0
    box = Gtk.Box.new(orientation, vspacing if orientation==Gtk.Orientation.VERTICAL else hspacing)

    for x in big_list:
        if isinstance(x, (list, tuple)):
            x = AutoBox(x, vspacing, hspacing, sub_orientation)
        elif isinstance(x, str):
            dimensions = x.casefold().split('x')
            x = Gtk.Label.new(None)
            x.set_size_request(int(dimensions[0]), int(dimensions[1]))
        if len(big_list) == 1: return x
        if x != None: box.pack_start(x, True, True, 0)

    if not box.get_children(): return None
    return box




class Adjuster(Gtk.Box):
    """DOCSTRING TODO"""
    def __init__(self, label, value, min_value, max_value, step_increment, page_increment, decimals=0, orientation=Gtk.Orientation.HORIZONTAL, tooltip=None, spinner=True, slider=True, slider_size=200):
        super(Adjuster, self).__init__()
        self.decimals = decimals
        self.props.orientation = Gtk.Orientation.VERTICAL

        self.label = Gtk.Label.new(label)
        self.pack_start(self.label, False, True, 0)

        self.adjustment = Gtk.Adjustment.new(value, min_value, max_value, step_increment, page_increment, 0)
        self.adjuster_box = Gtk.Box.new(orientation, 0)
        self.pack_start(self.adjuster_box, True, True, 0)

        if slider:
            self.slider = Gtk.Scale.new(orientation, self.adjustment)
            self.slider.props.draw_value=not spinner
            self.slider.props.digits=self.decimals
            if orientation == Gtk.Orientation.HORIZONTAL:
                width = slider_size
                height = -1
            else:
                self.slider.props.value_pos=Gtk.PositionType.LEFT
                width = -1
                height = slider_size
            self.slider.set_size_request(width, height)
            self.adjuster_box.pack_start(self.slider, True, True, 0)
            if tooltip:
                self.slider.props.tooltip_text=tooltip

        if spinner:
            self.spinner = Gtk.SpinButton.new(self.adjustment, step_increment, self.decimals)
            self.adjuster_box.pack_start(self.spinner, not slider, True, 0)
            if tooltip:
                self.spinner.props.tooltip_text=tooltip

    @property
    def value(self):
        return float(f'%.{self.decimals}f'%(self.adjustment.props.value)) if self.decimals > 0 else int(f'%.{self.decimals}f'%(self.adjustment.props.value))

    @value.setter
    def value(self, new_value):
        self.adjustment.props.value=new_value




class CheckBox(Gtk.CheckButton):
    """Basically just a normal GTK checkbutton with the 'value' variable I like to use.
    Possibly overkill."""
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
                if not isinstance(x, (list, tuple)):
                    x = [x, x]
                self.values.append(x[1])
                self.append_text(str(x[0]))
            else:
                self.append_text(str(x))
        self.value=value

    @property
    def value(self):
        if self.get_active() == -1: return None
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




class RadioButtons(Gtk.Box):
    """DOCSTRING TODO"""
    def __init__(self, label, buttons, value, orientation=Gtk.Orientation.VERTICAL, enums=False, tooltip=None):
        assert len(buttons)>1
        super(RadioButtons, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.enums = enums
        self.buttons_box = Gtk.Box.new(orientation, 5)
        self.label = Gtk.Label.new(label)
        self.pack_start(self.label, False, True, 0)
        self.pack_start(self.buttons_box, True, True, 0)
        self.radio_buttons = []
        if self.enums:
            self.values=[]
        for num, var in enumerate(buttons):
            self.radio_buttons.append(Gtk.RadioButton.new_with_label(None, str(var) if not self.enums else str(var[0])))
            self.buttons_box.pack_start(self.radio_buttons[num], True, True, 0)
            if num>0:
                self.radio_buttons[num].join_group(self.radio_buttons[0])
            if self.enums:
                self.values.append(var[1])
            if tooltip: self.radio_buttons[num].set_tooltip_text(tooltip)
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
    def __init__(self, label, value, multi_line = True, size="200x100"):
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
        if self.multi_line: self.scroll_box.set_min_content_height(int(sizes[1]))
        self.value = value

    @property
    def value(self):
        if self.multi_line:
            bounds = self.text_buffer.get_bounds()
            return self.text_buffer.get_text(bounds[0], bounds[1], True)
        else: return self.text_buffer.get_text()

    @value.setter
    def value(self, new_value):
        self.text_buffer.set_text(new_value, -1)




if __name__ == "__main__":

    test_adjuster = Adjuster("Test Adjuster", 30, 0, 100, 5, 10)
    test_adjuster2 = Adjuster("Test Adjuster2", 30, 0, 100, 5, 10, decimals = 1, slider=False)
    test_check = CheckBox("Test Check Box", True)
    test_drop_down= DropDown("Test Drop Down", [["Choice A", "A"], ["Choice B", "B"], ["Choice C", "C"]], "A", enums=True)
    test_radio = RadioButtons("Test Radio Buttons", ["Choice A", "Choice B", "Choice C"], 0)
    test_text_box = TextBox("Test Text Box", "Test Text\nLine 2")
    def get_vals(widget):
        for x in [test_adjuster, test_adjuster2, test_check, test_drop_down, test_radio, test_text_box]:
            print(x.value)
    execbutton = Gtk.Button("Execute")
    execbutton.connect("clicked", get_vals)
    test_app = App("Test App", AutoBox([
        [test_adjuster, [[test_adjuster2, test_drop_down],test_radio]],
        [test_text_box, [test_check, execbutton]]
        ], orientation=Gtk.Orientation.HORIZONTAL))
    test_app.launch()