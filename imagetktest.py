import tkinter

from surface import Surface


class ExampleGui(tkinter.Tk):
    SCROLL_SCALE = 5/4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.points = []

        w, h = 800, 600

        self.geometry("{}x{}".format(w, h))

        self.surface = Surface(self, w, h)
        self.surface.pack(expand=True, fill='both')

        self.bind('<Button>', self.on_press)
        self.bind('<ButtonRelease>', self.on_release)
        self.bind('<Configure>', self.on_configure)

        self.mainloop()

    def on_configure(self, ev: tkinter.Event):
        cur_w, cur_h = self.surface.width, self.surface.height
        w, h = ev.width, ev.height
        if (cur_w, cur_h) != (w, h):
            self.surface.resize(w, h)

    def on_release(self, ev):
        assert ev.type == tkinter.EventType.ButtonRelease, ev

    def on_press(self, ev):
        assert ev.type == tkinter.EventType.ButtonPress, ev
        x, y = self.surface.device_to_user(ev.x, ev.y)
        print(f"Clicked button={ev.num} x={x} y={y}")
        try:
            method = getattr(self, 'on_press_%s' % ev.num)
        except AttributeError:
            pass
        else:
            method(x, y)

    def on_press_1(self, x, y):
        self.surface.circle_device_radius(x, y, 20)
        self.points.append((x, y))

    def on_press_3(self, x, y):
        self.surface.circle_device_radius(x, y, 20)
        self.points.append((x, y))
        if len(self.points) >= 3:
            self.surface.poly(*self.points)
        del self.points[:]

    def on_press_4(self, x, y):
        self.surface.zoom(x, y, self.SCROLL_SCALE)

    def on_press_5(self, x, y):
        self.surface.zoom(x, y, 1/self.SCROLL_SCALE)


if __name__ == "__main__":
    ExampleGui()
