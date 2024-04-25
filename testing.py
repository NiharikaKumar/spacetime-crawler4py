from bs4 import BeautifulSoup

html_doc = """<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>"""


from collections import defaultdict

# Read the file
file_path = "results.txt"  # Replace with the path to your file
word_counts = defaultdict(int)
counter = 0

# Assuming the file is named "word_frequencies.txt"
with open(file_path, 'r') as file:
    for line in file:
        parts = line.strip().split(':')
        if len(parts) == 2:
            word = parts[0].strip()
            frequency = int(parts[1].strip())
            word_counts[word] += frequency

            if len(word) <= 3:
                counter += 1

# Sort the dictionary by frequency in descending order
sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

# Get the top 50 items
top_50 = sorted_word_counts[:50]

# Print the top 50 most frequent words
for word, frequency in top_50:
    print(f"{word}: {frequency}")
print("counter", counter)
