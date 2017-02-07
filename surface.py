from functools import partial, wraps

import numpy as np
import tkinter
import PIL.Image
import PIL.ImageTk
import cairo
from priolist import PriorityList


def save_restore(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        self.context.save()
        result = fn(self, *args, **kwargs)
        self.context.restore()
        return result

    return wrapper


class Surface:
    def __init__(self, parent, w, h):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context = cairo.Context(self.surface)

        self._image_ref = PIL.ImageTk.PhotoImage('RGBA', (w, h))
        self.drawables = PriorityList()
        self.redraw()

        self.label = tkinter.Label(parent, image=self._image_ref)

    def add(self, drawable):
        priority = drawable.layer
        self.drawables.add(priority, drawable)

    def remove(self, drawable):
        priority = drawable.layer
        self.drawables.remove(priority, drawable)

    def pack(self, *args, **kwargs):
        self.label.pack(*args, **kwargs)

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()

    def resize(self, w, h):
        cur_x0 = self.context.device_to_user(0, 0)[0]
        cur_x1 = self.context.device_to_user(self.width, 0)[0]
        cur_x = cur_x0 + (cur_x1 - cur_x0) / 2
        cur_y0 = self.context.device_to_user(0, 0)[1]
        cur_y1 = self.context.device_to_user(0, self.height)[1]
        cur_y = cur_y0 + (cur_y1 - cur_y0) / 2
        # new_scale = min(h / (cur_y1 - cur_y0), w / (cur_x1 - cur_x0))
        new_scale = (h / (cur_y1 - cur_y0) if self.height < self.width else
                     w / (cur_x1 - cur_x0))
        new_user_width = w / new_scale
        new_user_height = h / new_scale

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context.identity_matrix()
        self.context = cairo.Context(self.surface)
        self.context.scale(new_scale, new_scale)
        self.context.translate(-cur_x, -cur_y)
        self.context.translate(new_user_width / 2, new_user_height / 2)
        self._image_ref = PIL.ImageTk.PhotoImage('RGBA', (w, h))
        self.label.configure(image=self._image_ref)
        self.pack(expand=True, fill="both")
        self.redraw()

    def _update(self):
        w, h = self.surface.get_width(), self.surface.get_height()
        surface_data = self.surface.get_data().obj
        img = PIL.Image.frombytes("RGBA", (w, h), surface_data,
                                  "raw", "BGRA", 0, 1)
        self._image_ref.paste(img)

    def redraw(self):
        self.context.save()
        self.context.set_source_rgba(1, 1, 1, 1)
        self.context.paint()
        self.context.restore()
        for o in self.drawables:
            self.context.save()
            o.render(self.context)
            self.context.restore()
        self._update()

    def circle_device_radius(self, x, y, device_radius):
        x, y = self.context.user_to_device(x, y)
        class Circle:
            layer = 5
            def render(self, context):
                context.identity_matrix()
                context.translate(x, y)
                context.arc(0, 0, device_radius, 0, 2*np.pi)
                context.set_source_rgba(1, 0, 0, 0.8)
                context.fill()
        self.add(Circle())
        self.redraw()

    def _poly(self, *points):
        self.context.move_to(*points[0])
        for p in points[1:]:
            self.context.line_to(*p)
        self.context.close_path()
        self.context.set_source_rgba(1, 0, 0, 0.8)
        self.context.fill()

    @save_restore
    def poly(self, *points):
        self._poly(*points)

    def zoom(self, x, y, f):
        self.context.translate(x, y)
        self.context.scale(f, f)
        self.context.translate(-x, -y)
        self.redraw()

    def current_scale(self):
        return self.context.user_to_device_distance(1, 0)[0]

    def device_to_user(self, x, y):
        return self.context.device_to_user(x, y)
