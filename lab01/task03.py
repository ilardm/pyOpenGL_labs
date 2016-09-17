# -*- coding: utf-8 -*-

import sys


def bubble(seq):
    # https://ru.wikipedia.org/wiki/%D0%A1%D0%BE%D1%80%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0_%D0%BF%D1%83%D0%B7%D1%8B%D1%80%D1%8C%D0%BA%D0%BE%D0%BC

    if len(seq) <= 1:
        return seq

    have_changes = True
    while have_changes:
        have_changes = False

        for i in range(len(seq)-1):
            if seq[i] > seq[i+1]:
                tmp = seq[i+1]
                seq[i+1] = seq[i]
                seq[i] = tmp
                have_changes = True

    return seq


def try_convert(n):
    try:
        return int(n)
    except ValueError:
        return None


def main(argv):
    assert(len(argv) > 1)

    seq = argv[1:]
    seq = [try_convert(n) for n in seq]
    seq = [n for n in seq if n is not None]
    
    seq = bubble(seq)
    print('sorted:', seq)
    

if __name__ == '__main__':
    main(sys.argv)
