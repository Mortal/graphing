import bisect
import itertools
from collections import OrderedDict


class PriorityList:
    '''
    >>> l = PriorityList()
    >>> l.add(10, 'foo')
    >>> l.add(10, 'bar')
    >>> l.add(10, 'baz')
    >>> list(l)
    ['foo', 'bar', 'baz']
    >>> l.add(5, 'hello')
    >>> list(l)
    ['hello', 'foo', 'bar', 'baz']
    >>> l.add(5, 'world')
    >>> list(l)
    ['hello', 'world', 'foo', 'bar', 'baz']
    >>> l.add(8, 'bla')
    >>> list(l)
    ['hello', 'world', 'bla', 'foo', 'bar', 'baz']
    >>> l
    PriorityList({5: ['hello', 'world'], 8: ['bla'], 10: ['foo', 'bar', 'baz']})
    >>> l == eval(repr(l))
    True
    >>> l == PriorityList()
    False

    Note that inserting the same element multiple times with the same priority
    has no effect:

    >>> l = PriorityList()
    >>> x = 'foo'
    >>> l.add(10, x); l.add(10, x)
    >>> list(l)
    ['foo']
    >>> l.add(11, x)
    >>> list(l)
    ['foo', 'foo']
    >>> l.remove(10, x)
    >>> list(l)
    ['foo']
    >>> l.remove(11, x)
    >>> list(l)
    []
    '''

    def __init__(self, group_by_prio=None):
        if group_by_prio:
            self._prios, lists = zip(*sorted(group_by_prio.items()))
            self._lists = [OrderedDict((id(o), o) for o in l)
                           for l in lists]
            self._group_by_prio = dict(zip(self._prios, self._lists))
        else:
            self._prios, self._lists = [], []
            self._group_by_prio = {}

    @property
    def groups(self):
        return dict(zip(self._prios,
                        map(list, map(OrderedDict.values, self._lists))))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.groups)

    def _new_group(self, prio):
        g = OrderedDict()
        i = bisect.bisect(self._prios, prio)
        self._lists.insert(i, g)
        self._prios.insert(i, prio)
        self._group_by_prio[prio] = g
        return g

    def add(self, prio, x):
        try:
            self._group_by_prio[prio][id(x)] = x
        except KeyError:
            self._new_group(prio)[id(x)] = x

    def remove(self, prio, x):
        del self._group_by_prio[prio][id(x)]

    def __iter__(self):
        return itertools.chain.from_iterable(
            map(OrderedDict.values, self._lists))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __ne__(self, other):
        return tuple(self) != tuple(other)
