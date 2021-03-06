# Copyright (c) 2008-2009, samurai-x.org
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

class Rect(object):
    """
        a simple rectangle class. It has four slots x, y, width and height and
        can be created from or converted to other formats very easily.
    """
    __slots__ = ['x', 'y', 'width', 'height']

    def __init__(self, x=0, y=0, width=100, height=100):
        """
            :type x, y, width, height: int
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def copy(self):
        """
            return a new :class:`Rect` instance having the same values
            as self.
        """
        return Rect(self.x, self.y, self.width, self.height)

    def __str__(self):
        return "<Rect %s %s %s %s>" % (self.x, self.y, self.width, self.height)

    def to_dict(self):
        """
            return a dictionary having the keys 'x', 'y', 'width' and 'height',
            containing self's values.
        """
        return {'x': self.x, 'y': self.y,
                'width': self.width, 'height': self.height}

    @classmethod
    def from_object(cls, struct):
        """
            Create a new :class:`Rect` instance from the object *struct* that
            has four slots: x, y, width and height.
        """
        return cls(struct.x, struct.y, struct.width, struct.height)

    @classmethod
    def from_dict(cls, dic):
        """
            Create a new :class:`Rect` instance from the dictionary *dic* that
            has four keys: 'x' 'y', 'width' and 'height'.
        """
        return cls(dic['x'], dic['y'], dic['width'], dic['height'])
