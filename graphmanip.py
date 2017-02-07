import inspect
import math
from math import pi as PI
import tkinter
from functools import wraps

import cairo
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
        u, v = min(u, v, key=id), max(u, v, key=id)
        self.u, self.v, self.w = u, v, w

    @property
    def endpoint_ids(self):
        return (id(self.u), id(self.v))

    def render(self, context):
        context.move_to(self.u.x, self.u.y)
        context.line_to(self.v.x, self.v.y)
        context.set_source_rgba(0, 0, 0, 1)
        context.set_line_width(max(context.device_to_user_distance(1, 1)))
        context.stroke()
        context.set_line_width(0)
        context.move_to(self.u.x + (self.v.x - self.u.x) / 2,
                        self.u.y + (self.v.y - self.u.y) / 2)
        context.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(13)
        context.show_text(str(self.w))
        context.new_path()

    def __str__(self):
        return f'<Edge {self.w}>'

    @property
    def x0(self):
        return min(self.u.x, self.v.x)

    @property
    def x1(self):
        return max(self.u.x, self.v.x)

    @property
    def y0(self):
        return min(self.u.y, self.v.y)

    @property
    def y1(self):
        return max(self.u.y, self.v.y)

    def dist(self, x, y):
        # TODO verify this
        px = x - self.u.x
        py = y - self.u.y
        p_dist = math.sqrt(px ** 2 + py ** 2)
        vx = self.v.x - self.u.x
        vy = self.v.y - self.u.y
        p_angle = math.atan2(py, px)
        v_angle = math.atan2(vy, vx)
        angle = min((p_angle - v_angle) % (2*PI),
                    (v_angle - p_angle) % (2*PI))
        return p_dist * math.sin(angle)


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
        self.edges = {}
        self.edge_by_weight = []
        self.current_node = None
        self.current_coro = self.current_future = None
        self.futures = GraphFutures(self)

        self.bind('<Button>', self.dispatch_event)
        self.bind('<ButtonRelease>', self.dispatch_event)
        self.bind('<Configure>', self.on_configure)
        self.event_handler = {
            (tkinter.EventType.ButtonPress, 1): self.on_left_pressed,
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
        if nodes:
            dist, closest = min(((n.x - x) ** 2 + (n.y - y) ** 2, n)
                                for n in nodes)
            if dist < r ** 2:
                return closest

    def find_edge(self, x, y, device_tol=5):
        tol = device_tol / self.surface.current_scale()
        edges = [e for e in self.edges.values()
                 if e.x0 <= x <= e.x1 and e.y0 <= y <= e.y1]
        for e in edges:
            dist, closest = min((e.dist(x, y), e) for e in edges)
            if dist < tol ** 2:
                return closest

    def add_node(self, x, y):
        n = Node(x, y, self.NODE_RADIUS)
        self.nodes.append(n)
        self.surface.add(n)
        self.surface.redraw()
        return n

    def find_or_add_node(self, x, y):
        return self.find_node(x, y) or self.add_node(x, y)

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
            print(f"Warning: Closing current coro {self.current_coro}")
            self.current_coro.close()
        self.current_coro = coro
        self.current_future = future

    async def on_left_pressed(self, x, y, ev):
        u = self.find_node(x, y)
        if u:
            await self.add_edge_from(u)
            return
        e = self.find_edge(x, y)
        if e:
            del self.edges[e.endpoint_ids]
            for o in self.edge_by_weight[e.w+1:]:
                o.w -= 1
            print(e.w, self.edge_by_weight)
            del self.edge_by_weight[e.w]
            self.surface.remove(e)
            self.surface.redraw()
            return
        await self.add_edge_from(self.add_node(x, y))

    async def add_edge_from(self, u):
        x, y = await self.futures.left_released()
        v = self.find_or_add_node(x, y)
        e = Edge(u, v, len(self.edges))
        if self.edges.setdefault(e.endpoint_ids, e) is e:
            self.edge_by_weight.append(e)
            self.surface.add(e)
            self.surface.redraw()
        else:
            print(f'Edge {e} already exists')

    def on_scroll_up(self, x, y, ev):
        self.surface.zoom(x, y, self.SCROLL_SCALE)

    def on_scroll_down(self, x, y, ev):
        self.surface.zoom(x, y, 1/self.SCROLL_SCALE)


if __name__ == "__main__":
    GraphManipulator()
