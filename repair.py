#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!jupyter nbconvert --to='script' repair.ipynb


# In[107]:


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


# In[108]:

#assuming sequence goes left to right 
class KTupleInfo:
    def __init__(self):
        self.count = 0
        self.last = -1      #the rightmost pair
        self.first = -1     #the leftmost pair
        self.pos_in_queue = -1

    @classmethod
    def print_dict(cls, items):
        print(f"{'Key':<6} {'Count':<6} {'Last':<6} {'PosInQueue':<12}")
        print("-" * 32)
        for i, item in items.items():
            print(f"{str(i):<6} {item.count:<6} {item.last:<6} {item.pos_in_queue:<12}")

    def __repr__(self):
        return f"KTupleInfo(count={self.count}, last={self.last}, pos_in_queue={self.pos_in_queue})"


class SequenceElement:
    def __init__(self):
        self.symbol = None
        self.pos = -1
        self.prev_k_tuple = -1
        self.next_k_tuple = -1

    @classmethod
    def print_list(cls, items):
        print(f"{'Index':<6} {'Symbol':<10} {'Pos':<6} {'PrevKTuple':<12} {'NextKTuple':<12}")
        print("-" * 50)
        for i, item in enumerate(items):
            print(f"{str(i):<6} {str(item.symbol):<10} {item.pos:<6} {str(item.prev_k_tuple):<12} {str(item.next_k_tuple):<12}")

    def __repr__(self):
        return (f"SequenceElement(symbol={self.symbol}, prev_k_tuple={self.prev_k_tuple}, pos={self.pos}, "
                f"next_k_tuple={self.next_k_tuple})")




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
            active_k_tuples[k_tuple].last = i

            elem = SequenceElement()
            elem.symbol = symbol_list[i]
            elem.pos = i
            elem.prev_k_tuple = prev_index
            sequence[prev_index].next_k_tuple = i
            sequence.append(elem)

    return sequence, active_k_tuples


# In[109]:


# we use a dict based on priorities to manage priority queue
# no use for bothering with heapq

def construct_priority_queue(active_k_tuples):
    priority_queue = {}

    for k, v in active_k_tuples.items():
        if v.count not in priority_queue:
            priority_queue[v.count] = []
        v.pos_in_queue = len(priority_queue[v.count])
        priority_queue[v.count].append(k)

    return priority_queue


# In[116]:


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
            return sequence[node.pos+1].next

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
        
        i_C = C.prev_k_tuple
        
        #update counts in active_k_tuples - decrement old
        active_k_tuples[(B.symbol, C.symbol)].count -= 1
        if i_A != -1:
            active_k_tuples[(A.symbol, B.symbol)].count -=1
        if i_D != -1:
            active_k_tuples[(C.symbol, D.symbol)].count -=1
            
        #update counts in active_k_tuples - increment new
        if i_A != -1:
            if (A.symbol, new_symbol) not in active_k_tuples:
                active_k_tuples[(A.symbol, new_symbol)] = KTupleInfo()
            active_k_tuples[(A.symbol, new_symbol)].count +=1
        if i_D != -1:
            if (new_symbol, D.symbol) not in active_k_tuples:
                active_k_tuples[(new_symbol, D.symbol)] = KTupleInfo()
            active_k_tuples[(new_symbol, D.symbol)].count +=1
        
        
        #update list beginnings in active_k_tuples for old pairs 
        active_k_tuples[(B.symbol, C.symbol)].last = C.prev_k_tuple
        if i_A != -1:
            if active_k_tuples[(A.symbol, B.symbol)].last == B.pos:                                         
                #if this is the last A B in sequence:
                active_k_tuples[(A.symbol, B.symbol)].last = B.prev_k_tuple
        if i_D != -1:
            if active_k_tuples[(C.symbol, D.symbol)].last == D.pos:
                #if this is the last C D in sequence:
                active_k_tuples[(C.symbol, D.symbol)].last = D.prev_k_tuple
        
        #update list beginnings in active_k_tuples for new pairs 
        #this can be done when inserting them into active_k_tuples - this is just dumb, unoptimized version
        if i_A != -1:
            if active_k_tuples[(A.symbol, new_symbol)].last  == -1:
                active_k_tuples[(A.symbol, new_symbol)].last = C.pos
        if i_D != -1:
            if active_k_tuples[(new_symbol, D.symbol)].last  == -1:
                active_k_tuples[(new_symbol, D.symbol)].last = D.pos
            
            
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
            if D.prev_k_tuple != -1:
                sequence[B.prev_k_tuple].next_k_tuple = D.next_k_tuple
            if D.next_k_tuple != -1:
                sequence[B.next_k_tuple].prev_k_tuple = D.prev_k_tuple
            
        #update threading - new pairs 
        if i_A != -1:
            C.next_k_tuple = active_k_tuples[(A.symbol, new_symbol)].first
        if i_D != -1:
            D.next_k_tuple = active_k_tuples[(new_symbol, D.symbol)].first
        C.prev_k_tuple = -1
        D.prev_k_tuple = -1 
        
        #update positions of the first elements of the lists
        if i_A != -1:
            active_k_tuples[(A.symbol, new_symbol)].first = C.pos
        if i_D != -1:
            active_k_tuples[(new_symbol, D.symbol)].first = D.pos
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
    
    #update queues


# # 

# # tests

# In[117]:


from pprint import pprint


# In[118]:


def debug(string, k_tuple, new_symbol):
    sequence, active_k_tuples = construct_active_k_tuples_and_sequence(string_to_symbol_list(string)[0], 2)
    priority_queue = construct_priority_queue(active_k_tuples)
    # print("-"*32)
    # print("active_k_tuples before")
    # print("-"*32)
    # KTupleInfo.print_dict(active_k_tuples)
    # print("-"*32)
    # print("priority queue before")
    # print("-"*32)
    # print(priority_queue)
    # print("-"*32)
    print("sequence before")
    print("-"*32)
    SequenceElement.print_list(sequence)
    print("-"*32)

    replace_active_k_tuple(priority_queue, active_k_tuples, sequence, k_tuple, new_symbol, 2)

    # print("-"*32)
    # print("active_k_tuples after")
    # print("-"*32)
    # KTupleInfo.print_dict(active_k_tuples)
    # print("-"*32)
    # print("priority queue after")
    # print("-"*32)
    # print(priority_queue)
    # print("-"*32)
    print("sequence after")
    print("-"*32)
    SequenceElement.print_list(sequence)
    print("-"*32)

debug("012312012", (1,2), 4)


# In[82]:


debug("012012", (1,2), 3)


# In[77]:


debug("01", (0,1), 3)


# In[63]:


string_to_symbol_list("ala ma kota")


# In[65]:


s, a = construct_active_k_tuples_and_sequence(string_to_symbol_list("0101")[0], 2)
SequenceElement.print_list(s)
KTupleInfo.print_dict(a)


# In[66]:


s, a = construct_active_k_tuples_and_sequence(string_to_symbol_list("000")[0], 2)
SequenceElement.print_list(s)
KTupleInfo.print_dict(a)


# In[67]:


s, a = construct_active_k_tuples_and_sequence(string_to_symbol_list("012012")[0], 2)
SequenceElement.print_list(s)
KTupleInfo.print_dict(a)


# In[11]:


from pprint import pprint


# In[69]:


sequence, active_k_tuples = construct_active_k_tuples_and_sequence(string_to_symbol_list("012012")[0], 2)
print("active_k_tuples before")
KTupleInfo.print_dict(active_k_tuples)
priority_queue = construct_priority_queue(active_k_tuples)
print("active_k_tuples after")
KTupleInfo.print_dict(active_k_tuples)
print("priority queue")
pprint(priority_queue)


# In[ ]:





# In[ ]:




