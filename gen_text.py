import random
from ciphers import affine as aff
from ciphers import affine_bigram as affb
from ciphers import vigenere as v
from helper import generate_rand_text_from_cleaned_data, _random_affine_keys


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


def generate_text_by_vigenere(ukr_data, _alphabet, text_len, key_len):
    """
    Generate a random Ukrainian text fragment from the cleaned corpus and encrypt it with the Vigenère cipher.

    :param ukr_data: Preprocessed Ukrainian text corpus (string)
    :param _alphabet: Alphabet used for encryption/decryption
    :param text_len: Length of the text to generate
    :param key_len: Length of the random key for Vigenère encryption
    :return: Encrypted text using the Vigenère cipher
    """

    text = generate_rand_text_from_cleaned_data(ukr_data, text_len)
    key = generate_random_text(_alphabet, key_len)

    return v.encrypt(_alphabet, text, key)


def generate_text_by_affine(ukr_data, _alphabet, text_len):
    """
    Generate a random Ukrainian plaintext fragment from `ukr_data`
    and encrypt it with the affine cipher E(x) = (a*x + b) mod m.

    :param ukr_data: Cleaned Ukrainian text corpus (string)
    :param _alphabet: Alphabet (sequence of characters) used by the cipher
    :param text_len: Length of plaintext to sample from `ukr_data`
    :return: Ciphertext (affine-encrypted)
    """

    a, b = _random_affine_keys(len(_alphabet))
    text = generate_rand_text_from_cleaned_data(ukr_data, text_len)

    return aff.encrypt(_alphabet, text, a, b)


def generate_text_by_affine_bigram(ukr_data, _alphabet, text_len, crossing, pad_char):
    """
    Generate a random plaintext fragment from `ukr_data` and encrypt it
    with the affine bigram cipher.

    Bigram mapping for alphabet size m:
       X = x1*m + x2     (X in [0, m^2 - 1])
       Y = (a*X + b) mod m^2
       (y1, y2) = divmod(Y, m)

    :param ukr_data: Cleaned Ukrainian text corpus (string)
    :param _alphabet: Alphabet as a string; each character must be unique
    :param text_len: Length of plaintext to sample from `ukr_data`
    :param crossing: If True — use overlapping bigrams; if False — non-overlapping pairs
    :param pad_char: Optional padding char from `_alphabet` when crossing=False and len(text) is odd
    :return: Ciphertext string (affine-bigram encrypted)
    """

    m = len(_alphabet)
    a, b = _random_affine_keys(m, True)
    text = generate_rand_text_from_cleaned_data(ukr_data, text_len)

    return affb.encrypt(_alphabet, text, a, b, crossing=crossing, pad_char=pad_char)
