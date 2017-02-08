class FontFace():
    '''A *cairo.FontFace* specifies all aspects of a font other than the size or font
    matrix (a font matrix is used to distort a font by sheering it or scaling it
    unequally in the two directions). A *FontFace* can be set on a
    :class:`Context` by using :meth:`Context.set_font_face` the size and font
    matrix are set with :meth:`Context.set_font_size` and
    :meth:`Context.set_font_matrix`.

    There are various types of *FontFace*, depending on the font backend they
    use.
    '''

    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.FontFace(*args, **kwargs)

    def __init__(self):
        '''   .. note:: This class cannot be instantiated directly, it is returned by
             :meth:`Context.get_font_face`.
        '''
        raise NotImplementedError


class FreeTypeFontFace(FontFace):
    '''FreeType Fonts - Font support for FreeType.

    The FreeType font backend is primarily used to render text on GNU/Linux
    systems, but can be used on other platforms too.

       .. note:: FreeType Fonts are not implemented in pycairo because there is no open source Python bindings to FreeType (and fontconfig) that provides a C API. This a possible project idea for anyone interested in adding FreeType support to pycairo.
    '''

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("no init docstring found")


class ToyFontFace(FontFace):
    '''The *cairo.ToyFontFace* class can be used instead of :meth:`Context.select_font_face` to create a toy font independently of a context.
    '''

    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.ToyFontFace(*args, **kwargs)

    def __init__(self, family, slant=None, weight=None):
        '''   :param family: a font family name
           :type family: str
           :param slant: the :ref:`FONT_SLANT <constants_FONT_SLANT>` of the font,
             defaults to :data:`cairo.FONT_SLANT_NORMAL`.
           :param weight: the :ref:`FONT_WEIGHT <constants_FONT_WEIGHT>` of the font,
             defaults to :data:`cairo.FONT_WEIGHT_NORMAL`.
           :returns: a new *ToyFontFace*

           Creates a *ToyFontFace* from a triplet of family, slant, and weight. These
           font faces are used in implementation of the the "toy" font API.

           If family is the zero-length string "", the platform-specific default
           family is assumed. The default family then can be queried using
           :meth:`.get_family`.

           The :meth:`Context.select_font_face` method uses this to create font
           faces. See that function for limitations of toy font faces.

           .. versionadded:: 1.8.4
        '''
        raise NotImplementedError

    def get_family(self):
        ''':returns: the family name of a toy font
        :rtype: str

        .. versionadded:: 1.8.4
        '''
        raise NotImplementedError

    def get_slant(self):
        ''':returns: the :ref:`FONT_SLANT <constants_FONT_SLANT>` value

        .. versionadded:: 1.8.4
        '''
        raise NotImplementedError

    def get_weight(self):
        ''':returns: the :ref:`FONT_WEIGHT <constants_FONT_WEIGHT>` value

        .. versionadded:: 1.8.4
        '''
        raise NotImplementedError


class UserFontFace(FontFace):
    '''The user-font feature allows the cairo user to provide drawings for glyphs in
    a font. This is most useful in implementing fonts in non-standard formats,
    like SVG fonts and Flash fonts, but can also be used by games and other
    application to draw "funky" fonts.

       .. note:: UserFontFace support has not (yet) been added to pycairo. If you
          need this feature in pycairo register your interest by sending a message
          to the cairo mailing list, or by opening a pycairo bug report.
    '''

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("no init docstring found")


class ScaledFont():
    '''A *ScaledFont* is a font scaled to a particular size and device resolution. A
    *ScaledFont* is most useful for low-level font usage where a library or
    application wants to cache a reference to a scaled font to speed up the
    computation of metrics.

    There are various types of scaled fonts, depending on the font backend they
    use.
    '''

    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.ScaledFont(*args, **kwargs)

    def __init__(self, font_face, font_matrix, ctm, options):
        '''   :param font_face: a :class:`FontFace` instance
           :param font_matrix: font space to user space transformation :class:`Matrix`
             for the font. In the simplest case of a N point font, this matrix is just
             a scale by N, but it can also be used to shear the font or stretch it
             unequally along the two axes. See :meth:`Context.set_font_matrix`.
           :param ctm: user to device transformation :class:`Matrix` with which the
             font will be used.
           :param options: a :class:`FontOptions` instance to use when getting metrics
             for the font and rendering with it.

           Creates a *ScaledFont* object from a *FontFace* and matrices that describe
           the size of the font and the environment in which it will be used.
        '''
        raise NotImplementedError

    def extents(self):
        ''':returns: (ascent, descent, height, max_x_advance, max_y_advance), a tuple of float values.

        Gets the metrics for a *ScaledFont*.
        '''
        raise NotImplementedError

    def get_ctm(self):
        '''Not implemented in pycairo (yet)
        '''
        raise NotImplementedError

    def get_font_face(self):
        ''':returns: the :class:`FontFace` that this *ScaledFont* was created for.

        .. versionadded:: 1.2
        '''
        raise NotImplementedError

    def get_font_matrix(self):
        '''Not implemented in pycairo (yet)
        '''
        raise NotImplementedError

    def get_font_options(self):
        '''Not implemented in pycairo (yet)
        '''
        raise NotImplementedError

    def get_scale_matrix(self):
        ''':returns: the scale :class:`Matrix`

        The scale matrix is product of the font matrix and the ctm associated
        with the scaled font, and hence is the matrix mapping from font space to
        device space.

        .. versionadded:: 1.8
        '''
        raise NotImplementedError

    def glyph_extents(self):
        '''Not implemented in pycairo (yet)
        '''
        raise NotImplementedError

    def text_extents(self, text):
        ''':param text: text
        :type text: str
        :returns: (x_bearing, y_bearing, width, height, x_advance, y_advance)
        :rtype: 6-tuple of float

        Gets the extents for a string of text. The extents describe a user-space
        rectangle that encloses the "inked" portion of the text drawn at the
        origin (0,0) (as it would be drawn by :meth:`Context.show_text` if the
        cairo graphics state were set to the same font_face, font_matrix, ctm,
        and font_options as *ScaledFont*).  Additionally, the x_advance and
        y_advance values indicate the amount by which the current point would be
        advanced by :meth:`Context.show_text`.

        Note that whitespace characters do not directly contribute to the size
        of the rectangle (width and height). They do contribute indirectly by
        changing the position of non-whitespace characters. In particular,
        trailing whitespace characters are likely to not affect the size of the
        rectangle, though they will affect the x_advance and y_advance values.

        .. versionadded:: 1.2
        '''
        raise NotImplementedError

    def text_to_glyphs(self):
        '''Not implemented in pycairo (yet)
        '''
        raise NotImplementedError


class FontOptions():
    '''An opaque structure holding all options that are used when rendering fonts.

    Individual features of a *FontOptions* can be set or accessed using functions
    named *FontOptions.set_<feature_name>* and
    *FontOptions.get_<feature_name>*,  like :meth:`FontOptions.set_antialias`
    and :meth:`FontOptions.get_antialias`.

    New features may be added to a *FontOptions* in the future. For this reason,
    :meth:`FontOptions.copy()`, :meth:`FontOptions.equal()`,
    :meth:`FontOptions.merge()`, and :meth:`FontOptions.hash()` should be used to
    copy, check for equality, merge, or compute a hash value of FontOptions
    objects.
    '''

    def __new__(cls, *args, **kwargs):
        import cairo
        return cairo.FontOptions(*args, **kwargs)

    def __init__(self):
        '''   :returns: a newly allocated *FontOptions*.

           Allocates a new *FontOptions* object with all options initialized to default values.
        '''
        raise NotImplementedError

    def get_antialias(self):
        ''':returns: the :ref:`ANTIALIAS <constants_ANTIALIAS>` mode for the *FontOptions* object
        '''
        raise NotImplementedError

    def get_hint_metrics(self):
        ''':returns: the :ref:`HINT METRICS <constants_HINT_METRICS>` mode for the *FontOptions* object
        '''
        raise NotImplementedError

    def get_hint_style(self):
        ''':returns: the :ref:`HINT STYLE <constants_HINT_STYLE>` for the *FontOptions* object
        '''
        raise NotImplementedError

    def get_subpixel_order(self):
        ''':returns: the :ref:`SUBPIXEL_ORDER <constants_SUBPIXEL_ORDER>` for the *FontOptions* object
        '''
        raise NotImplementedError

    def set_antialias(self, antialias):
        ''':param antialias: the :ref:`ANTIALIAS <constants_ANTIALIAS>` mode

        This specifies the type of antialiasing to do when rendering text.
        '''
        raise NotImplementedError

    def set_hint_metrics(self, hint_metrics):
        ''':param hint_metrics: the :ref:`HINT METRICS <constants_HINT_METRICS>` mode

        This controls whether metrics are quantized to integer values in device
        units.
        '''
        raise NotImplementedError

    def set_hint_style(self, hint_style):
        ''':param hint_style: the :ref:`HINT STYLE <constants_HINT_STYLE>`

        This controls whether to fit font outlines to the pixel grid, and if so,
        whether to optimize for fidelity or contrast.
        '''
        raise NotImplementedError

    def set_subpixel_order(self, subpixel_order):
        ''':param subpixel_order: the :ref:`SUBPIXEL_ORDER <constants_SUBPIXEL_ORDER>`

        The subpixel order specifies the order of color elements within each
        pixel on the display device when rendering with an antialiasing mode of
        :data:`cairo.ANTIALIAS_SUBPIXEL`.
        '''
        raise NotImplementedError
