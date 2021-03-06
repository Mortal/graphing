from cairo import (
    ANTIALIAS_DEFAULT, ANTIALIAS_GRAY, ANTIALIAS_NONE, ANTIALIAS_SUBPIXEL,
    CAPI, CONTENT_ALPHA, CONTENT_COLOR, CONTENT_COLOR_ALPHA, EXTEND_NONE,
    EXTEND_PAD, EXTEND_REFLECT, EXTEND_REPEAT, FILL_RULE_EVEN_ODD,
    FILL_RULE_WINDING, FILTER_BEST, FILTER_BILINEAR, FILTER_FAST,
    FILTER_GAUSSIAN, FILTER_GOOD, FILTER_NEAREST, FONT_SLANT_ITALIC,
    FONT_SLANT_NORMAL, FONT_SLANT_OBLIQUE, FONT_WEIGHT_BOLD,
    FONT_WEIGHT_NORMAL, FORMAT_A1, FORMAT_A8, FORMAT_ARGB32, FORMAT_RGB16_565,
    FORMAT_RGB24, HAS_ATSUI_FONT, HAS_FT_FONT, HAS_GLITZ_SURFACE,
    HAS_IMAGE_SURFACE, HAS_PDF_SURFACE, HAS_PNG_FUNCTIONS, HAS_PS_SURFACE,
    HAS_QUARTZ_SURFACE, HAS_RECORDING_SURFACE, HAS_SVG_SURFACE, HAS_USER_FONT,
    HAS_WIN32_FONT, HAS_WIN32_SURFACE, HAS_XCB_SURFACE, HAS_XLIB_SURFACE,
    HINT_METRICS_DEFAULT, HINT_METRICS_OFF, HINT_METRICS_ON,
    HINT_STYLE_DEFAULT, HINT_STYLE_FULL, HINT_STYLE_MEDIUM, HINT_STYLE_NONE,
    HINT_STYLE_SLIGHT, LINE_CAP_BUTT, LINE_CAP_ROUND, LINE_CAP_SQUARE,
    LINE_JOIN_BEVEL, LINE_JOIN_MITER, LINE_JOIN_ROUND, OPERATOR_ADD,
    OPERATOR_ATOP, OPERATOR_CLEAR, OPERATOR_COLOR_BURN, OPERATOR_COLOR_DODGE,
    OPERATOR_DARKEN, OPERATOR_DEST, OPERATOR_DEST_ATOP, OPERATOR_DEST_IN,
    OPERATOR_DEST_OUT, OPERATOR_DEST_OVER, OPERATOR_DIFFERENCE,
    OPERATOR_EXCLUSION, OPERATOR_HARD_LIGHT, OPERATOR_HSL_COLOR,
    OPERATOR_HSL_HUE, OPERATOR_HSL_LUMINOSITY, OPERATOR_HSL_SATURATION,
    OPERATOR_IN, OPERATOR_LIGHTEN, OPERATOR_MULTIPLY, OPERATOR_OUT,
    OPERATOR_OVER, OPERATOR_OVERLAY, OPERATOR_SATURATE, OPERATOR_SCREEN,
    OPERATOR_SOFT_LIGHT, OPERATOR_SOURCE, OPERATOR_XOR, PATH_CLOSE_PATH,
    PATH_CURVE_TO, PATH_LINE_TO, PATH_MOVE_TO, PDF_VERSION_1_4,
    PDF_VERSION_1_5, PS_LEVEL_2, PS_LEVEL_3, REGION_OVERLAP_IN,
    REGION_OVERLAP_OUT, REGION_OVERLAP_PART, SUBPIXEL_ORDER_BGR,
    SUBPIXEL_ORDER_DEFAULT, SUBPIXEL_ORDER_RGB, SUBPIXEL_ORDER_VBGR,
    SUBPIXEL_ORDER_VRGB, SVG_VERSION_1_1, SVG_VERSION_1_2,
)

from cairo import cairo_version, cairo_version_string, version, version_info

from .context import Context
from .matrix import Matrix
from .paths import Path
from .patterns import (
    Pattern, SolidPattern, SurfacePattern, Gradient, LinearGradient,
    RadialGradient,
)
from .region import Region, RectangleInt
from .surfaces import (
    Surface, ImageSurface, PDFSurface, PSSurface, RecordingSurface, SVGSurface,
    XCBSurface, XlibSurface,
)
from .text import (
    FontFace, FreeTypeFontFace, ToyFontFace, UserFontFace, ScaledFont,
    FontOptions,
)
