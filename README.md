# WordSearch

## Problem Overview

- The grid consists of 10 000 * 10 000 lowercase letters (a - z), a total of 100 million letters.
- We need to check for the presence of 1 million words with an average length of 9 characters.
- Check horizontally, from left to right and vertically from top to bottom

## Key Challanges

1. Scale
    - Grid size 100 million characters
    - 1 million words
2. Two-dimensional search
    We must search both horizontally and vertically for 10 000 rows and 10 000 columns
3. Memory (we ignore this in this task)

A single scan of the grid (horizontal and vertical) would be O(200 million).
Scanning all words, with an average length of 9 characters ~O(9 million).
The naive approach would be to traverse the grid for every word. The optimal approach is to traverse the grid only once.

## Strategy

### 1. Divide the Grid Into Rows and Columns

- 10 000 rows-strings of 10 000 characters
- 10 000 col-strings of 10 000 characters

### 2. Use a Multi-pattern Search Algorithm

The biggest performance gain comes from searching for all the words simountaenously. Essentially in linear time over the grid, rather than traversing the grid multiple times. To do this, I used the **Aho-Corasick** algorithm. 

**Aho-Corasick**

- Build a finite state machine for all the words.
    - A trie of all the words we search for, and traverse this search tree when going through each row/col in the grid.
- We sacrifice some time building the trie and its failure link (However considering 9 million < 200 million, this is reasonable).
- After preprocessing (building the trie and links), we can run through each text (a row or a col) in O(text_length + num_matches)
- In summary, we pay for construction cost of the 1 million word search tree once, and can then scan each row and col in linear time (if we look past the factor of occurrences).

**Complexity**

- **n**, length of text
- **m**, length of characters in all words
- **z**, total number of occurences

**~O(n + m + z)**

### 3. Details of My Approach

The grid, standard size row length of 10 000, but can be overwritten.
I chose to create the substring rows and cols already in the constructor, for easy reference.

```python

class WordSearch:
    """ Class for searching multiple word search in a grid
    """

    def __init__(self, grid, ROW_LENGTH = 10000):
        """ Initialize the grid, define list of rows and list of cols
        args:
            grid: single string representing the whole grid
            ROW_LENGTH: length of a row
        """
        self.grid = grid
        self.n = ROW_LENGTH

        self.rows = [grid[i*self.n:(i+1)*self.n] for i in range(self.n)]
        self.columns = [''.join(col) for col in zip(*self.rows)]

```

Instead of using an `is_present` method which searches for a specific word in the grid. I created a one-time method `find_words` which creates a list inititated with the default result-value `False` and a length equal to the word-list, in the end this will mirror the word list with result values of `True` or `False`. To compute the result/the list `found` i used the Aho-Corasick algorithm, explained below.

```python

def find_words(self, words_to_find):
        """ Find the words in given list which appear in grid
            Search all row-strings and all col-strings
        args:
            words_to_find: list of the words to search for
        returns:
            a set of all words that were found in the grid
        """

        AC = AhoCorasick(words_to_find)
        found = [False] * len(words_to_find)
        
        for row_str in self.rows:
            indices = AC.search(row_str)
            for w_idx in indices:
                found[w_idx] = True

        for col_str in self.columns:
            indices = AC.search(col_str)
            for w_idx in indices:
                found[w_idx] = True

        return found

```

My implementation conflicts with the structure in the task description. This is beacuse I identified the `is_present`- search the grid for every word approach as a bottleneck, which would result in poor performance. As I mentioned before, we ideally only traverse the grid once, beacuse of its size. However, if this is a requirement this could be achieved by some structural changes.
EX:
- Store the results from find_words as a field variable
- is_present checks the stored results

```python

def is_present(self, word):
    #TODO
    return True

```

**Aho-Corasick**
The constructor for the AhoCorasick class takes the list of words as an argument, and then constructs the trie from those words. The base char is a, represented as 0 in this trie. The purpose this conversion is to make it the trie easy to work with, these digits then serve as both an index and a value. ex. if `c_idx = 1` and we type self.next[ current ] [ c_idx ] then we check the current node's "next" node 'b', -1 if this isn't a valid sequence. 
Each Node: 
- next array, size 26 for all possible characters in the alphabet
- a fail link, which points to the longest possible suffix, where we can continue the pattern matching.
- an array `output` storing indexes which end at the given node.

A better explaination and vizualization of the trie: https://www.geeksforgeeks.org/aho-corasick-algorithm-pattern-searching/ 

**each node** 

```python

class AhoCorasick:
    """ Aho-Corasick automaton for matching multiple patterns.
        This class builds a trie from the given words, then constructs failure links 
        to allow simultaneous pattern matching against any text.
    """

    def __init__(self, word_list):
        """ Init the automaton with a list of words
        args:
            word_list: words to find, insert these words into the automaton
        """
        self.alphabet_size = 26
        self.base_char = ord('a')

        # Each node (root is node 0): 
        # 'next' array of size 26 for next char
        # 'fail' link
        # 'output' list to store indexes of words that end at this node
        self.next = []
        self.fail = []
        self.output = []

        self._create_node()

        for i, word in enumerate(word_list):
            self._insert(word, i)
        
        self._build_fail_links()

```

Create a new node.

```python

def _create_node(self):
    """ Create a new node
    returns:
        index of new node
    """
    self.next.append([-1] * self.alphabet_size)
    self.fail.append(-1)
    self.output.append([])
    return len(self.next) - 1

```

Convert a char to a numeric index for easy look-ups. 

```python

def _char_to_index(self, c):
    """convert chars to numeric index, (ex. a -> 0, b -> 1)"""
    return ord(c) - self.base_char

```

Inserts a word into the trie. Every word starts from the root. Convert the char to its numeric index and see if it already exists in the trie, if not, create a new node. Change current and proceed with the next char. When the entire word is inserted, add its index to the ouput array.

```python

def _insert(self, word, index):
    """ Insert a word into the trie.
    args: 
        word: word to insert
        index: index of word in original list, used for output
    """
    current = 0
    for c in word:
        c_idx = self._char_to_index(c)
        if self.next[current][c_idx] == -1:
            self.next[current][c_idx] = self._create_node()
        current = self.next[current][c_idx]
    
    self.output[current].append(index)

```

Build fail links for all nodes.
- Firstly, all children of root point back to the root.
- We then prepare a BFS traversal of the trie, adding existing child nodes to a queue.
- Traverse the trie using BFS. By using BFS, we ensure that when we reach a node at a deeper level, all higher nodes have failure links.

```python

def _build_fail_links(self):
    """Builds the failure links using BFS, completing the Aho-Corasick automaton."""
    queue = deque()

    for c in range(self.alphabet_size):
        nxt = self.next[0][c]
        
        if nxt != -1:
            self.fail[nxt] = 0
            queue.append(nxt)
        else:
            self.next[0][c] = 0
    
    while queue:
        node = queue.popleft()
        failure = self.fail[node]

        for c in range(self.alphabet_size):
            child = self.next[node][c]
            if child != -1:
                self.fail[child] = self.next[failure][c]

                self.output[child].extend(self.output[self.fail[child]])
                queue.append(child)
            else:
                self.next[node][c] = self.next[failure][c]

```

The search method traverses the automaton, following the string `text` which is a row or a column from the grid. As we stored indexes of word-endings in each node, when we find a word, we extend the `found_indexes` list with the output list of that node. The result is a list of the indexes of all the words we found when searching through a row or a column.

```python

def search(self, text):
    """Run the automaton on given text (a row or col).
    args:
        text: the text to search
    returns:
        a list of indexes of found words.
    """
    current = 0
    found_indexes = []

    for c in text:
        c_idx = self._char_to_index(c)
        current = self.next[current][c_idx]

        if self.output[current]:
            found_indexes.extend(self.output[current])

    return found_indexes

```

### 4. Results

I tested my solution on a grid with row length 10 000, and a word list of size 10 000. This workload, not quite the size of the task description, but still significant, resulted in runtimes around 140 seconds (on my personal computer, results may vary depending on RAM, CPU, etc.). Comparing to a naive approach; using Python's `in` feature (a worst case complexity of O(N*m), where N=size of grid, m=size of word list), for every word on every row and col, this resulted in runtimes around 600 seconds. This gap would only increase with an increasing workload.

```python

import WordSearch as WS
import random
import string
import time


# Function to generate a random string of size n * m grid
def generate_random_grid(n, m):
    return ''.join(random.choices(string.ascii_lowercase, k=n * m))

# List of random words
def generate_random_words(num_words, max_word_length):
    words = []
    for _ in range(num_words):
        word_length = random.randint(1, max_word_length)
        word = ''.join(random.choices(string.ascii_lowercase, k=word_length))
        words.append(word)
    return words

# Test function runtime on row length 10,000 and 10,000 words
def test_word_search():

    n, m = 10000, 10000
    
    grid = generate_random_grid(n, m)
    words_to_find = generate_random_words(10000, 24)
    
    print("starting timer")
    start_time = time.time() #calculate runtime
    
    ws = WS.WordSearch(grid)
    result = ws.find_words(words_to_find)
    for w, res in zip(words_to_find, result):
        if res:
            print(f"found {w}")
    
    elapsed_time = time.time() - start_time
    print(f"Execution time: {elapsed_time:.4f} seconds")


if __name__ == '__main__':
    test_word_search()

```

## Bouns question

Building the automaton with a multicore system would be difficult and probably better left to a single thread, as this would be difficult to parallelize due to its complexity. However the searching phase could see improvements by dividing the workload. This could be easily implemented by, splitting the rows, say for 8 cores 1 250 for each (and similar with the columns). Each thread would then run the automaton independetly on its subset of rows and cols. The automaton is then read-only and the results written to a shared, thread-safe data structure.

## sources

https://www.geeksforgeeks.org/aho-corasick-algorithm-pattern-searching/ 
https://www.geeksforgeeks.org/aho-corasick-algorithm-in-python/ 
