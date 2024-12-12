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