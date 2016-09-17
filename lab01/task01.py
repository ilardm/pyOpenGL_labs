#-*- coding: utf-8

import sys


FIRST_PRIME = 2


def get_primes(n):
    # https://ru.wikipedia.org/wiki/%D0%A0%D0%B5%D1%88%D0%B5%D1%82%D0%BE_%D0%AD%D1%80%D0%B0%D1%82%D0%BE%D1%81%D1%84%D0%B5%D0%BD%D0%B0#.D0.90.D0.BB.D0.B3.D0.BE.D1.80.D0.B8.D1.82.D0.BC

    assert(n >= FIRST_PRIME)

    if n == FIRST_PRIME:
        return [FIRST_PRIME]

    sieve = list(range(FIRST_PRIME, n+1))

    p = FIRST_PRIME

    while True:
        for i in range(2*p, n+1, p):
            try:
                sieve.remove(i)
            except ValueError:
                # already removed or does not exist
                pass

        found = False
        for i in sieve:
            if i > p:
                p = i
                found = True
                break

        if not found:
            break

    return sieve


def main(argv):
    assert(len(argv) > 1)

    n = int(argv[1])

    primes = get_primes(n)
    print('primes:', primes)
    

if __name__ == '__main__':
    main(sys.argv)
