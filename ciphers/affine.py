from helper import euclidean_algorithm_extended as eae


def encrypt(_alphabet, _text, a, b):
    """
    Affine cipher encryption.
    Formula: E(x) = (a * x + b) mod m
    :param _alphabet: Alphabet (string or list of characters)
    :param _text: Plaintext to encrypt (characters must be in _alphabet)
    :param a: Multiplicative key 'a' (must be coprime with the alphabet size m)
    :param b: Additive key 'b' (an integer in [0, m-1])
    :return: Encrypted text (ciphertext)
    """

    m = len(_alphabet)
    if eae(a, m)[0] != 1:
        raise ValueError(f"'a'={a} must be coprime with the alphabet length m={m}")
    result = ''
    for ch in _text:
        x = _alphabet.index(ch)
        y = (a * x + b) % m
        result += _alphabet[y]
    return result
