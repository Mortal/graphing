class Surface:
    def __init__(self, parent, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context = cairo.Context(self.surface)

        self._image_ref = PIL.ImageTk.PhotoImage('RGBA', (w, h))
        self.draw_history = []
        self.redraw()

        self.label = tkinter.Label(parent, image=self._image_ref)

    def pack(self, *args, **kwargs):
        self.label.pack(*args, **kwargs)

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()

    def resize(self, w, h):
        cur_w, cur_h = width, height
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

    def update(self):
        w, h = self.surface.get_width(), self.surface.get_height()
        surface_data = self.surface.get_data().obj
        img = PIL.Image.frombytes("RGBA", (w, h), surface_data, "raw", "BGRA", 0, 1)
        self._image_ref.paste(img)

    def redraw(self):
        self.context.save()
        self.context.set_source_rgba(1, 1, 1, 1)
        self.context.paint()
        self.context.restore()
        for call in self.draw_history:
            call()
        self.update()
