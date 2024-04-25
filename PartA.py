import sys



"""
write a program that takes one text file as an argument and outputs the token frequencies.
"""



"""
Runtime complexity: O(1) because it is just doing integer comparison.
                    The function just consists of a series of if-else
                    statements, and there are 3 if-else comparison that
                    each input has to do.

"""
def is_alphanum(character: str) -> bool:
    """returns true/false depending on whether a character is an alphanumeric 
        character, i.e. is between A-Z or a-z or 0-9"""
    
    # a-z is 97-122 included
    # A-Z is 65-90 included
    # 0-9 is 48-57 included

    if 48 <= ord(character) <= 57:
        return True
    elif 65 <= ord(character) <= 90:
        return True
    elif 97 <= ord(character) <= 122:
        return True
    else:
        return False



"""
Runtime complexity: O(n). This function runs in linear time because it reads all the
                    characters in a given file. Since the amount of characters in a file
                    can differ, the function will take as long as there are number of characters
                    to read. Even if the character is not alphanumeric, the file still needs
                    to read to assess that its not alphanum.

"""
def get_tokens(file_path: str) -> list[str]:
    """ takes in a filename, and parses it byte-by-byte, assesses whether it is an alphanumeric
        character, and splits the file into tokens which are split on each 
        non-alphnum character.
    
    """
    tokens = []

    try:
        with open(file_path, 'r') as myfile:
            
            mybyte = myfile.read(1)
            word = ""

            while mybyte: 
                if is_alphanum(mybyte):
                    word += mybyte
                else:
                    if len(word) > 0:
                        word = word.lower()
                        tokens.append(word)
                        word = ""
                mybyte = myfile.read(1)

        return tokens
    
    except FileNotFoundError:
        print(f"Unable to open file {file_path}")
    except Exception as e:
        print(f"An error occured while opening file {file_path}")



""" 
Runtime complexity: O(n) because it ONLY uses a O(n) function described above
                    called get_tokens.
"""
def tokenize(file_path: str) -> list[str]:
    """ gets a file path, and tokenizes the words in it by splitting on every non-alphanumeric
        character.
    """
    return get_tokens(file_path)



"""
Runtime Complexity: O(n) because it iterates through all the tokens that were generated
                    from the file path. Since the number of tokens very based on the file,
                    it will take linear time to traverse the entire list once. The time 
                    complexity of this function grows linearly with the size of the token_list.

"""
def computeWordFrequencies(token_list: list[str]) -> dict[str, int]:
    """ creates a dictionary where the key corresponds to a unique token, and its associated value
        corresponds to its frequency in the file/token_list.
    """
    word_frequencies = {}

    for token in token_list:
        if token in word_frequencies:
            word_frequencies[token] += 1
        else:
            word_frequencies[token] = 1

    return word_frequencies



"""
Runtime Complexity: O(n log n). printResult uses the inbuilt sorted method to sort the key/value
                    pairs by most frequently seen words. Python's sort function runs in O(n log n)
                    complexity because it needs to make O(n log n) comparisons to determine the correct
                    order of elements in the worst case.
"""
def printResult(token_frequencies: dict[str, int]) -> None:
    """ takes in a dictionary of word: frequency key,value pairs and sorts the dictionary by values
        first (frequency) and keys second in cases of ties (alphabetically).
    """
    token_frequencies = sorted(token_frequencies.items(), key=lambda kv: (-kv[1], kv[0]),)

    for k, v in token_frequencies:
        print(f"{k}\t{v}")




def main() -> None:
    """driver code that takes in file name and calls the appropriate 
        functions in correct order
    """
    args = sys.argv
    total_args = len(args)

    if total_args < 2 or total_args > 2:
        print("Error: Please enter the correct number of arguments on the command line")
    else:
        file_path = args[1]
        token_list = tokenize(file_path)
        word_frequencies = computeWordFrequencies(token_list)
        printResult(word_frequencies)



if __name__ == "__main__":
    main()