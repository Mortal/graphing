from functools import partial, wraps

import numpy as np
import tkinter
import PIL.Image
import PIL.ImageTk
import cairo


def save_restore(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        self.context.save()
        result = fn(self, *args, **kwargs)
        self.context.restore()
        return result

    return wrapper


def draw_history(fn):
    fn = save_restore(fn)

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        self.draw_history.append(partial(fn, self, *args, **kwargs))
        self.draw_history[-1]()
        self.paste()

    return wrapper


class ExampleGui(tkinter.Tk):
    SCROLL_SCALE = 5/4

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
        self.bind('<Configure>', self.on_configure)

        self.mainloop()

    def on_configure(self, ev: tkinter.Event):
        cur_w, cur_h = self.surface.get_width(), self.surface.get_height()
        w, h = ev.width, ev.height
        if (cur_w, cur_h) != (w, h):
            cur_x0 = self.context.device_to_user(0, 0)[0]
            cur_x1 = self.context.device_to_user(cur_w, 0)[0]
            cur_y0 = self.context.device_to_user(0, 0)[1]
            cur_y1 = self.context.device_to_user(0, cur_h)[1]
            new_scale = min(h / (cur_y1 - cur_y0), w / (cur_x1 - cur_x0))

            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
            self.context = cairo.Context(self.surface)
            self.context.translate(cur_x0, cur_y0)
            self.context.scale(new_scale, new_scale)
            self._image_ref = PIL.ImageTk.PhotoImage('RGBA', (w, h))
            self.label.configure(image=self._image_ref)
            self.label.pack(expand=True, fill="both")
            self.redraw()

    def paste(self):
        w, h = self.surface.get_width(), self.surface.get_height()
        surface_data = self.surface.get_data().obj
        img = PIL.Image.frombytes("RGBA", (w, h), surface_data, "raw", "BGRA", 0, 1)
        self._image_ref.paste(img)

    def on_release(self, ev):
        assert ev.type == tkinter.EventType.ButtonRelease, ev

    @draw_history
    def circle_device_radius(self, x, y, device_radius):
        x, y = self.context.user_to_device(x, y)
        self.context.identity_matrix()
        self.context.translate(x, y)
        self.context.arc(0, 0, device_radius, 0, 2*np.pi)
        self.context.set_source_rgba(1, 0, 0, 0.8)
        self.context.fill()

    def _poly(self, *points):
        self.context.move_to(*points[0])
        for p in points[1:]:
            self.context.line_to(*p)
        self.context.close_path()
        self.context.set_source_rgba(1, 0, 0, 0.8)
        self.context.fill()

    @draw_history
    def poly(self, *points):
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
        self.context.scale(self.SCROLL_SCALE, self.SCROLL_SCALE)
        self.context.translate(-x, -y)
        self.redraw()

    def on_press_5(self, x, y):
        self.context.translate(x, y)
        self.context.scale(1/self.SCROLL_SCALE, 1/self.SCROLL_SCALE)
        self.context.translate(-x, -y)
        self.redraw()


if __name__ == "__main__":
    ExampleGui()
