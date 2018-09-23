#!/usr/bin/env python
'''
    Implements a simple 'more' output-modifier that can be used in a pipe.

    Example usage: ls | more.py
    
    When the page is full, use 'h' to see the options.
'''
import more_or_less
import sys


def main():
    more_or_less.paginate(input=sys.stdin)
    # Yes that's all that is required


if __name__ == "__main__":
    main()
