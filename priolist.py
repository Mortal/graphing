import bisect
import itertools


class PriorityList:
    '''
    >>> l = PriorityList()
    >>> l.append(10, 'foo')
    >>> l.append(10, 'bar')
    >>> l.append(10, 'baz')
    >>> list(l)
    ['foo', 'bar', 'baz']
    >>> l.append(5, 'hello')
    >>> list(l)
    ['hello', 'foo', 'bar', 'baz']
    >>> l.append(5, 'world')
    >>> list(l)
    ['hello', 'world', 'foo', 'bar', 'baz']
    >>> l.append(8, 'bla')
    >>> list(l)
    ['hello', 'world', 'bla', 'foo', 'bar', 'baz']
    >>> l
    PriorityList({5: ['hello', 'world'], 8: ['bla'], 10: ['foo', 'bar', 'baz']})
    >>> l == eval(repr(l))
    True
    '''

    def __init__(self, group_by_prio=None):
        if group_by_prio:
            self._prios, self._lists = zip(*sorted(group_by_prio.items()))
            self._group_by_prio = dict(zip(self._prios, self._lists))
        else:
            self._prios, self._lists = [], []
            self._group_by_prio = {}

    @property
    def groups(self):
        return dict(zip(self._prios, self._lists))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.groups)

    def _new_group(self, prio):
        g = []
        i = bisect.bisect(self._prios, prio)
        self._lists.insert(i, g)
        self._prios.insert(i, prio)
        self._group_by_prio[prio] = g
        return g

    def append(self, prio, x):
        try:
            self._group_by_prio[prio].append(x)
        except KeyError:
            self._new_group(prio).append(x)

    def __iter__(self):
        return itertools.chain.from_iterable(self._lists)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __ne__(self, other):
        return tuple(self) != tuple(other)
