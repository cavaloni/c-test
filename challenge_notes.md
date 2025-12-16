Pair Programming Assignment

While screen-sharing, in the development environment of your choice, write code that generates anagram puzzles, as described by the problem description below. Use the template code below as a starting point. This is open-book, so feel free to search online or consult documentation as we work through it.

The Customer

Your customer is a psychological research lab who is studying the phenomenon of “perfectionism.”

The researchers in this lab decide that they will use puzzles to conduct an experiment on self-reported “perfectionists”, determining whether those who call themselves perfectionists react differently to difficult puzzles than those who do not.

To satisfy this experiment condition, the researchers seek the help of a programmer -- you. They want to generate puzzles of varying difficulty. They want to be able to easily verify that the answers provided for a puzzle are correct. And they want to be able to generate unsolvable puzzles that look like solvable ones.

The only requirement is that the puzzle generator and solver is written in Python, can be easily imported from a Python REPL , and can be used by someone who is a novice in Python (make function calls, create object instances, etc.) The code should also run quickly enough that it can be used in an interactive setting while the experiment subjects are in the room. No command-line interface or GUI is required.

The Anagram Puzzle

Through some brainstorming with the team, you come up with the idea for generating “anagram puzzles”. These are puzzles based on re-arranging character sequences into a valid English word. For example, the puzzle “dgo” has the solutions “dog” and “god”.

Write code that generates anagram strings of a given difficulty level, and code that can be used to verify or solve a given anagram string. What are some strategies for generating unsolvable puzzles that look like solvable puzzles?

The Python Program

Start out with the following import statements and code template:

from collections import defaultdict
from random import choice, shuffle

# Words file can be found here 
DICTIONARY = open("./sowpods.txt")

if __name__ == “__main__”:
print("Hello, anagram!")



#Rerequirements
    1. generate puzzles of varying difficulty (1 - 5)
        - optional param for difficulty
    2. generate unsolvable puzzles that look like solvable ones 
        - optional param for unsolvable puzzles
    3. verify answers
        - return True or False
    4. Easily imported, written as library, can be used by someone who is a novice in Python (make function calls, create object instances, etc.)
    5. Run quickly enough that it can be used in an interactive setting while the experiment subjects are in the room


#Implementation structure/approach
    1. Create buckets of difficulty from 1 -5
       - Get smallest and largest word
       - difference between largest and smallest and divide by 5
       - ex 10 sm 2 
          - 2-3, 4-5, 6-7, 8-9, 10
       - create dict of buckets (list)
     
    2. create anagram
       - Word jumbler

     2. Annagram checker
        - reused in the verification
        - used to filter words to construct list
        - use to help create Commonness/familiarity our unsolveable list
         
     3. Create unsovleables lists
        - create list of words that are not anagrams of each other
          - Get words from each difficulty list and min num of vowells to get a unsolvable, if not unsolvable move to next word
        - create for each difficulty levelCommonness/familiarity 

    4. Generate puzzles
       - if difficulty is given, use that bucket 
          - pull random from bucket
       - if unsolvable is given, use that bucket
          - pull random from bucket
       - if both are given, use that bucket
          - pull random from bucket