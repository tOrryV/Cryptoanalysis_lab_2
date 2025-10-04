import random


def euclidean_algorithm_extended(a, b):
    """
    Extended Euclidean Algorithm.
    Returns a tuple (gcd, x, y) such that: a*x + b*y = gcd(a, b)
    :param a: First integer
    :param b: Second integer (modulus in our use case)
    :return: (gcd, x, y)
    """

    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = euclidean_algorithm_extended(b % a, a)
        return gcd, y - (b // a) * x, x


def generate_rand_text_from_cleaned_data(ukr_data, text_len):
    """
    Generate a random substring from a preprocessed Ukrainian text corpus.

    Selects a random starting index within the given string `ukr_data` and
    returns a substring of exactly `text_len` characters.

    :param ukr_data: Cleaned Ukrainian text corpus (string)
    :param text_len: Length of the desired random text fragment (positive integer)
    :return: Randomly selected substring of `ukr_data` with length `text_len`
    """

    start = random.SystemRandom().randrange(len(ukr_data) - text_len + 1)
    return ukr_data[start:start + text_len]


def _random_affine_keys(m):
    """
    Generate random valid keys (a, b) for the affine cipher with modulus m.

    The affine cipher uses the encryption function:
        E(x) = (a * x + b) mod m
    where:
        - a must be coprime with m (gcd(a, m) = 1)
        - b can be any integer in the range [0, m-1]

    :param m: Size of the alphabet (modulus). Must be a positive integer.
    :return: A tuple (a, b) where:
             - a is a randomly chosen integer such that gcd(a, m) = 1
             - b is a randomly chosen integer in [0, m-1]
    """

    rnd = random.SystemRandom()
    while True:
        a = rnd.randrange(1, m)
        if euclidean_algorithm_extended(a, m)[0] == 1:
            break
    b = rnd.randrange(0, m)

    return a, b
