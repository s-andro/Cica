#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fontforge
import psMat
import os
import sys
import math
from logging import getLogger, StreamHandler, Formatter, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
formatter = Formatter('%(asctime)s [%(levelname)s] : %(message)s')
handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(handler)

# ASCENT = 850
# DESCENT = 174
ASCENT = 820
DESCENT = 204
SOURCE = './sourceFonts'
LICENSE = open('./LICENSE.txt').read()
COPYRIGHT = open('./COPYRIGHT.txt').read()
VERSION = '4.0.0'
FAMILY = 'Cica'

fonts = [
    {
         'family': FAMILY,
         'name': FAMILY + '-Regular',
         'filename': FAMILY + '-Regular.ttf',
         'weight': 400,
         'weight_name': 'Regular',
         'style_name': 'Regular',
         'hack': 'Hack-Regular.ttf',
         'mgen_plus': 'rounded-mgenplus-1m-regular.ttf',
         'hack_weight_reduce': 0,
         'mgen_weight_add': 0,
         'italic': False,
     }, {
         'family': FAMILY,
         'name': FAMILY + '-RegularItalic',
         'filename': FAMILY + '-RegularItalic.ttf',
         'weight': 400,
         'weight_name': 'Regular',
         'style_name': 'Italic',
         'hack': 'Hack-Regular.ttf',
         'mgen_plus': 'rounded-mgenplus-1m-regular.ttf',
         'hack_weight_reduce': 0,
         'mgen_weight_add': 0,
         'italic': True,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-Bold',
        'filename': FAMILY + '-Bold.ttf',
        'weight': 700,
        'weight_name': 'Bold',
         'style_name': 'Bold',
        'hack': 'Hack-Bold.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-bold.ttf',
        'hack_weight_reduce': 0,
        'mgen_weight_add': 0,
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-BoldItalic',
        'filename': FAMILY + '-BoldItalic.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold Italic',
        'hack': 'Hack-Bold.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-bold.ttf',
        'hack_weight_reduce': 0,
        'mgen_weight_add': 0,
        'italic': True,
    }
]

def log(str):
    logger.debug(str)

def remove_glyph_from_hack(_font):
    u"""Rounded Mgen+を採用したいグリフをHackから削除
    """
    log('remove_ambiguous() : %s' % _font.fontname)

    glyphs = [
            0x2026, # …
            ]

    for g in glyphs:
        _font.selection.select(g)
        _font.clear()

    return _font


def check_files():
    err = 0
    for f in fonts:
        if not os.path.isfile('./sourceFonts/%s' % f.get('hack')):
            logger.error('%s not exists.' % f)
            err = 1

        if not os.path.isfile('./sourceFonts/%s' % f.get('mgen_plus')):
            logger.error('%s not exists.' % f)
            err = 1


    if err > 0:
        sys.exit(err)

def set_os2_values(_font, _info):
    weight = _info.get('weight')
    style_name = _info.get('style_name')
    _font.os2_weight = weight
    _font.os2_width = 5
    _font.os2_fstype = 0
    if style_name == 'Regular':
        _font.os2_stylemap = 64
    elif style_name == 'Bold':
        _font.os2_stylemap = 32
    elif style_name == 'Italic':
        _font.os2_stylemap = 1
    elif style_name == 'Bold Italic':
        _font.os2_stylemap = 33
    _font.os2_vendor = 'TMNM'
    _font.os2_version = 1
    _font.os2_winascent = ASCENT
    _font.os2_winascent_add = False
    _font.os2_windescent = DESCENT
    _font.os2_windescent_add = False

    _font.os2_typoascent = -150
    _font.os2_typoascent_add = True
    _font.os2_typodescent = 100
    _font.os2_typodescent_add = True
    _font.os2_typolinegap = 0

    _font.hhea_ascent = -150
    _font.hhea_ascent_add = True
    _font.hhea_descent = 100
    _font.hhea_descent_add = True
    _font.hhea_linegap = 0
    _font.os2_panose = (2, 11, int(weight / 100), 9, 2, 2, 3, 2, 2, 7)
    return _font

def align_to_center(_g):
    width = 0

    if _g.width > 700:
        width = 1024
    else:
        width = 512

    _g.width = width
    _g.left_side_bearing = _g.right_side_bearing = (_g.left_side_bearing + _g.right_side_bearing)/2
    _g.width = width

    return _g

def align_to_left(_g):
    width = _g.width
    _g.left_side_bearing = 0
    _g.width = width

def align_to_right(_g):
    width = _g.width
    bb = _g.boundingBox()
    left = width - (bb[2] - bb[0])
    _g.left_side_bearing = left
    _g.width = width

def add_dejavu(_f, conf):
    dejavu = None
    weight_name = conf.get('weight_name')
    if weight_name == "Regular":
        dejavu = fontforge.open('./sourceFonts/DejaVuSansMono.ttf')
    elif weight_name == "Bold":
        dejavu = fontforge.open('./sourceFonts/DejaVuSansMono-Bold.ttf')

    for g in dejavu.glyphs():
        g.transform(psMat.compose(psMat.scale(0.45, 0.45), psMat.translate(-21, 0)))
        g.width = 512

    _f.importLookups(dejavu, dejavu.gpos_lookups)

    # 0x0300 - 0x036f - Combining Diacritical Marks
    for g in dejavu.glyphs():
        if g.encoding < 0x0300 or g.encoding > 0x036f:
            continue
        else:
            if len(g.references) > 0:
                anchorPoints = g.anchorPoints
                g.anchorPoints = ()
                g.transform(psMat.scale(2.22, 2.22))
                g.transform(psMat.translate(50, 0))
                g.width = 512
                g.anchorPoints = anchorPoints

            if g.encoding <= 0x0304:
                anchorPoints = g.anchorPoints
                g.anchorPoints = ()
                g.transform(psMat.scale(1.2, 1.2))
                g.transform(psMat.translate(-100, -60))
                g.width = 512
                g.anchorPoints = anchorPoints
            elif g.encoding == 0x0305:
                g.transform(psMat.translate(0, -60))
            elif g.encoding <= 0x0315:
                g.transform(psMat.translate(0, 0))
            elif g.encoding <= 0x0317:
                g.transform(psMat.translate(0, 302))
            elif g.encoding <= 0x0319:
                g.transform(psMat.translate(0, 200))
            elif g.encoding <= 0x031b:
                g.transform(psMat.translate(0, -60))
            elif g.encoding <= 0x031c:
                g.transform(psMat.translate(0, 22))
            elif g.encoding <= 0x031f:
                g.transform(psMat.translate(0, 141))
            elif g.encoding <= 0x0332:
                g.transform(psMat.translate(0, 90))
            elif g.encoding == 0x0333:
                g.transform(psMat.compose(psMat.scale(0.9, 0.9), psMat.translate(-415, 29)))
                g.width = 512
            elif g.encoding <= 0x0338:
                g.transform(psMat.translate(0, 0))
            elif g.encoding <= 0x033c:
                g.transform(psMat.translate(0, 138))
            else:
                g.transform(psMat.translate(0, 0))
            dejavu.selection.select(g.encoding)
            dejavu.copy()
            _f.selection.select(g.encoding)
            _f.paste()
    # 0x0370 - 0x03ff - GREEK
    for g in dejavu.glyphs():
        if g.encoding < 0x0370 or g.encoding > 0x03ff:
            continue
        else:
            if len(g.references) == 0:
                bb = g.boundingBox()
                g.anchorPoints = (('Anchor-7', 'mark', 256, bb[3] + 20),)
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                _f.selection.select(g.encoding)
                _f.paste()
    # 0x2100 - 0x214f Letterlike Symbols
    for g in dejavu.glyphs():
        if g.encoding < 0x2100 or g.encoding > 0x214f or g.encoding == 0x2122:
            continue
        else:
            if len(g.references) == 0:
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                _f.selection.select(g.encoding)
                _f.paste()
    # 0x2150 - 0x218f Number Forms
    for g in dejavu.glyphs():
        if g.encoding < 0x2150 or g.encoding > 0x218f:
            continue
        else:
            if len(g.references) == 0:
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                _f.selection.select(g.encoding)
                _f.paste()
    # 0x2190 - 0x21ff Arrows
    for g in dejavu.glyphs():
        if g.encoding < 0x2190 or g.encoding > 0x21ff:
            continue
        else:
            if len(g.references) == 0:
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                _f.selection.select(g.encoding)
                _f.paste()
    # 0x2200 - 0x22ff Mathematical Operators
    for g in dejavu.glyphs():
        if g.encoding < 0x2200 or g.encoding > 0x22ff:
            continue
        else:
            if len(g.references) == 0:
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                _f.selection.select(g.encoding)
                _f.paste()
    # 0x2300 - 0x23ff Miscellaneous Technical
    for g in dejavu.glyphs():
        if g.encoding < 0x2300 or g.encoding > 0x23ff:
            continue
        else:
            if len(g.references) == 0:
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                _f.selection.select(g.encoding)
                _f.paste()
    dejavu.close()
    return _f

def modify_nerd(_g):
    align_left = [
        0xe0b0, 0xe0b1, 0xe0b4, 0xe0b5, 0xe0b8, 0xe0b9, 0xe0bc,
        0xe0bd, 0xe0c0, 0xe0c1, 0xe0c4, 0xe0c6, 0xe0c8, 0xe0cc, 0xe0cd,
        0xe0d1, 0xe0d2,
    ]
    align_right = [
        0xe0b2, 0xe0b3, 0xe0b6, 0xe0b7, 0xe0b7, 0xe0ba, 0xe0bb, 0xe0be,
        0xe0bf, 0xe0c2, 0xe0c3, 0xe0c5, 0xe0c7, 0xe0ca, 0xe0ce, 0xe0d4,
    ]
    # Powerline
    if _g.encoding >= 0xe0b0 and _g.encoding <= 0xe0d4:
        _g.transform(psMat.translate(0, -55))
        _g.width = 1024

        if _g.encoding >= 0xe0b0 and _g.encoding <= 0xe0b7:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024

        if _g.encoding >= 0xe0b8 and _g.encoding <= 0xe0bf:
            _g.transform(psMat.compose(psMat.scale(0.8, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024

        if _g.encoding >= 0xe0c0 and _g.encoding <= 0xe0c3:
            _g.transform(psMat.scale(0.7, 1.0))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding >= 0xe0c4 and _g.encoding <= 0xe0c7:
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding == 0xe0c8 or _g.encoding == 0xe0ca:
            _g.transform(psMat.scale(0.7, 1.0))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding == 0xe0ce:
            _g.transform(psMat.scale(0.8, 1.0))
            bb = _g.boundingBox()
            left = 1024 - (bb[2] - bb[0])
            _g.left_side_bearing = left
            _g.width = 1024
        if _g.encoding == 0xe0cf:
            _g.transform(psMat.scale(0.9, 1.0))
            _g = align_to_center(_g)
        if _g.encoding == 0xe0d0:
            _g = align_to_center(_g)
        if _g.encoding == 0xe0d1:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            _g.left_side_bearing = 0
            _g.width = 1024
        if _g.encoding == 0xe0d2 or _g.encoding == 0xe0d4:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
    elif _g.encoding >= 0xf000 and _g.encoding <= 0xf2e0:
        _g.transform(psMat.compose(psMat.scale(0.75, 0.75), psMat.translate(0, 55)))
        _g.width = 1024
        _g = align_to_center(_g)
    else:
        _g.transform(psMat.translate(0, -55))
        _g.width = 1024
        _g = align_to_center(_g)

    return _g



def vertical_line_to_broken_bar(_f):
    _f.selection.select(0x00a6)
    _f.copy()
    _f.selection.select(0x007c)
    _f.paste()
    return _f

def emdash_to_broken_dash(_f):
    _f.selection.select(0x006c)
    _f.copy()
    _f.selection.select(0x2014)
    _f.pasteInto()
    _f.intersect()
    return _f

def mathglyph_to_double(_f):
    pass

def zenkaku_space(_f):
    _f.selection.select(0x2610)
    _f.copy()
    _f.selection.select(0x3000)
    _f.paste()
    _f.selection.select(0x271a)
    _f.copy()
    _f.selection.select(0x3000)
    _f.pasteInto()
    _f.intersect()
    for g in _f.selection.byGlyphs:
        g = align_to_center(g)
    return _f

def zero(_f):
    _f.selection.select(0x4f)
    _f.copy()
    _f.selection.select(0x30)
    _f.paste()
    _f.selection.select(0xb7)
    _f.copy()
    _f.selection.select(0x30)
    _f.pasteInto()
    for g in _f.selection.byGlyphs:
        g = align_to_center(g)
    return _f

def modify_WM(_f):
    _f.selection.select(0x57)
    _f.transform(psMat.scale(0.95, 1.0))
    _f.copy()
    _f.selection.select(0x4d)
    _f.paste()
    _f.transform(psMat.compose(psMat.rotate(math.radians(180)), psMat.translate(0, 627)))
    for g in _f.selection.byGlyphs:
        g = align_to_center(g)
    return _f

def modify_m(_f, _weight):
    m = fontforge.open('./sourceFonts/m-Regular.sfd')
    if _weight == 'Bold':
        m.close()
        m = fontforge.open('./sourceFonts/m-Bold.sfd')
    m.selection.select(0x6d)
    m.copy()
    _f.selection.select(0x6d)
    _f.paste()
    for g in m.glyphs():
        if g.encoding == 0x6d:
            anchorPoints = g.anchorPoints
    for g in _f.glyphs():
        if g.encoding == 0x6d:
            g.anchorPoints = anchorPoints

    return _f


def add_smalltriangle(_f):
    _f.selection.select(0x25bc)
    _f.copy()
    _f.selection.select(0x25be)
    _f.paste()
    _f.transform(psMat.compose(psMat.scale(0.64), psMat.translate(0, 68)))
    _f.copy()
    _f.selection.select(0x25b8)
    _f.paste()
    _f.transform(psMat.rotate(math.radians(90)))

    for g in _f.glyphs():
        if g.encoding == 0x25be or g.encoding == 0x25b8:
            g.width = 512
            g = align_to_center(g)

    return _f

def fix_box_drawings(_f):
    left = [
        0x2510, 0x2518, 0x2524, 0x2555, 0x2556, 0x2557, 0x255b, 0x255c, 0x255d,
        0x2561, 0x2562, 0x2563,
    ]
    right = [
        0x250c, 0x2514, 0x251c, 0x2552, 0x2553, 0x2554, 0x2558, 0x2559, 0x255a,
        0x255e, 0x255f, 0x2560,
    ]

    for g in _f.glyphs():
        if g.encoding < 0x2500 or g.encoding > 0x256c:
            continue
        if g.encoding in left:
            align_to_left(g)
        elif g.encoding in right:
            align_to_right(g)

    return _f


def build_font(_f, emoji):
    log('Generating %s ...' % _f.get('weight_name'))
    hack = fontforge.open('./sourceFonts/%s' % _f.get('hack'))
    hack = remove_glyph_from_hack(hack)
    cica = fontforge.open('./sourceFonts/%s' % _f.get('mgen_plus'))
    nerd = fontforge.open('./sourceFonts/nerd.ttf')

    for g in hack.glyphs():
        g.transform((0.42,0,0,0.42,0,0))
        if _f.get('hack_weight_reduce') != 0:
            # g.changeWeight(_f.get('hack_weight_reduce'), 'auto', 0, 0, 'auto')
            g.stroke("circular", _f.get('hack_weight_reduce'), 'butt', 'round', 'removeexternal')
        g = align_to_center(g)
    hack = modify_m(hack, _f.get('weight_name'))


    alternate_expands = [
        0x306e,
    ]

    if _f.get('mgen_weight_add') != 0:
        for g in cica.glyphs():
            # g.changeWeight(_f.get('mgen_weight_add'), 'auto', 0, 0, 'auto')
            g.stroke("caligraphic", _f.get('mgen_weight_add'), _f.get('mgen_weight_add'), 45, 'removeinternal')
            # g.stroke("circular", _f.get('mgen_weight_add'), 'butt', 'round', 'removeinternal')


    ignoring_center = [
        0x3001, 0x3002, 0x3008, 0x3009, 0x300a, 0x300b, 0x300c, 0x300d,
        0x300e, 0x300f, 0x3010, 0x3011, 0x3014, 0x3015, 0x3016, 0x3017,
        0x3018, 0x3019, 0x301a, 0x301b, 0x301d, 0x301e, 0x3099, 0x309a,
        0x309b, 0x309c,
    ]
    for g in cica.glyphs():
        g.transform((0.91,0,0,0.91,0,0))
        full_half_threshold = 700
        if _f.get('italic'):
            g.transform(psMat.skew(0.25))
            skew_amount = g.font.ascent * 0.91 * 0.25
            g.width = g.width + skew_amount
            full_half_threshold += skew_amount
        if g.width > full_half_threshold:
            width = 1024
        else:
            width = 512
        g.transform(psMat.translate((width - g.width)/2, 0))
        g.width = width
        if g.encoding in ignoring_center:
            pass
        else:
            g = align_to_center(g)

    for g in hack.glyphs():
        if  g.isWorthOutputting:
            if _f.get('italic'):
                g.transform(psMat.skew(0.25))
            if g.encoding >= 0x2500 and g.encoding <= 0x25af:
                g.transform(psMat.compose(psMat.scale(1.024, 1.024), psMat.translate(0, -30)))
                g = align_to_center(g)
            hack.selection.select(g.encoding)
            hack.copy()
            cica.selection.select(g.encoding)
            cica.paste()

    for g in nerd.glyphs():
        if g.encoding < 0xe0a0 or g.encoding > 0xf4ff:
            continue
        g = modify_nerd(g)
        nerd.selection.select(g.encoding)
        nerd.copy()
        cica.selection.select(g.encoding)
        cica.paste()

    cica = fix_box_drawings(cica)
    cica = zenkaku_space(cica)
    cica = zero(cica)
    cica = modify_WM(cica)
    cica = vertical_line_to_broken_bar(cica)
    cica = emdash_to_broken_dash(cica)
    cica = add_gopher(cica)
    if emoji:
        cica = add_notoemoji(cica)
    cica = add_smalltriangle(cica)
    cica = add_dejavu(cica, _f)
    cica = resize_supersub(cica)

    cica.ascent = ASCENT
    cica.descent = DESCENT
    cica.upos = 45
    cica.fontname = _f.get('family')
    cica.familyname = _f.get('family')
    cica.fullname = _f.get('name')
    cica.weight = _f.get('weight_name')
    cica = set_os2_values(cica, _f)
    cica.appendSFNTName(0x411,0, COPYRIGHT)
    cica.appendSFNTName(0x411,1, _f.get('family'))
    cica.appendSFNTName(0x411,2, _f.get('style_name'))
    # cica.appendSFNTName(0x411,3, "")
    cica.appendSFNTName(0x411,4, _f.get('name'))
    cica.appendSFNTName(0x411,5, "Version " + VERSION)
    cica.appendSFNTName(0x411,6, _f.get('family') + "-" + _f.get('weight_name'))
    # cica.appendSFNTName(0x411,7, "")
    # cica.appendSFNTName(0x411,8, "")
    # cica.appendSFNTName(0x411,9, "")
    # cica.appendSFNTName(0x411,10, "")
    # cica.appendSFNTName(0x411,11, "")
    # cica.appendSFNTName(0x411,12, "")
    cica.appendSFNTName(0x411,13, LICENSE)
    # cica.appendSFNTName(0x411,14, "")
    # cica.appendSFNTName(0x411,15, "")
    cica.appendSFNTName(0x411,16, _f.get('family'))
    cica.appendSFNTName(0x411,17, _f.get('style_name'))
    cica.appendSFNTName(0x409,0, COPYRIGHT)
    cica.appendSFNTName(0x409,1, _f.get('family'))
    cica.appendSFNTName(0x409,2, _f.get('style_name'))
    cica.appendSFNTName(0x409,3, VERSION + ";" + _f.get('family') + "-" + _f.get('style_name'))
    cica.appendSFNTName(0x409,4, _f.get('name'))
    cica.appendSFNTName(0x409,5, "Version " + VERSION)
    cica.appendSFNTName(0x409,6, _f.get('name'))
    # cica.appendSFNTName(0x409,7, "")
    # cica.appendSFNTName(0x409,8, "")
    # cica.appendSFNTName(0x409,9, "")
    # cica.appendSFNTName(0x409,10, "")
    # cica.appendSFNTName(0x409,11, "")
    # cica.appendSFNTName(0x409,12, "")
    cica.appendSFNTName(0x409,13, LICENSE)
    # cica.appendSFNTName(0x409,14, "")
    # cica.appendSFNTName(0x409,15, "")
    cica.appendSFNTName(0x409,16, _f.get('family'))
    cica.appendSFNTName(0x409,17, _f.get('style_name'))
    if emoji:
        fontpath = './dist/%s' % _f.get('filename')
    else:
        fontpath = './dist/noemoji/%s' % _f.get('filename')

    cica.generate(fontpath)

    cica.close()
    hack.close()
    nerd.close()


def add_notoemoji(_f):
    notoemoji = fontforge.open('./sourceFonts/NotoEmoji-Regular.ttf')
    for g in notoemoji.glyphs():
        if g.isWorthOutputting and g.encoding > 0x04f9:
            g.transform((0.42,0,0,0.42,0,0))
            g = align_to_center(g)
            notoemoji.selection.select(g.encoding)
            notoemoji.copy()
            _f.selection.select(g.encoding)
            _f.paste()
    notoemoji.close()
    return _f

def add_gopher(_f):
    gopher = fontforge.open('./sourceFonts/gopher.sfd')
    for g in gopher.glyphs():
        if g.isWorthOutputting:
            gopher.selection.select(0x40)
            gopher.copy()
            _f.selection.select(0xE160)
            _f.paste()
            g.transform(psMat.compose(psMat.scale(-1, 1), psMat.translate(g.width, 0)))
            gopher.copy()
            _f.selection.select(0xE161)
            _f.paste()
    gopher.close()
    return _f

def resize_supersub(_f):
    superscripts = [
            {"src": 0x0031, "dest": 0x00b9}, {"src": 0x0032, "dest": 0x00b2},
            {"src": 0x0033, "dest": 0x00b3}, {"src": 0x0030, "dest": 0x2070},
            {"src": 0x0069, "dest": 0x2071}, {"src": 0x0034, "dest": 0x2074},
            {"src": 0x0037, "dest": 0x2077}, {"src": 0x0038, "dest": 0x2078},
            {"src": 0x0039, "dest": 0x2079}, {"src": 0x002b, "dest": 0x207a},
            {"src": 0x002d, "dest": 0x207b}, {"src": 0x003d, "dest": 0x207c},
            {"src": 0x0028, "dest": 0x207d}, {"src": 0x0029, "dest": 0x207e},
            {"src": 0x006e, "dest": 0x207f},
            # ↓上付きの大文字
            {"src": 0x0041, "dest": 0x1d2c}, {"src": 0x00c6, "dest": 0x1d2d},
            {"src": 0x0042, "dest": 0x1d2e}, {"src": 0x0044, "dest": 0x1d30},
            {"src": 0x0045, "dest": 0x1d31}, {"src": 0x018e, "dest": 0x1d32},
            {"src": 0x0047, "dest": 0x1d33}, {"src": 0x0048, "dest": 0x1d34},
            {"src": 0x0049, "dest": 0x1d35}, {"src": 0x004a, "dest": 0x1d36},
            {"src": 0x004b, "dest": 0x1d37}, {"src": 0x004c, "dest": 0x1d38},
            {"src": 0x004d, "dest": 0x1d39}, {"src": 0x004e, "dest": 0x1d3a},
            ## ↓REVERSED N なのでNを左右反転させる必要あり
            {"src": 0x004e, "dest": 0x1d3b, "reversed": True},
            {"src": 0x004f, "dest": 0x1d3c}, {"src": 0x0222, "dest": 0x1d3d},
            {"src": 0x0050, "dest": 0x1d3e}, {"src": 0x0052, "dest": 0x1d3f},
            {"src": 0x0054, "dest": 0x1d40}, {"src": 0x0055, "dest": 0x1d41},
            {"src": 0x0057, "dest": 0x1d42},
            # ↓上付きの小文字
            {"src": 0x0061, "dest": 0x1d43}, {"src": 0x0250, "dest": 0x1d44},
            {"src": 0x0251, "dest": 0x1d45}, {"src": 0x1d02, "dest": 0x1d46},
            {"src": 0x0062, "dest": 0x1d47}, {"src": 0x0064, "dest": 0x1d48},
            {"src": 0x0065, "dest": 0x1d49}, {"src": 0x0259, "dest": 0x1d4a},
            {"src": 0x025b, "dest": 0x1d4b}, {"src": 0x025c, "dest": 0x1d4c},
            {"src": 0x0067, "dest": 0x1d4d},
            ## ↓TURNED i なので 180度回す必要あり
            {"src": 0x0069, "dest": 0x1d4e, "turned": True},
            {"src": 0x006b, "dest": 0x1d4f}, {"src": 0x006d, "dest": 0x1d50},
            {"src": 0x014b, "dest": 0x1d51}, {"src": 0x006f, "dest": 0x1d52},
            {"src": 0x0254, "dest": 0x1d53}, {"src": 0x1d16, "dest": 0x1d54},
            {"src": 0x1d17, "dest": 0x1d55}, {"src": 0x0070, "dest": 0x1d56},
            {"src": 0x0074, "dest": 0x1d57}, {"src": 0x0075, "dest": 0x1d58},
            {"src": 0x1d1d, "dest": 0x1d59}, {"src": 0x026f, "dest": 0x1d5a},
            {"src": 0x0076, "dest": 0x1d5b}, {"src": 0x1d25, "dest": 0x1d5c},
            {"src": 0x03b2, "dest": 0x1d5d}, {"src": 0x03b3, "dest": 0x1d5e},
            {"src": 0x03b4, "dest": 0x1d5f}, {"src": 0x03c6, "dest": 0x1d60},
            {"src": 0x03c7, "dest": 0x1d61},
            {"src": 0x0056, "dest": 0x2c7d}, {"src": 0x0068, "dest": 0x02b0},
            {"src": 0x0266, "dest": 0x02b1}, {"src": 0x006a, "dest": 0x02b2},
            {"src": 0x006c, "dest": 0x02e1}, {"src": 0x0073, "dest": 0x02e2},
            {"src": 0x0078, "dest": 0x02e3}, {"src": 0x0072, "dest": 0x02b3},
            {"src": 0x0077, "dest": 0x02b7}, {"src": 0x0079, "dest": 0x02b8},
            {"src": 0x0063, "dest": 0x1d9c}, {"src": 0x0066, "dest": 0x1da0},
            {"src": 0x007a, "dest": 0x1dbb}, {"src": 0x0061, "dest": 0x00aa},
            {"src": 0x0252, "dest": 0x1d9b}, {"src": 0x0255, "dest": 0x1d9d},
            {"src": 0x00f0, "dest": 0x1d9e}, {"src": 0x025c, "dest": 0x1d9f},
            {"src": 0x025f, "dest": 0x1da1}, {"src": 0x0261, "dest": 0x1da2},
            {"src": 0x0265, "dest": 0x1da3}, {"src": 0x0268, "dest": 0x1da4},
            {"src": 0x0269, "dest": 0x1da5}, {"src": 0x026a, "dest": 0x1da6},
            {"src": 0x1d7b, "dest": 0x1da7}, {"src": 0x029d, "dest": 0x1da8},
            {"src": 0x026d, "dest": 0x1da9}, {"src": 0x1d85, "dest": 0x1daa},
            {"src": 0x029f, "dest": 0x1dab}, {"src": 0x0271, "dest": 0x1dac},
            {"src": 0x0270, "dest": 0x1dad}, {"src": 0x0272, "dest": 0x1dae},
            {"src": 0x0273, "dest": 0x1daf}, {"src": 0x0274, "dest": 0x1db0},
            {"src": 0x0275, "dest": 0x1db1}, {"src": 0x0278, "dest": 0x1db2},
            {"src": 0x0282, "dest": 0x1db3}, {"src": 0x0283, "dest": 0x1db4},
            {"src": 0x01ab, "dest": 0x1db5}, {"src": 0x0289, "dest": 0x1db6},
            {"src": 0x028a, "dest": 0x1db7}, {"src": 0x1d1c, "dest": 0x1db8},
            {"src": 0x028b, "dest": 0x1db9}, {"src": 0x028c, "dest": 0x1dba},
            {"src": 0x0290, "dest": 0x1dbc}, {"src": 0x0291, "dest": 0x1dbd},
            {"src": 0x0292, "dest": 0x1dbe}, {"src": 0x03b8, "dest": 0x1dbf},

    ]
    subscripts = [
            {"src": 0x0069, "dest": 0x1d62}, {"src": 0x0072, "dest": 0x1d63},
            {"src": 0x0075, "dest": 0x1d64}, {"src": 0x0076, "dest": 0x1d65},
            {"src": 0x03b2, "dest": 0x1d66}, {"src": 0x03b3, "dest": 0x1d67},
            {"src": 0x03c1, "dest": 0x1d68}, {"src": 0x03c6, "dest": 0x1d69},
            {"src": 0x03c7, "dest": 0x1d6a}, {"src": 0x006a, "dest": 0x2c7c},
            {"src": 0x0030, "dest": 0x2080}, {"src": 0x0031, "dest": 0x2081},
            {"src": 0x0032, "dest": 0x2082}, {"src": 0x0033, "dest": 0x2083},
            {"src": 0x0034, "dest": 0x2084}, {"src": 0x0035, "dest": 0x2085},
            {"src": 0x0036, "dest": 0x2086}, {"src": 0x0037, "dest": 0x2087},
            {"src": 0x0038, "dest": 0x2088}, {"src": 0x0039, "dest": 0x2089},
            {"src": 0x002b, "dest": 0x208a}, {"src": 0x002d, "dest": 0x208b},
            {"src": 0x003d, "dest": 0x208c}, {"src": 0x0028, "dest": 0x208d},
            {"src": 0x0029, "dest": 0x208e}, {"src": 0x0061, "dest": 0x2090},
            {"src": 0x0065, "dest": 0x2091}, {"src": 0x006f, "dest": 0x2092},
            {"src": 0x0078, "dest": 0x2093}, {"src": 0x0259, "dest": 0x2094},
            {"src": 0x0068, "dest": 0x2095}, {"src": 0x006b, "dest": 0x2096},
            {"src": 0x006c, "dest": 0x2097}, {"src": 0x006d, "dest": 0x2098},
            {"src": 0x006e, "dest": 0x2099}, {"src": 0x0070, "dest": 0x209a},
            {"src": 0x0073, "dest": 0x209b}, {"src": 0x0074, "dest": 0x209c}
    ]

    for g in superscripts:
        _f.selection.select(g["src"])
        _f.copy()
        _f.selection.select(g["dest"])
        _f.paste()
    for g in subscripts:
        _f.selection.select(g["src"])
        _f.copy()
        _f.selection.select(g["dest"])
        _f.paste()

    for g in _f.glyphs("encoding"):
        if g.encoding > 0x2c7d:
            continue
        elif in_scripts(g.encoding, superscripts):
            if g.encoding == 0x1d5d or g.encoding == 0x1d61:
                g.transform(psMat.scale(0.70, 0.70))
            elif g.encoding == 0x1d3b:
                g.transform(psMat.scale(0.75, 0.75))
                g.transform(psMat.compose(psMat.scale(-1, 1), psMat.translate(g.width, 0)))
            elif g.encoding == 0x1d4e:
                g.transform(psMat.scale(0.75, 0.75))
                g.transform(psMat.rotate(3.14159))
                g.transform(psMat.translate(0, 512))
            else:
                g.transform(psMat.scale(0.75, 0.75))
            bb = g.boundingBox()
            g.transform(psMat.translate(0, 244))
            align_to_center(g)
        elif in_scripts(g.encoding, subscripts):
            if g.encoding == 0x1d66 or g.encoding == 0x1d6a:
                g.transform(psMat.scale(0.70, 0.70))
            else:
                g.transform(psMat.scale(0.75, 0.75))
            bb = g.boundingBox()
            y = -144
            if bb[1] < -60: # DESCENT - 144
                y = -60
            g.transform(psMat.translate(0, y))
            align_to_center(g)
    return _f

def in_scripts(encoding, scripts):
    for s in scripts:
        if encoding == s["dest"]:
            return True
    return False


def scripts_from(encoding, scripts):
    for s in scripts:
        if encoding == s["dest"]:
            return s["src"]
    raise ValueError

def main():
    print('')
    print('### Generating Cica started. ###')
    check_files()
    for _f in fonts:
        build_font(_f, True)
        build_font(_f, False)

    print('### Succeeded ###')


if __name__ == '__main__':
    main()
