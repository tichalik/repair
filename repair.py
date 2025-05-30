#!/usr/bin/env python
# coding: utf-8

# In[10]:


#!jupyter nbconvert --to='script' repair.ipynb


# In[3]:


def string_to_symbol_list(string):
    last_symbol = 0
    symbol_list = []
    char_to_symbol_dict = {}

    for x in string:
        if x not in char_to_symbol_dict:
            char_to_symbol_dict[x] = last_symbol
            last_symbol += 1
        symbol_list.append(char_to_symbol_dict[x])

    return (symbol_list, char_to_symbol_dict)


# In[5]:


#assuming sequence goes left to right 
class KTupleInfo:
    def __init__(self, count=0, last=-1, first=-1):
        self.count = count
        self.orig_count = 0 #stays 0 for pairs created in replacement
        self.last = last
        self.first = first

    @classmethod
    def get_print_lines(cls, items):
        lines = [f"{'Key':<6} {'Count':<6} {'Last':<6}",
                 "-" * 32]
        for i, item in items.items():
            lines.append(f"{str(i):<6} {item.count:<6} {item.last:<6}")
        return lines

    def __repr__(self):
        return f"KTupleInfo(count={self.count}, last={self.last})"

    def __eq__(self, other):
        if not isinstance(other, KTupleInfo):
            return NotImplemented
        return self.count == other.count and self.last == other.last




class SequenceElement:
    def __init__(self, symbol=None, pos=-1, prev_k_tuple=-1, next_k_tuple=-1):
        self.symbol = symbol
        self.pos = pos
        self.prev_k_tuple = prev_k_tuple
        self.next_k_tuple = next_k_tuple

    @classmethod
    def get_print_lines(cls, items):
        lines = [f"{'Index':<6} {'Symbol':<10} {'Pos':<6} {'PrevKTuple':<12} {'NextKTuple':<12}",
                 "-" * 50]
        for i, item in enumerate(items):
            lines.append(f"{str(i):<6} {str(item.symbol):<10} {item.pos:<6} {str(item.prev_k_tuple):<12} {str(item.next_k_tuple):<12}")
        return lines

    def __repr__(self):
        return (f"SequenceElement(symbol={self.symbol}, prev_k_tuple={self.prev_k_tuple}, pos={self.pos}, "
                f"next_k_tuple={self.next_k_tuple})")

    def __eq__(self, other):
        if not isinstance(other, SequenceElement):
            return NotImplemented
        return (self.symbol == other.symbol and
                self.pos == other.pos and
                self.prev_k_tuple == other.prev_k_tuple and
                self.next_k_tuple == other.next_k_tuple)


def construct_active_k_tuples_and_sequence(symbol_list, k):
    active_k_tuples = {}
    sequence = []

    for i in range(k - 1):
        elem = SequenceElement()
        elem.symbol = symbol_list[i]
        elem.prev_k_tuple = -1
        elem.pos = i
        elem.next_k_tuple = -1
        sequence.append(elem)

    for i in range(k - 1, len(symbol_list)):
        k_tuple = tuple(symbol_list[i - k + 1:i + 1])
        if k_tuple not in active_k_tuples:
            info = KTupleInfo()
            info.count = 1
            info.orig_count = 1
            info.last = i
            active_k_tuples[k_tuple] = info

            elem = SequenceElement()
            elem.symbol = symbol_list[i]
            elem.prev_k_tuple = -1
            elem.pos = i
            elem.next_k_tuple = -1
            sequence.append(elem)
        else:
            prev_index = active_k_tuples[k_tuple].last
            active_k_tuples[k_tuple].count += 1
            active_k_tuples[k_tuple].orig_count = active_k_tuples[k_tuple].count
            active_k_tuples[k_tuple].last = i

            elem = SequenceElement()
            elem.symbol = symbol_list[i]
            elem.pos = i
            elem.prev_k_tuple = prev_index
            sequence[prev_index].next_k_tuple = i
            sequence.append(elem)

    return sequence, active_k_tuples


# In[8]:


# we use a dict based on priorities to manage priority queue
# no use for bothering with heapq

def construct_priority_queue(active_k_tuples):

    max_count = 0
    for v in active_k_tuples.values():
        if v.count > max_count:
            max_count = v.count

    priority_queue = {i+1 : set() for i in range(max_count)}

    for k, v in active_k_tuples.items():
        priority_queue[v.count].add(k)

    return priority_queue


# In[9]:


def replace_active_k_tuple(priority_queue, active_k_tuples, sequence, k_tuple, new_symbol,k):
    #works only for k=2
    #then need to come up with way to replace all the deleted tuples

    #NotASymbol
    NAS = -1
    def get_prev_index(node): 
        #return -1 if not found
        if node.pos == 0:
            return -1 
        elif sequence[node.pos-1].symbol != NAS:
            return node.pos-1
        else:
            return sequence[node.pos-1].prev_k_tuple

    def get_next_index(node):
        #return -1 if not found
        if node.pos == len(sequence)-1:
            return -1 
        elif sequence[node.pos+1].symbol != NAS:
            return node.pos+1
        else:
            return sequence[node.pos+1].next_k_tuple

    #keys of active_k_tuples which were changes anyhow
    changed_k_tuples = set()

    # assumming sequence = ... A B C D ... 
    # where (B, C) is the pair to be replaced
    # i_X means the index of X

    i_C = active_k_tuples[k_tuple].last
    while i_C != -1:
        #------------------replace single pair------------------

        C = sequence[i_C]
        B = sequence[get_prev_index(C)]

        i_A = get_prev_index(B)
        i_D = get_next_index(C)

        changed_k_tuples.add((B.symbol, C.symbol))
        if i_A != -1:
            changed_k_tuples.add((sequence[i_A].symbol, B.symbol))
            changed_k_tuples.add((sequence[i_A].symbol, new_symbol))
        if i_D != -1:
            changed_k_tuples.add((C.symbol, sequence[i_D].symbol))
            changed_k_tuples.add((new_symbol, sequence[i_D].symbol))


        #update counts in active_k_tuples - decrement old
        active_k_tuples[(B.symbol, C.symbol)].count -= 1
        if i_A != -1:
            active_k_tuples[(sequence[i_A].symbol, B.symbol)].count -=1
        if i_D != -1:
            active_k_tuples[(C.symbol, sequence[i_D].symbol)].count -=1

        #update counts in active_k_tuples - increment new
        if i_A != -1:
            if (sequence[i_A].symbol, new_symbol) not in active_k_tuples:
                active_k_tuples[(sequence[i_A].symbol, new_symbol)] = KTupleInfo()
            active_k_tuples[(sequence[i_A].symbol, new_symbol)].count +=1
        if i_D != -1:
            if (new_symbol, sequence[i_D].symbol) not in active_k_tuples:
                active_k_tuples[(new_symbol, sequence[i_D].symbol)] = KTupleInfo()
            active_k_tuples[(new_symbol, sequence[i_D].symbol)].count +=1


        #update list beginnings in active_k_tuples for old pairs 
        active_k_tuples[(B.symbol, C.symbol)].last = C.prev_k_tuple
        # rightmost goes first!!!
        if i_D != -1:
            if active_k_tuples[(C.symbol, sequence[i_D].symbol)].last == sequence[i_D].pos:
                #if this is the last C D in sequence:
                active_k_tuples[(C.symbol, sequence[i_D].symbol)].last = sequence[i_D].prev_k_tuple
        if i_A != -1:
            if active_k_tuples[(sequence[i_A].symbol, B.symbol)].last == B.pos:                                         
                #if this is the last A B in sequence:
                active_k_tuples[(sequence[i_A].symbol, B.symbol)].last = B.prev_k_tuple

        #update list beginnings in active_k_tuples for new pairs 
        #this can be done when inserting them into active_k_tuples - this is just dumb, unoptimized version
        if i_A != -1:
            if active_k_tuples[(sequence[i_A].symbol, new_symbol)].last  == -1:
                active_k_tuples[(sequence[i_A].symbol, new_symbol)].last = C.pos
        if i_D != -1:
            if active_k_tuples[(new_symbol, sequence[i_D].symbol)].last  == -1:
                active_k_tuples[(new_symbol, sequence[i_D].symbol)].last = sequence[i_D].pos


        #update threading - old pairs
        if C.prev_k_tuple != -1:
            sequence[C.prev_k_tuple].next_k_tuple = -1
        #there never is C.next_k_tuple
        if i_A != -1:
            if B.prev_k_tuple != -1:
                sequence[B.prev_k_tuple].next_k_tuple = B.next_k_tuple
            if B.next_k_tuple != -1:
                sequence[B.next_k_tuple].prev_k_tuple = B.prev_k_tuple
        if i_D != -1:
            if sequence[i_D].prev_k_tuple != -1:
                sequence[sequence[i_D].prev_k_tuple].next_k_tuple = sequence[i_D].next_k_tuple
            if sequence[i_D].next_k_tuple != -1:
                sequence[sequence[i_D].next_k_tuple].prev_k_tuple = sequence[i_D].prev_k_tuple

        #update threading - new pairs 
            # WATCHOUT!!! PROBLEM WITH first WHEN NOT RUNNING THE CODE IN LOOP 
            # we can simulate the loop with the new pairs already existing in the sequence
            # but those do not have .first configured properly, instead they have -1
            # so newly added AE/ED do not point to AE/ED already present in the sequence
        if i_A != -1:
            C.next_k_tuple = active_k_tuples[(sequence[i_A].symbol, new_symbol)].first
            if active_k_tuples[(sequence[i_A].symbol, new_symbol)].first != -1:
                sequence[active_k_tuples[(sequence[i_A].symbol, new_symbol)].first].prev_k_tuple = C.pos
        if i_D != -1:
            sequence[i_D].next_k_tuple = active_k_tuples[(new_symbol, sequence[i_D].symbol)].first
            if active_k_tuples[(new_symbol, sequence[i_D].symbol)].first != -1:
                sequence[active_k_tuples[(new_symbol, sequence[i_D].symbol)].first].prev_k_tuple = i_D
        C.prev_k_tuple = -1
        sequence[i_D].prev_k_tuple = -1 

        #update positions of the first elements of the lists
        if i_A != -1:
            active_k_tuples[(sequence[i_A].symbol, new_symbol)].first = C.pos
        if i_D != -1:
            active_k_tuples[(new_symbol, sequence[i_D].symbol)].first = sequence[i_D].pos
        #redundant - nobody cares about first element of the removed list 
        if active_k_tuples[(B.symbol, C.symbol)].first == C.pos:
            active_k_tuples[(B.symbol, C.symbol)].first = -1

        #manage empty spaces
        if B.pos == 0:
            pass # prev_k_tuple remains -1
        elif sequence[B.pos-1].symbol != NAS:
            B.prev_k_tuple = B.pos-1
        else:
            B.prev_k_tuple = sequence[B.pos-1].prev_k_tuple
        if B.pos == len(sequence) -1:
            pass # next_k_tuple remains -1
        elif sequence[B.pos+1].symbol != NAS:
            B.next_k_tuple = B.pos+1
        else:
            B.next_k_tuple = sequence[B.pos+1].next_k_tuple


        #change symbols
        B.symbol = NAS
        C.symbol = new_symbol

        i_C = active_k_tuples[k_tuple].last

    #update queues
    for changed in changed_k_tuples:

        #if it is not a new pair - new pairs are not in the queue yet 
        if active_k_tuples[changed].orig_count != 0:
            priority_queue[active_k_tuples[changed].orig_count].discard(changed)

        if active_k_tuples[changed].count == 0:
            del active_k_tuples[changed]
        else:
            priority_queue[active_k_tuples[changed].count].add(changed)
            active_k_tuples[changed].orig_count = active_k_tuples[changed].count 


# In[ ]:




