# Copyright (c) 2008, samurai-x.org
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the samurai-x.org nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SAMURAI-X.ORG ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL SAMURAI-X.ORG  BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pyglet.window.xlib import xlib 

import samuraix
from samuraix.cairo import *
from samuraix.rsvg import *
from samuraix.sxctypes import byref

import logging
log = logging.getLogger(__name__)


class DrawContext(object):
    svg_handles = {}

    def __init__(self, screen, width, height, drawable):
        self.screen = screen
        self.width = width
        self.height = height 
        self.drawable = drawable
        self.depth = screen.default_depth
        self.visual = screen.default_visual
        self.surface = cairo_xlib_surface_create(samuraix.display, drawable, self.visual,   
                            width, height)
        self.cr = cairo_create(self.surface)

        self.default_font = "snap"
        self.default_font_size = 10

        log.debug('created drawcontext %s' % self)

    def __del__(self):
        self.delete()

    def delete(self):
        log.debug('destroying drawcontext %s' %self)
        cairo_surface_destroy(self.surface)
        cairo_destroy(self.cr)

    def fillrect(self, x, y, width, height, color):
        if False:
            pat = cairo_pattern_create_linear (0.0, 0.0, width, 0.0)
            cairo_pattern_add_color_stop_rgba (pat, 0.0, 1.0, 0.0, 0.0, 1.0)
            cairo_pattern_add_color_stop_rgba (pat, width/3, 0.1, 0.0, 0.0, 1.0)
            cairo_pattern_add_color_stop_rgba (pat, width, 0.0, 0.0, 0.0, 1.0)
            cairo_rectangle(self.cr, x, y, width, height)
            cairo_set_source(self.cr, pat)
            cairo_fill(self.cr)
            cairo_pattern_destroy(pat)
        else:
            cairo_set_source_rgb(self.cr, color[0], color[1], color[2])
            cairo_rectangle(self.cr, x, y, width, height)
            cairo_fill(self.cr)

    def text(self, x, y, string, color=(0.0, 0.0, 0.0), 
            font=None, bold=False, align=None, font_size=None):
        cairo_set_source_rgb(self.cr, color[0], color[1], color[2])

        if font is None:
            font = self.default_font
        if font_size is None:
            font_size = self.default_font_size

        if bold:
            weight = CAIRO_FONT_WEIGHT_BOLD
        else:
            weight = CAIRO_FONT_WEIGHT_NORMAL

        cairo_select_font_face(self.cr, font, CAIRO_FONT_SLANT_NORMAL,
                               weight)
        cairo_set_font_size(self.cr, font_size)

        if align and align != 'left':
            #typedef struct {
            #    double x_bearing;
            #    double y_bearing;
            #    double width;
            #    double height;
            #    double x_advance;
            #    double y_advance;
            #} cairo_text_extents_t;

            extents = cairo_text_extents_t()

            cairo_text_extents(self.cr, string, byref(extents))

            if align == "right":
                x -= extents.x_advance  

        cairo_move_to(self.cr, x, y)
        cairo_show_text(self.cr, string)

    def svg(self, filename, x=0, y=0, width=None, height=None):
        try:
            handle = self.svg_handles[filename]
        except KeyError:
            handle = self.svg_handles[filename] = rsvg_handle_new_from_file(filename)

        cairo_save(self.cr)

        cairo_translate(self.cr, x, y)
 
        if width is not None or height is not None:
            dim = RsvgDimensionData()
            rsvg_handle_get_dimensions(handle, byref(dim))
            if width is not None:
                scale_x = float(width) / dim.width
            else:
                scale_x = 1.0
            if height is not None:
                scale_y = float(height) / dim.height
            else:
                scale_y = 1.0
            cairo_scale(self.cr, scale_x, scale_y)

        rsvg_handle_render_cairo(handle, self.cr)

        cairo_restore(self.cr)

    def fill(self, color=(0.0, 0.0, 0.0)):
        cairo_set_source_rgb(self.cr, *color)
        cairo_paint(self.cr)

