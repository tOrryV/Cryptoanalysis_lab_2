import random


def generate_random_text(_alphabet, text_len):
    """
    Random text generator.
    Generates a string of specified length using a uniform distribution of characters.
    :param _alphabet: Alphabet (string or list of characters) to sample from
    :param text_len: Desired length of the generated text (positive integer)
    :return: Randomly generated text with uniform character distribution
    """

    return ''.join(random.choice(_alphabet) for _ in range(text_len))


def generate_recurse_text(_alphabet, text_len):
    """
    Generate recursive text where:
      s0, s1 — random,
      s_i = (s_{i-1} + s_{i-2}) mod len(alphabet)
    :param _alphabet: list or string of characters
    :param text_len: desired length (>=2)
    """
    if text_len <= 0:
        return ''

    rand = random.SystemRandom()
    res = rand.choice(_alphabet) + rand.choice(_alphabet)

    for _ in range(text_len - 2):
        idx = (_alphabet.index(res[-1]) + _alphabet.index(res[-2])) % len(_alphabet)
        res += _alphabet[idx]

    return res