
#include <string>
#include <fstream>

#include <unordered_map>
#include <vector>
#include <functional>
#include <iostream>

//assuming the symbols are chars 
#define SYMBOL_TYPE unsigned int
//first int that cannot be interpreted as a char
#define HOLE	256

//sincle symbol in the compresed sequence
struct Sequence_node
{
	Sequence_node * prev;
	SYMBOL_TYPE symbol;
	Sequence_node * next;

    //debug only
    int pos;
};

struct Priority_queue_node
{
	
};

//active pairs data. the pair itself is the key used to access 
//this in the hash table
struct Hash_entry
{
    //count of active pairs
	unsigned int count = 0;
    //last occurence of the pair in sequence
	Sequence_node* last_pair = nullptr; 
};

//structure for using std::vector as key in hashmap
struct vec_hash {
  std::size_t operator()(std::vector<SYMBOL_TYPE> const& v) const noexcept {
    std::size_t h = 0;
    for (SYMBOL_TYPE x : v)
      h = h * 31 + std::hash<SYMBOL_TYPE>{}(x);
    return h;
  }
};


int main(int argc, char ** argv)
{
	
	//read file
	const char* path = argv[1];
    std::ifstream in(path, std::ios::binary | std::ios::ate);
    if (!in) {
        std::cerr << "Error: could not open file \"" << path << "\"\n";
        return 1;
    }

    // 1) Get total byte count
    std::streamsize sequence_size = in.tellg();
	Sequence_node * sequence; //array allocated by new
	sequence = new Sequence_node[sequence_size];
	
    // 2) Rewind to start
    in.seekg(0, std::ios::beg);
	
	std::unordered_map<std::vector<SYMBOL_TYPE>, Hash_entry, vec_hash> hashmap;

    // 3) Iterate over each byte
	char c;
	in.get(c);
	SYMBOL_TYPE last_symbol = (SYMBOL_TYPE) c;
	SYMBOL_TYPE symbol;
	int i = 0;
	sequence[i++].symbol = last_symbol;
     while (in.get(c)) {
		symbol = (SYMBOL_TYPE) c;
		
		sequence[i].symbol = symbol;
        sequence[i].pos = i;
		
		Hash_entry & hash_entry = hashmap[{last_symbol, symbol}];
		hash_entry.count++;
		if (hash_entry.last_pair != nullptr)
		{
			hash_entry.last_pair->next = &sequence[i];
			sequence[i].prev = hash_entry.last_pair;
		}
        hash_entry.last_pair = &sequence[i];
		
        last_symbol = symbol;
		i++;
    }
	
	
	//------------------DEBUGGING---------------------
	
	 // Print each element’s address, prev, symbol, next
     for (int i = 0; i < sequence_size; ++i) {
     std::cout << "Node[" << i << "] " 
                   << " | symbol=" << (char) sequence[i].symbol
               << " | prev="
               << (sequence[i].prev
                        ? std::to_string(sequence[i].prev->pos)
                        : std::string("null"))
               << " | next="
               << (sequence[i].next
                       ? std::to_string(sequence[i].next->pos)
                       : std::string("null"))
               << '\n';
    }
	
	
	//read input
	
	
	//encode characters into numbers (so we could add phases) -> unnecessary if assuming chars
	//construct array of sequence nodes 
	//construct hash table
	//construct priority queue
	
	//for first_bucket in priority_queue:
	//	for pair in first_bucket:
	//		replace pair with phases
	//		enter pairs with phase into queue and hash table
	

	//profit??
	
	delete[] sequence;
} 
