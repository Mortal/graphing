class Path():
    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.Path(*args, **kwargs)

    def __init__(self):
        '''   *Path* cannot be instantiated directly, it is created by calling
           :meth:`Context.copy_path` and :meth:`Context.copy_path_flat`.

           str(path) lists the path elements.

           See :ref:`PATH attributes <constants_PATH>`

           Path is an iterator.

           See examples/warpedtext.py for example usage.
        '''
        raise NotImplementedError
