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
