#! /usr/bin/python

import math
import random
import sys

def pad (string, padded_length, padding_char = " ") :
    return string + padding_char * (padded_length - len (string))

class Set (object) :
    """Models the set as in the set-associative cache."""
    dirty, clean = 1, 0

    def __init__ (self,
                  size,
                  tag_bit_length,
                  write_no_allocate) :
        self.dict = {}
        self.capacity = size
        self.seen_tags = set ()
        self.cold_miss_count = 0
        self.conflict_miss_count = 0
        self.access_count = 0
        self.tag_bit_length = tag_bit_length
        self.write_no_allocate = write_no_allocate

    def __str__ (self) :
        """A suitably space separated list of tags in the set.
        Tags in hex, a * shows a dirty tag."""
        str_repr = ""
        for key in self.dict :
            modified = ' '
            if self.dict [key] == self.dirty : modified = '*'
            str_repr += (
                ' '
                + pad (hex (key) [2:]
                       + modified,
                       1 + self.tag_bit_length / 4)
                + ' ')
        return str_repr

    def __writeBack (self, tag) :
        # As we are just counting the number of misses and hits,
        # and not the performance in terms of time and latency etc,
        # What happens here is irrlevant.
        pass

    def pickBlockToEvict (self) :
        return random.choice (self.dict.keys ())

    def evictAndWrite (self, tag_to_be_written, dirty_status) :
        """ Picks a tag to be evicted, writes its contents back
        to memory if dirty and then writes the tag_to_be_written
        to the set.
        dirty_status : whether the block we just wrote to the cache
                       should be marked dirty or clean. """
        tag_to_replace = self.pickBlockToEvict ()
        if self.dict [tag_to_replace] == self.dirty :
            self.__writeBack (tag_to_be_written)
        self.dict.pop (tag_to_replace)
        self.dict [tag_to_be_written] = dirty_status

    def writeOrRead (self, tag, dirty_status) :
        self.access_count += 1
        # Hit : Tag is present.
        # Miss : Tag is not present
        # -> tag not in seen tags : cold miss
        # -> else if set is full : conflict miss

        # Hit
        if tag in self.dict :
            pass

        # Also, don't do anything if it is a write miss and we are using
        # write no allocate policy. Just increment the counts.
        elif self.write_no_allocate and dirty_status == self.dirty :
            # Cold miss
            if tag not in self.seen_tags :
                self.cold_miss_count += 1
                self.seen_tags.add (tag)
            # Conflict miss
            else :
                self.conflict_miss_count += 1

        # Cold miss
        elif tag not in self.seen_tags :
            self.cold_miss_count += 1
            if len (self.dict) == self.capacity :
                self.evictAndWrite (tag, dirty_status)
            else :
                self.dict [tag] = dirty_status
            self.seen_tags.add (tag)

        # Conflict miss
        else :
            self.conflict_miss_count += 1
            # TODO: Remove this kludgy workaround
            # normal, expected case :
            # tag not in cache, tag has been seen
            # that must mean the set is full
            if (len (self.dict) == self.capacity) :
                self.evictAndWrite (tag, dirty_status)
            # case at hand :
            # write no allocate, wrote tag foo
            # that will mark tag foo as seen
            # read tag foo
            # the set has some space, still the execution will come here
            # and if the set is empty, evictAndWrite will fail.
            elif (self.write_no_allocate
                  and dirty_status == self.clean) :
                self.dict [tag] = self.clean 
            else :
                sys.exit ("Logic fail! Should never come here.")

    def write (self, tag) :
        self.writeOrRead (tag, self.dirty)

    def read (self, tag) :
        self.writeOrRead (tag, self.clean)
            

class Cache (object) :
    
    def __init__ (self,
                  n_sets,
                  n_ways,
                  block_size,
                  sample_addr = "0xb7737f64",
                  set_class = Set,
                  write_no_allocate = False) :
        self.n_sets = n_sets
        self.n_ways = n_ways
        self.block_size = block_size

        # Calculate various bit lengths for splitting up of address
        self.addr_bit_length = 4 * len (sample_addr.split ("x") [1])
        self.block_addr_bit_length = (
            self.addr_bit_length
            - int (math.log (self.block_size, 2)))
        self.set_number_bit_length = int (math.log (self.n_sets, 2))
        self.tag_bit_length = (self.block_addr_bit_length
                               -
                               self.set_number_bit_length)

        # Now create the sets.
        self.array = [set_class (n_ways,
                                 self.tag_bit_length,
                                 write_no_allocate)
                      for foo in range (n_sets)]

    def __splitAddr (self, addr) :
        """ Returns a tuple with tag, set_number.
        the memory is assumed to be byte addressable and further it
        is assumed that the address given by the addr is the byte
        address of the memory location. """
        try :
            addr = int (addr, 0)
        except :
            pass
        block_addr = addr / self.block_size

        # [tag | set_number | byte offset in block]

        # Now, in the block address, we need to choose
        # The most significant set_bits number of bits.
        set_number = block_addr % (2 ** self.set_number_bit_length)
        tag = block_addr / (2 ** self.set_number_bit_length)
        return (tag, set_number)

    def __str__ (self) :
        return "\n".join ([pad (hex (i) [2:],
                                self.set_number_bit_length / 4)
                           + " : "
                           + self.array[i].__str__()
                           for i in range (len (self.array))])

    def write (self, addr) :
        tag, set_number = self.__splitAddr (addr)
        self.array [set_number].write (tag)

    def read (self, addr) :
        tag, set_number = self.__splitAddr (addr)
        self.array [set_number].read (tag)

    def printStats (self) :
        separator = "=================="
        print pad (self.__class__.__name__ + " specs", len (separator))
        print separator
        size = self.n_sets * self.n_ways * self.block_size
        if size >= 1048576 :
            size = str (size / 1048576) + 'M'
        elif size >= 1024 :
            size = str (size / 1024) + "K"

        block_size = self.block_size
        if block_size >= 1048576 :
            block_size = str (block_size / 1048576) + 'M'
        elif block_size >= 1024 :
            block_size = str (block_size / 1024) + "K"
            
        print "size       :", size
        print "block size :", block_size
        print "sets       :", self.n_sets
        print "ways       :", self.n_ways
        print separator
        for count in ['access_count',
                      'cold_miss_count',
                      'conflict_miss_count'] :
            print (str (self.getCumulativeCount (count))
                   + '\t'
                   + ' '.join (count.split ('_')))
        miss = (self.getCumulativeCount ('cold_miss_count')
                + self.getCumulativeCount ('conflict_miss_count'))
        total = self.getCumulativeCount ('access_count')
        print ("Hit Rate : "
               + str (round (100 * (1 - float (miss) / total), 3))
               + "%")

    def getCumulativeCount (self, attr_name) :
        return sum ([set_.__getattribute__(attr_name)
                     for set_ in self.array])

class LRUSet (Set) :
    def __init__ (self, *args, **kwargs) :
        super(LRUSet, self).__init__ (*args, **kwargs)
        # [least recently used, ...., most recently used]
        self.recency_list = []

    def pickBlockToEvict (self) :
        tag = self.recency_list [0]
        self.recency_list = self.recency_list [1:]
        return tag

    def writeOrRead (self, tag, dirty_status) :
        super(LRUSet, self).writeOrRead (tag, dirty_status)
        # Remove the tag if it were there in the recency list
        # and put it at the end of the list.
        try :
            self.recency_list.remove (tag)
        except :
            # If it was a write miss, and it is write no allocate,
            # do nothing else.
            if (self.write_no_allocate
                and tag not in self.dict
                and dirty_status == self.dirty) : return
        self.recency_list.append (tag)

class LRUCache (Cache) :
    def __init__ (self, *args, **kwargs) :
        kwargs ['set_class'] = LRUSet
        super(LRUCache, self).__init__ (*args, **kwargs)

class LFUSet (Set) :
    def __init__ (self, *args, **kwargs) :
        super(LFUSet, self).__init__ (*args, **kwargs)
        # {tag:frequency}
        self.frequency_dict = {}

    def pickBlockToEvict (self) :
        # Pick the tag with least frequency
        frequencies = self.frequency_dict.values ()
        frequencies.sort ()
        least_frequency = frequencies [0]
        for tag in self.frequency_dict :
            if self.frequency_dict [tag] == least_frequency :
                self.frequency_dict.pop (tag)
                return tag

    def writeOrRead (self, tag, dirty_status) :
        super(LFUSet, self).writeOrRead (tag, dirty_status)

        # If it was a write miss, and it is write no allocate,
        # do nothing else.
        if (self.write_no_allocate
            and tag not in self.dict
            and dirty_status == self.dirty) : return

        # Update the frequency value of that tag
        try :
            self.frequency_dict [tag] += 1
        except :
            self.frequency_dict [tag] = 1

class LFUCache (Cache) :
    def __init__ (self, *args, **kwargs) :
        kwargs ['set_class'] = LFUSet
        super(LFUCache, self).__init__ (*args, **kwargs)

class FIFOSet (Set) :
    def __init__ (self, *args, **kwargs) :
        super(FIFOSet, self).__init__ (*args, **kwargs)
        # [oldest tag added to set, ..., newest tag added to set]
        self.tag_queue = []

    def pickBlockToEvict (self) :
        tag = self.tag_queue [0]
        self.tag_queue = self.tag_queue [1:]
        return tag

    def writeOrRead (self, tag, dirty_status) :
        super(FIFOSet, self).writeOrRead (tag, dirty_status)

        # If it was a write miss, and it is write no allocate,
        # do nothing else.
        if (self.write_no_allocate
            and tag not in self.dict
            and dirty_status == self.dirty) : return

        # If it is a new tag, add it as the newest tag
        if tag not in self.tag_queue :
            self.tag_queue.append (tag)

class FIFOCache (Cache) :
    def __init__ (self, *args, **kwargs) :
        kwargs ['set_class'] = FIFOSet
        super(FIFOCache, self).__init__ (*args, **kwargs)

if __name__ == "__main__" :
    foo = FIFOCache (16, 3, 1, '0xb00', write_no_allocate = False)
    foo.write (0xa2b)
    foo.write (0xa3c)
    foo.write (0xa2d)
    foo.write (0xa2e)
    foo.write (0xa4f)
    foo.write (0xa40)
    foo.write (0xa51)
    print foo
    foo.printStats()
