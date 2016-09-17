# -*- coding: utf-8 -*-

import sys

INITIAL_SEQ = [1, 1]


def next_fib(seq):
    assert(len(seq) >= 2)

    return seq[-1] + seq[-2]


def fib(n):
    # https://ru.wikipedia.org/wiki/%D0%A7%D0%B8%D1%81%D0%BB%D0%B0_%D0%A4%D0%B8%D0%B1%D0%BE%D0%BD%D0%B0%D1%87%D1%87%D0%B8

    assert(n >= 1)

    seq = INITIAL_SEQ

    nf = next_fib(seq)
    while nf <= n:
        seq.append(nf)
        nf = next_fib(seq)

    return seq


def main(argv):
    assert(len(argv) > 1)

    n = int(argv[1])

    seq = fib(n)
    print('fib:', seq)
    

if __name__ == '__main__':
    main(sys.argv)
