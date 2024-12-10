from collections import deque

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

    
    def _create_node(self):
        """ Create a new node
        returns:
            index of new node
        """
        self.next.append([-1] * self.alphabet_size)
        self.fail.append(-1)
        self.output.append([])
        return len(self.next) - 1
    

    def _char_to_index(self, c):
        """convert chars to numeric index, (ex. a -> 0, b -> 1)"""
        return ord(c) - self.base_char
    

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


if __name__ == '__main__':
    ROW_LENGTH = 3
    grid = "abcdefghi"
    words_to_find = ["abc", #true
                     "abe", #false
                     "cba", #false
                     "adg", #true
                     "ifc", #false
                     "abcdef"] #false

    ws = WordSearch(grid, ROW_LENGTH)
    result = ws.find_words(words_to_find)

    expected = [True, False, False, True, False, False]

    assert result == expected, (
        f"failed, expected: {expected}, actual: {result}"
    )
    print("test passed")

    for w, res in zip(words_to_find, result):
        if res:
            print(f"found {w}")