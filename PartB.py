import sys
from PartA import *



"""
Runtime Complexity: O(n + m + n log n) where n is size of file1 and m is size of file2.
                    This is because we have to get the tokens from both files in order to 
                    compare them, and then find their intersections to get the commonalities.

"""
def findCommonalities(file1: str, file2: str) -> None:
    word_set1 = set(get_tokens(file1)) 
    word_set2 = set(get_tokens(file2))
    
    common = word_set1 & word_set2

    for word in common:
        print(word)
    
    print(len(common))



def main() -> None:
    """ driver code that runs this part.
    """
    args = sys.argv
    total_args = len(args)

    if total_args < 3 or total_args > 3:
        print("Error: Please enter the correct number of arguments on the command line")
    else:
        file1 = args[1]
        file2 = args[2]
        findCommonalities(file1, file2)



if __name__ == "__main__":
    main()