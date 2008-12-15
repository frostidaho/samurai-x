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

import samuraix.event
from samuraix.xcb import _xcb

class ResourceMeta(type):
    def __new__(mcs, name, bases, dct):
        return type.__new__(mcs, name, bases, dct)

    def __call__(cls, connection, xid, *args, **kwargs):
        cached = connection.get_from_cache(xid)
        if cached:
            assert isinstance(cached, cls) # if that one fails, it's a bug. xids are not unique then.
            return cached
        else:
            obj = type.__call__(cls, connection, xid, *args, **kwargs)
            connection.add_to_cache(obj)
            return obj

class Resource(samuraix.event.EventDispatcher):
    __metaclass__ = ResourceMeta

    @classmethod
    def create(cls, connection):
        return cls(connection, _xcb.xcb_generate_id(connection._connection))

    def __init__(self, connection, xid):
        self.connection = connection
        self._xid = xid

    def __eq__(self, other):
        return self._xid == other._xid
    
    def xize(self):
        return self._xid

    def delete(self):
        """ 
            The resource is going to be deleted. Remove it from
            the cache.
        """
        self.connection.remove_from_cache(self)
