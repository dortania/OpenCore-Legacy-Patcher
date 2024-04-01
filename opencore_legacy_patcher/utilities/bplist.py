#################################################################################
# Copyright (C) 2009-2011 Vladimir "Farcaller" Pouzanov <farcaller@gmail.com>   #
#                                                                               #
# Permission is hereby granted, free of charge, to any person obtaining a copy  #
# of this software and associated documentation files (the "Software"), to deal #
# in the Software without restriction, including without limitation the rights  #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     #
# copies of the Software, and to permit persons to whom the Software is         #
# furnished to do so, subject to the following conditions:                      #
#                                                                               #
# The above copyright notice and this permission notice shall be included in    #
# all copies or substantial portions of the Software.                           #
#                                                                               #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR    #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,      #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE   #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER        #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN     #
# THE SOFTWARE.                                                                 #
#################################################################################

import struct
import codecs
from datetime import datetime, timedelta

class BPListWriter(object):
    def __init__(self, objects):
        self.bplist = ""
        self.objects = objects

    def binary(self):
        '''binary -> string

        Generates bplist
        '''
        self.data = 'bplist00'

        # TODO: flatten objects and count max length size

        # TODO: write objects and save offsets

        # TODO: write offsets

        # TODO: write metadata

        return self.data

    def write(self, filename):
        '''

        Writes bplist to file
        '''
        if self.bplist != "":
            pass
            # TODO: save self.bplist to file
        else:
            raise Exception('BPlist not yet generated')

class BPListReader(object):
    def __init__(self, s):
        self.data = s
        self.objects = []
        self.resolved = {}

    def __unpackIntStruct(self, sz, s):
        '''__unpackIntStruct(size, string) -> int

        Unpacks the integer of given size (1, 2 or 4 bytes) from string
        '''
        if   sz == 1:
            ot = '!B'
        elif sz == 2:
            ot = '!H'
        elif sz == 4:
            ot = '!I'
        elif sz == 8:
            ot = '!Q'
        else:
            raise Exception('int unpack size '+str(sz)+' unsupported')
        return struct.unpack(ot, s)[0]

    def __unpackInt(self, offset):
        '''__unpackInt(offset) -> int

        Unpacks int field from plist at given offset
        '''
        return self.__unpackIntMeta(offset)[1]

    def __unpackIntMeta(self, offset):
        '''__unpackIntMeta(offset) -> (size, int)

        Unpacks int field from plist at given offset and returns its size and value
        '''
        obj_header = self.data[offset]
        obj_type, obj_info = (obj_header & 0xF0), (obj_header & 0x0F)
        int_sz = 2**obj_info
        return int_sz, self.__unpackIntStruct(int_sz, self.data[offset+1:offset+1+int_sz])

    def __resolveIntSize(self, obj_info, offset):
        '''__resolveIntSize(obj_info, offset) -> (count, offset)

        Calculates count of objref* array entries and returns count and offset to first element
        '''
        if obj_info == 0x0F:
            ofs, obj_count = self.__unpackIntMeta(offset+1)
            objref = offset+2+ofs
        else:
            obj_count = obj_info
            objref = offset+1
        return obj_count, objref

    def __unpackFloatStruct(self, sz, s):
        '''__unpackFloatStruct(size, string) -> float

        Unpacks the float of given size (4 or 8 bytes) from string
        '''
        if   sz == 4:
            ot = '!f'
        elif sz == 8:
            ot = '!d'
        else:
            raise Exception('float unpack size '+str(sz)+' unsupported')
        return struct.unpack(ot, s)[0]

    def __unpackFloat(self, offset):
        '''__unpackFloat(offset) -> float

        Unpacks float field from plist at given offset
        '''
        obj_header = self.data[offset]
        obj_type, obj_info = (obj_header & 0xF0), (obj_header & 0x0F)
        int_sz = 2**obj_info
        return int_sz, self.__unpackFloatStruct(int_sz, self.data[offset+1:offset+1+int_sz])

    def __unpackDate(self, offset):
        td = int(struct.unpack(">d", self.data[offset+1:offset+9])[0])
        return datetime(year=2001,month=1,day=1) + timedelta(seconds=td)

    def __unpackItem(self, offset):
        '''__unpackItem(offset)

        Unpacks and returns an item from plist
        '''
        obj_header = self.data[offset]
        obj_type, obj_info = (obj_header & 0xF0), (obj_header & 0x0F)
        if   obj_type == 0x00:
            if   obj_info == 0x00: # null   0000 0000
                return None
            elif obj_info == 0x08: # bool   0000 1000           // false
                return False
            elif obj_info == 0x09: # bool   0000 1001           // true
                return True
            elif obj_info == 0x0F: # fill   0000 1111           // fill byte
                raise Exception("0x0F Not Implemented") # this is really pad byte, FIXME
            else:
                raise Exception('unpack item type '+str(obj_header)+' at '+str(offset)+ 'failed')
        elif obj_type == 0x10: #     int    0001 nnnn   ...     // # of bytes is 2^nnnn, big-endian bytes
            return self.__unpackInt(offset)
        elif obj_type == 0x20: #    real    0010 nnnn   ...     // # of bytes is 2^nnnn, big-endian bytes
            return self.__unpackFloat(offset)
        elif obj_type == 0x30: #    date    0011 0011   ...     // 8 byte float follows, big-endian bytes
            return self.__unpackDate(offset)
        elif obj_type == 0x40: #    data    0100 nnnn   [int]   ... // nnnn is number of bytes unless 1111 then int count follows, followed by bytes
            obj_count, objref = self.__resolveIntSize(obj_info, offset)
            return self.data[objref:objref+obj_count] # XXX: we return data as str
        elif obj_type == 0x50: #    string  0101 nnnn   [int]   ... // ASCII string, nnnn is # of chars, else 1111 then int count, then bytes
            obj_count, objref = self.__resolveIntSize(obj_info, offset)
            return self.data[objref:objref+obj_count]
        elif obj_type == 0x60: #    string  0110 nnnn   [int]   ... // Unicode string, nnnn is # of chars, else 1111 then int count, then big-endian 2-byte uint16_t
            obj_count, objref = self.__resolveIntSize(obj_info, offset)
            return self.data[objref:objref+obj_count*2].decode('utf-16be')
        elif obj_type == 0x80: #    uid     1000 nnnn   ...     // nnnn+1 is # of bytes
            # FIXME: Accept as a string for now
            obj_count, objref = self.__resolveIntSize(obj_info, offset)
            return self.data[objref:objref+obj_count]
        elif obj_type == 0xA0: #    array   1010 nnnn   [int]   objref* // nnnn is count, unless '1111', then int count follows
            obj_count, objref = self.__resolveIntSize(obj_info, offset)
            arr = []
            for i in range(obj_count):
                arr.append(self.__unpackIntStruct(self.object_ref_size, self.data[objref+i*self.object_ref_size:objref+i*self.object_ref_size+self.object_ref_size]))
            return arr
        elif obj_type == 0xC0: #   set      1100 nnnn   [int]   objref* // nnnn is count, unless '1111', then int count follows
            # XXX: not serializable via apple implementation
            raise Exception("0xC0 Not Implemented") # FIXME: implement
        elif obj_type == 0xD0: #   dict     1101 nnnn   [int]   keyref* objref* // nnnn is count, unless '1111', then int count follows
            obj_count, objref = self.__resolveIntSize(obj_info, offset)
            keys = []
            for i in range(obj_count):
                keys.append(self.__unpackIntStruct(self.object_ref_size, self.data[objref+i*self.object_ref_size:objref+i*self.object_ref_size+self.object_ref_size]))
            values = []
            objref += obj_count*self.object_ref_size
            for i in range(obj_count):
                values.append(self.__unpackIntStruct(self.object_ref_size, self.data[objref+i*self.object_ref_size:objref+i*self.object_ref_size+self.object_ref_size]))
            dic = {}
            for i in range(obj_count):
                dic[keys[i]] = values[i]
            return dic
        else:
            raise Exception('don\'t know how to unpack obj type '+hex(obj_type)+' at '+str(offset))

    def __resolveObject(self, idx):
        try:
            return self.resolved[idx]
        except KeyError:
            obj = self.objects[idx]
            if type(obj) == list:
                newArr = []
                for i in obj:
                    newArr.append(self.__resolveObject(i))
                self.resolved[idx] = newArr
                return newArr
            if type(obj) == dict:
                newDic = {}
                for k,v in obj.items():
                    key_resolved = self.__resolveObject(k)
                    if isinstance(key_resolved, str):
                        rk = key_resolved
                    else:
                        rk = codecs.decode(key_resolved, "utf-8")
                    rv = self.__resolveObject(v)
                    newDic[rk] = rv
                self.resolved[idx] = newDic
                return newDic
            else:
                self.resolved[idx] = obj
                return obj

    def parse(self):
        # read header
        if self.data[:8] != b'bplist00':
            raise Exception('Bad magic')

        # read trailer
        self.offset_size, self.object_ref_size, self.number_of_objects, self.top_object, self.table_offset = struct.unpack('!6xBB4xI4xI4xI', self.data[-32:])
        #print "** plist offset_size:",self.offset_size,"objref_size:",self.object_ref_size,"num_objs:",self.number_of_objects,"top:",self.top_object,"table_ofs:",self.table_offset

        # read offset table
        self.offset_table = self.data[self.table_offset:-32]
        self.offsets = []
        ot = self.offset_table
        for i in range(self.number_of_objects):
            offset_entry = ot[:self.offset_size]
            ot = ot[self.offset_size:]
            self.offsets.append(self.__unpackIntStruct(self.offset_size, offset_entry))
        #print "** plist offsets:",self.offsets

        # read object table
        self.objects = []
        k = 0
        for i in self.offsets:
            obj = self.__unpackItem(i)
            #print "** plist unpacked",k,type(obj),obj,"at",i
            k += 1
            self.objects.append(obj)

        # rebuild object tree
        #for i in range(len(self.objects)):
        #    self.__resolveObject(i)

        # return root object
        return self.__resolveObject(self.top_object)

    @classmethod
    def plistWithString(cls, s):
        parser = cls(s)
        return parser.parse()

# helpers for testing
def plist(obj):
    from Foundation import NSPropertyListSerialization, NSPropertyListBinaryFormat_v1_0
    b = NSPropertyListSerialization.dataWithPropertyList_format_options_error_(obj,  NSPropertyListBinaryFormat_v1_0, 0, None)
    return str(b.bytes())

def unplist(s):
    from Foundation import NSData, NSPropertyListSerialization
    d = NSData.dataWithBytes_length_(s, len(s))
    return NSPropertyListSerialization.propertyListWithData_options_format_error_(d, 0, None, None)

if __name__ == "__main__":
    import os
    import sys
    import json
    file_path = sys.argv[1]

    with open(file_path, "rb") as fp:
        data = fp.read()

    out = BPListReader(data).parse()

    with open(file_path + ".json", "w") as fp:
        json.dump(out, indent=4)