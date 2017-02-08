import string
from functools import partial
from collections import namedtuple


class Element(namedtuple('Element', 'type x')):
    def __str__(self):
        if self.type == EDGE:
            return self.x
        elif self.x < 26:
            return string.ascii_lowercase(self.x)
        else:
            return '%s(%s)' % (('Edge', 'Node')[self.type], self.x)
    def __repr__(self):
        return '%s(%s)' % (('Edge', 'Node')[self.type], self.x)


EDGE, NODE = range(2)
Edge = partial(Element, EDGE)
Node = partial(Element, NODE)


class UnionFind:
    def __init__(self):
        self.rep = {}

    def make_set(self, v):
        self.rep.setdefault(v, v)

    def link(self, u, v):
        self.rep[u] = v

    def find(self, u):
        while self.rep[u] != u:
            self.rep[u] = u = self.rep[self.rep[u]]
        return self.rep[u]

    def union(self, u, v):
        self.link(self.find(u), self.find(v))

    def connected(self, u, v):
        return self.find(u) == self.find(v)

    def component(self, u):
        r = self.find(u)
        return (v for v in self.rep if self.find(v) == r)


def process_graph(edge_lists, edges, node_names):
    print('process_graph, %s edges, hash(edges)=%s, hash(weights)=%s' %
          (len(edges), hash(frozenset(edges)), hash(tuple(edges))))

    components = {}

    for i in range(len(edges)):
        uf = UnionFind()
        for j, (u, v) in enumerate(edges[i:], i):
            uf.make_set(Edge(j))
            uf.make_set(Node(u))
            uf.make_set(Node(v))
            uf.union(Edge(j), Node(u))
            uf.union(Edge(j), Node(v))
            if uf.connected(Edge(i), Edge(j)):
                nodes = (v.x for v in uf.component(Edge(j))
                         if v.type == NODE)
                components[i, j] = frozenset(nodes)

    largest = {}
    for size in range(len(edges), 0, -1):
        for i in range(0, len(edges) - (size - 1)):
            j = i + (size - 1)
            try:
                comp = components[i, j]
            except KeyError:
                print('%s,%s' % (i, j))
            else:
                ri, rj = largest.setdefault(comp, (i, j))
                if (ri, rj) != (i, j):
                    print('%s,%s = %s,%s' % (i, j, ri, rj))
                else:
                    print('%s,%s = %s' %
                          (i, j, ''.join(sorted(node_names[i] for i in comp))))
