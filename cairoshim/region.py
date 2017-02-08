class Region():
    '''*Region* is a simple graphical data type representing an area of
    integer-aligned rectangles. They are often used on raster surfaces to track
    areas of interest, such as change or clip areas.
    '''

    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.Region(*args, **kwargs)

    def __init__(self, rectangle_int|rectangle_ints=None):
        '''   :param rectangle_int: a rectangle or a list of rectangle
           :type rectangle_int: :class:`RectangleInt` or [:class:`RectangleInt`]

           Allocates a new empty region object or a region object with the containing
           rectangle(s).
        '''
        raise NotImplementedError

    def copy(self):
        ''':returns: A newly allocated :class:`Region`.
        :raises: :exc:`NoMemory` if memory cannot be allocated.

        Allocates a new *Region* object copying the area from original.
        '''
        raise NotImplementedError


class RectangleInt():
    '''*RectangleInt* is a data structure for holding a rectangle with integer
    coordinates.
    '''

    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.RectangleInt(*args, **kwargs)

    def __init__(self, x=0, y=0, width=0, height=0):
        '''   :param x: X coordinate of the left side of the rectangle
           :type x: int
           :param y: Y coordinate of the the top side of the rectangle
           :type y: int
           :param width: width of the rectangle
           :type width: int
           :param height: height of the rectangle
           :type height: int

           Allocates a new *RectangleInt* object.
        '''
        raise NotImplementedError
