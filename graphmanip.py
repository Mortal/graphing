import string
import math
from math import pi as PI
import tkinter

import cairoshim as cairo
from surface import InteractiveSurface, EventType


class Node:
    layer = 10
    FONT_SIZE = 13

    def __init__(self, x, y, r, name):
        self.x, self.y, self.r = x, y, r
        self.name = name

    def render(self, context: cairo.Context):
        x, y = context.user_to_device(self.x, self.y)
        context.identity_matrix()
        context.translate(x, y)
        context.arc(0, 0, self.r, 0, 2*PI)
        context.set_source_rgba(1, 0, 0, 1)
        context.fill_preserve()
        context.set_source_rgba(0, 0, 0, 1)
        context.set_line_width(max(context.device_to_user_distance(1, 1)))
        context.stroke()

        context.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
        size = self.FONT_SIZE
        context.set_font_size(size)
        x_bearing, y_bearing, width, height, x_advance, y_advance = (
            context.text_extents(self.name))
        context.move_to(-width/2, -(y_bearing + height/2))
        context.show_text(self.name)
        context.new_path()

    def __str__(self):
        return '<Node %s,%s>' % (self.x, self.y)


class Edge:
    layer = 5
    FONT_SIZE = 13

    def __init__(self, u, v, w):
        u, v = min(u, v, key=id), max(u, v, key=id)
        self.u, self.v, self.w = u, v, w

    @property
    def endpoint_ids(self):
        return (id(self.u), id(self.v))

    def render(self, context: cairo.Context):
        context.move_to(self.u.x, self.u.y)
        context.line_to(self.v.x, self.v.y)
        context.set_source_rgba(0, 0, 0, 1)
        width = max(context.device_to_user_distance(1, 1))
        context.set_line_width(width)
        context.stroke()

        context.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
        size = self.FONT_SIZE*width
        context.set_font_size(size)
        x_bearing, y_bearing, width, height, x_advance, y_advance = (
            context.text_extents(str(self.w)))
        context.move_to(self.u.x + (self.v.x - self.u.x) / 2 - x_advance/2,
                        self.u.y + (self.v.y - self.u.y) / 2 + height/2)
        context.show_text(str(self.w))
        context.new_path()

    def __str__(self):
        return '<Edge %s>' % self.w

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


def name_from_index(i):
    '''
    >>> single_letter_names = [name_from_index(i) for i in range(26)]
    >>> single_letter_names == list(string.ascii_lowercase)
    True
    >>> name_from_index(26)
    'aa'
    >>> name_from_index(26 + 26**2)
    'aaa'
    >>> name_from_index(26 + 26**2 + 5)
    'aaf'
    '''
    Σ = string.ascii_lowercase
    n = len(Σ)
    l = 1
    while i >= n ** l:
        i -= n ** l
        l += 1
    s = []
    for _ in range(l):
        i, letter = divmod(i, n)
        s.append(Σ[letter])
    return ''.join(reversed(s))


class GraphManipulator(InteractiveSurface):
    NODE_RADIUS = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.nodes = []
        self.edges = {}
        self.edge_by_weight = []

        self.event_handler.update({
            (EventType.ButtonPress, 1): self.on_left_pressed,
            (EventType.ButtonPress, 3): self.on_right_pressed,
        })

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
        if edges:
            dist, closest = min((e.dist(x, y), e) for e in edges)
            if dist < tol:
                return closest

    def add_node(self, x, y):
        n = Node(x, y, self.NODE_RADIUS, name_from_index(len(self.nodes)))
        self.nodes.append(n)
        self.surface.add(n)
        self.surface.redraw()
        return n

    def find_or_add_node(self, x, y):
        return self.find_node(x, y) or self.add_node(x, y)

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
            del self.edge_by_weight[e.w]
            self.surface.remove(e)
            self.surface.redraw()
            return
        await self.add_edge_from(self.add_node(x, y))

    async def on_right_pressed(self, x, y, ev):
        u = self.find_node(x, y)
        if u:
            u.x, u.y = await self.futures.right_released()
            self.surface.redraw()

    async def add_edge_from(self, u):
        x, y = await self.futures.left_released()
        v = self.find_or_add_node(x, y)
        if u == v:
            return
        e = Edge(u, v, len(self.edges))
        if self.edges.setdefault(e.endpoint_ids, e) is e:
            self.edge_by_weight.append(e)
            self.surface.add(e)
            self.surface.redraw()
        else:
            print('Edge %s already exists' % e)

    def on_scroll_up(self, x, y, ev):
        v = self.find_node(x, y)
        e = v or self.find_edge(x, y)
        if e and not v:
            self.swap_edge_weights(e.w-1, e.w)
        else:
            super().on_scroll_up(x, y, ev)

    def on_scroll_down(self, x, y, ev):
        v = self.find_node(x, y)
        e = v or self.find_edge(x, y)
        if e and not v:
            self.swap_edge_weights(e.w, e.w+1)
        else:
            super().on_scroll_down(x, y, ev)

    def swap_edge_weights(self, i, j):
        edges = self.edge_by_weight
        if 0 <= i < len(edges) and 0 <= j < len(edges):
            edges[i], edges[j] = edges[j], edges[i]
            edges[i].w = i
            edges[j].w = j
            self.surface.redraw()


if __name__ == "__main__":
    GraphManipulator().mainloop()
