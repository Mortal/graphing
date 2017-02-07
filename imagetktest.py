# http://stackoverflow.com/a/26189022/1570972
from functools import partial, wraps

import numpy as np
import tkinter
import PIL.Image
import PIL.ImageTk
import cairo


def draw_history(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        self.draw_history.append(partial(fn, self, *args, **kwargs))
        self.draw_history[-1]()
        self.paste()

    return wrapper


class ExampleGui(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.points = []

        w, h = 800, 600

        self.geometry("{}x{}".format(w, h))

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context = cairo.Context(self.surface)

        self._image_ref = PIL.ImageTk.PhotoImage('RGBA', (w, h))
        self.draw_history = []
        self.redraw()

        self.label = tkinter.Label(self, image=self._image_ref)
        self.label.pack(expand=True, fill="both")

        self.bind('<Button>', self.on_press)
        self.bind('<ButtonRelease>', self.on_release)

        self.mainloop()

    def paste(self):
        w, h = self.surface.get_width(), self.surface.get_height()
        surface_data = self.surface.get_data().obj
        img = PIL.Image.frombytes("RGBA", (w, h), surface_data, "raw", "BGRA", 0, 1)
        self._image_ref.paste(img)

    def on_release(self, ev):
        assert ev.type == tkinter.EventType.ButtonRelease, ev

    @draw_history
    def circle_device_radius(self, x, y, device_radius):
        print(f'Draw circle at {x},{y} with device radius {device_radius}')
        x, y = self.context.user_to_device(x, y)
        self.context.save()
        self.context.identity_matrix()
        self.context.translate(x, y)
        self.context.arc(0, 0, device_radius, 0, 2*np.pi)
        self.context.set_source_rgba(1, 0, 0, 0.8)
        self.context.fill()
        self.context.restore()

    def _poly(self, *points):
        self.context.save()
        self.context.move_to(*points[0])
        for p in points[1:]:
            self.context.line_to(*p)
        self.context.close_path()
        self.context.set_source_rgba(1, 0, 0, 0.8)
        self.context.fill()
        self.context.restore()

    @draw_history
    def poly(self, *points):
        print(f"Draw poly {points}")
        self._poly(*points)

    def redraw(self):
        self.context.save()
        self.context.set_source_rgba(1, 1, 1, 1)
        self.context.paint()
        self.context.restore()
        for call in self.draw_history:
            call()
        self.paste()

    def on_press(self, ev):
        assert ev.type == tkinter.EventType.ButtonPress, ev
        x, y = self.context.device_to_user(ev.x, ev.y)
        try:
            method = getattr(self, 'on_press_%s' % ev.num)
        except AttributeError:
            print(f"Clicked button={ev.num} x={x} y={y}")
        else:
            method(x, y)

    def on_press_1(self, x, y):
        self.circle_device_radius(x, y, 20)
        self.points.append((x, y))
        if len(self.points) == 3:
            self.poly(*self.points)
            del self.points[:]

    def on_press_4(self, x, y):
        self.context.translate(x, y)
        self.context.scale(2, 2)
        self.context.translate(-x, -y)
        self.redraw()

    def on_press_5(self, x, y):
        self.context.translate(x, y)
        self.context.scale(0.5, 0.5)
        self.context.translate(-x, -y)
        self.redraw()


if __name__ == "__main__":
    ExampleGui()
