import inspect
from functools import wraps

import tkinter
import PIL.Image
import PIL.ImageTk
import cairoshim as cairo
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

    def zoom(self, x, y, f):
        self.context.translate(x, y)
        self.context.scale(f, f)
        self.context.translate(-x, -y)
        self.redraw()

    def current_scale(self):
        return self.context.user_to_device_distance(1, 0)[0]

    def device_to_user(self, x, y):
        return self.context.device_to_user(x, y)


try:
    from tkinter import EventType
except ImportError:
    import enum
    class EventType(str, enum.Enum):
        KeyPress = '2'
        Key = KeyPress,
        KeyRelease = '3'
        ButtonPress = '4'
        Button = ButtonPress,
        ButtonRelease = '5'
        Motion = '6'
        Enter = '7'
        Leave = '8'
        FocusIn = '9'
        FocusOut = '10'
        Keymap = '11'           # undocumented
        Expose = '12'
        GraphicsExpose = '13'   # undocumented
        NoExpose = '14'         # undocumented
        Visibility = '15'
        Create = '16'
        Destroy = '17'
        Unmap = '18'
        Map = '19'
        MapRequest = '20'
        Reparent = '21'
        Configure = '22'
        ConfigureRequest = '23'
        Gravity = '24'
        ResizeRequest = '25'
        Circulate = '26'
        CirculateRequest = '27'
        Property = '28'
        SelectionClear = '29'   # undocumented
        SelectionRequest = '30' # undocumented
        Selection = '31'        # undocumented
        Colormap = '32'
        ClientMessage = '33'    # undocumented
        Mapping = '34'          # undocumented
        VirtualEvent = '35',    # undocumented
        Activate = '36',
        Deactivate = '37',
        MouseWheel = '38',
        def __str__(self):
            return self.name


class FutureEvent:
    def __init__(self, event_type, num: int):
        self.event_type = event_type
        self.num = num

        which = {1: 'left', 3: 'right'}.get(num, '?')
        whats = {EventType.ButtonPress: 'Press',
                 EventType.ButtonRelease: 'Release'}
        what = whats.get(event_type, '?')
        self.help = '%s the %s mouse button' % (what, which)

    def __await__(self):
        ev = yield self
        assert self.filter(ev)
        return ev

    def filter(self, ev: tkinter.Event):
        return ev.type == self.event_type and ev.num == self.num


class SurfaceFutures:
    def __init__(self, interactive_surface):
        self.interactive_surface = interactive_surface

    @property
    def surface(self):
        return self.interactive_surface.surface

    def get_event_xy(self, event):
        return self.surface.device_to_user(event.x, event.y)

    async def left_pressed(self):
        ev = await FutureEvent(EventType.ButtonPress, 1)
        return self.get_event_xy(ev)

    async def left_released(self):
        ev = await FutureEvent(EventType.ButtonRelease, 1)
        return self.get_event_xy(ev)

    async def right_pressed(self):
        ev = await FutureEvent(EventType.ButtonPress, 3)
        return self.get_event_xy(ev)

    async def right_released(self):
        ev = await FutureEvent(EventType.ButtonRelease, 3)
        return self.get_event_xy(ev)


class InteractiveSurface(tkinter.Tk):
    SCROLL_SCALE = 5/4
    INITIAL_SIZE = 800, 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        w, h = self.INITIAL_SIZE
        self.geometry("{}x{}".format(w, h))
        self.surface = Surface(self, w, h)
        self.surface.pack(expand=True, fill='both')

        self.current_node = None
        self.current_coro = self.current_future = None
        self.futures = SurfaceFutures(self)

        self.bind('<Button>', self.dispatch_event)
        self.bind('<ButtonRelease>', self.dispatch_event)
        self.bind('<Configure>', self.on_configure)

        self.event_handler = {
            (EventType.ButtonPress, 4): self.on_scroll_up,
            (EventType.ButtonRelease, 5): self.on_scroll_down,
        }

    def on_configure(self, ev: tkinter.Event):
        cur_w, cur_h = self.surface.width, self.surface.height
        w, h = ev.width, ev.height
        if (cur_w, cur_h) != (w, h):
            self.surface.resize(w, h)

    def dispatch_event(self, ev):
        if self.current_future and self.current_future.filter(ev):
            try:
                future = self.current_coro.send(ev)
            except StopIteration:
                self.current_coro = self.current_future = None
            else:
                self.current_future = future
                print(future.help)
            return
        try:
            fn = self.event_handler[ev.type, ev.num]
        except KeyError:
            pass
        else:
            x, y = self.surface.device_to_user(ev.x, ev.y)
            res = fn(x, y, ev)
            if inspect.iscoroutine(res):
                self.set_coro(res)

    def set_coro(self, coro):
        try:
            future = coro.send(None)
        except StopIteration:
            return
        if self.current_coro:
            print("Warning: Closing current coro %s" % self.current_coro)
            self.current_coro.close()
        self.current_coro = coro
        self.current_future = future
        print(future.help)

    def on_scroll_up(self, x, y, ev):
        self.surface.zoom(x, y, self.SCROLL_SCALE)

    def on_scroll_down(self, x, y, ev):
        self.surface.zoom(x, y, 1/self.SCROLL_SCALE)
