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
        return (yield self)

    def filter(self, ev: tkinter.Event):
        return ev.type == self.event_type and ev.num == self.num


def left_click():
    return FutureEvent


class GraphFutures:
    def __init__(self, graph_manipulator):
        self.graph_manipulator = graph_manipulator

    @property
    def surface(self):
        return self.graph_manipulator.surface

    def get_event_xy(self, event):
        return self.surface.device_to_user(event.x, event.y)

    async def left_click(self):
        ev = await FutureEvent(tkinter.EventType.ButtonPress, 1)
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

        def ev_xy(f):
            @wraps(f)
            def wrapped(ev):
                x, y = self.surface.device_to_user(ev.x, ev.y)
                return f(x, y, ev)

            return wrapped

        self.bind('<Button-1>', ev_xy(self.left_pressed))
        self.bind('<ButtonRelease-1>', ev_xy(self.left_released))
        # self.bind('<Button-3>', ev_xy(self.right_click))
        self.bind('<Button-4>', ev_xy(self.scroll_up))
        self.bind('<Button-5>', ev_xy(self.scroll_down))
        self.bind('<Configure>', self.on_configure)

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

    def left_pressed(self, x, y, ev):
        self.current_node = self.find_or_add_node(x, y)

    def left_released(self, x, y, ev):
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

    def scroll_up(self, x, y, ev):
        self.surface.zoom(x, y, self.SCROLL_SCALE)

    def scroll_down(self, x, y, ev):
        self.surface.zoom(x, y, 1/self.SCROLL_SCALE)


if __name__ == "__main__":
    GraphManipulator()
