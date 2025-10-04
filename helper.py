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

