from math import pi as PI
import tkinter
from functools import wraps

from surface import Surface


class Node:
    layer = 10

    def __init__(self, x, y, r):
        self.x, self.y, self.r = x, y, r

    def render(self, context):
        x, y = context.user_to_device(self.x, self.y)
        context.identity_matrix()
        context.translate(x, y)
        context.arc(0, 0, self.r, 0, 2*PI)
        context.set_source_rgba(1, 0, 0, 1)
        context.fill_preserve()
        context.set_source_rgba(0, 0, 0, 1)
        context.set_line_width(max(context.device_to_user_distance(1, 1)))
        context.stroke()

    def __str__(self):
        return f'<Node {self.x},{self.y}>'


class Edge:
    layer = 5

    def __init__(self, u, v, w):
        self.u, self.v, self.w = u, v, w

    def render(self, context):
        context.move_to(self.u.x, self.u.y)
        context.line_to(self.v.x, self.v.y)
        context.set_source_rgba(0, 0, 0, 1)
        context.set_line_width(max(context.device_to_user_distance(1, 1)))
        context.stroke()
        # TODO draw weight

    def __str__(self):
        return f'<Edge {self.w}>'


class FutureEvent:
    def __init__(self, event_type: tkinter.EventType, num: int):
        self.event_type = event_type
        self.num = num

    def __await__(self):
        ev = yield self
        assert self.filter(ev)
        return ev

    def filter(self, ev: tkinter.Event):
        return ev.type == self.event_type and ev.num == self.num


class GraphFutures:
    def __init__(self, graph_manipulator):
        self.graph_manipulator = graph_manipulator

    @property
    def surface(self):
        return self.graph_manipulator.surface

    def get_event_xy(self, event):
        return self.surface.device_to_user(event.x, event.y)

    async def left_pressed(self):
        ev = await FutureEvent(tkinter.EventType.ButtonPress, 1)
        return self.get_event_xy(ev)

    async def left_released(self):
        ev = await FutureEvent(tkinter.EventType.ButtonRelease, 1)
        return self.get_event_xy(ev)

    async def right_pressed(self):
        ev = await FutureEvent(tkinter.EventType.ButtonPress, 3)
        return self.get_event_xy(ev)

    async def right_released(self):
        ev = await FutureEvent(tkinter.EventType.ButtonRelease, 3)
        return self.get_event_xy(ev)


class GraphManipulator(tkinter.Tk):
    SCROLL_SCALE = 5/4
    NODE_RADIUS = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.points = []

        w, h = 800, 600

        self.geometry("{}x{}".format(w, h))

        self.surface = Surface(self, w, h)
        self.surface.pack(expand=True, fill='both')

        self.nodes = []
        self.edges = []
        self.current_node = None
        self.current_coro = self.current_future = None

        self.bind('<Button>', self.dispatch_event)
        self.bind('<ButtonRelease>', self.dispatch_event)
        self.bind('<Configure>', self.on_configure)
        self.event_handler = {
            (tkinter.EventType.ButtonPress, 1): self.on_left_pressed,
            (tkinter.EventType.ButtonRelease, 1): self.on_left_released,
            (tkinter.EventType.ButtonPress, 4): self.on_scroll_up,
            (tkinter.EventType.ButtonRelease, 5): self.on_scroll_down,
        }

        self.mainloop()

    def on_configure(self, ev: tkinter.Event):
        cur_w, cur_h = self.surface.width, self.surface.height
        w, h = ev.width, ev.height
        if (cur_w, cur_h) != (w, h):
            self.surface.resize(w, h)

    def find_node(self, x, y):
        r = self.NODE_RADIUS / self.surface.current_scale()
        x0 = x - r
        x1 = x + r
        y0 = y - r
        y1 = y + r
        nodes = [n for n in self.nodes
                 if x0 <= n.x <= x1 and y0 <= n.y <= y1]
        print(f'{len(nodes)} candidate close nodes')
        if nodes:
            dist, closest = min(((n.x - x) ** 2 + (n.y - y) ** 2, n)
                                for n in nodes)
            print(f'Closest at distance {dist} (comp. {r**2})')
            if dist < r ** 2:
                return closest

    def find_or_add_node(self, x, y):
        n = self.find_node(x, y)
        if not n:
            print(f'Add node at {x} {y}')
            n = Node(x, y, self.NODE_RADIUS)
            self.nodes.append(n)
            self.surface.add(n)
            self.surface.redraw()
        return n

    def dispatch_event(self, ev):
        if self.current_future and self.current_future.filter(ev):
            try:
                future = self.current_coro.send(ev)
            except StopIteration:
                self.current_coro = self.current_future = None
            else:
                self.current_future = future
            return
        try:
            fn = self.handlers[ev.type, ev.num]
        except KeyError:
            pass
        else:
            x, y = self.surface.device_to_user(ev.x, ev.y)
            fn(x, y, ev)

    def on_left_pressed(self, x, y, ev):
        self.current_node = self.find_or_add_node(x, y)

    def on_left_released(self, x, y, ev):
        if self.current_node is None:
            print('left_released: current_node is None')
            return
        n = self.find_or_add_node(x, y)
        if n != self.current_node:
            e = Edge(self.current_node, n, len(self.edges))
            self.current_node = None
            self.edges.append(e)
            self.surface.add(e)
            self.surface.redraw()

    def on_scroll_up(self, x, y, ev):
        self.surface.zoom(x, y, self.SCROLL_SCALE)

    def on_scroll_down(self, x, y, ev):
        self.surface.zoom(x, y, 1/self.SCROLL_SCALE)


if __name__ == "__main__":
    GraphManipulator()
