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


def _random_affine_keys(m, bigram=False):
    """
    Generate random valid keys (a, b) for the affine cipher.

    If `bigram` is False → generate keys for the classic affine cipher with modulus M = m.
    If `bigram` is True  → generate keys for the affine bigram cipher with modulus M = m^2.

    :param m: Size of the alphabet (integer).
    :param bigram: Boolean flag — if True, keys are generated for the bigram affine cipher (mod m^2);
                   if False, keys are generated for the standard affine cipher (mod m).
    :return: Tuple (a, b) where:
             - a (int) — multiplicative key coprime with M
             - b (int) — additive key in the range [0, M-1]
    """

    M = m ** 2 if bigram else m
    rnd = random.SystemRandom()

    while True:
        a = rnd.randrange(1, M)
        if euclidean_algorithm_extended(a, M)[0] == 1:
            break

    b = rnd.randrange(0, M)
    return a, b
