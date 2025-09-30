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
    if euclidean_algorithm_extended(a, m)[0] != 1:
        raise ValueError(f"'a'={a} must be coprime with the alphabet length m={m}")
    result = ''
    for ch in _text:
        x = _alphabet.index(ch)
        y = (a * x + b) % m
        result += _alphabet[y]
    return result


def decrypt(_alphabet, _text, a, b):
    """
    Affine cipher decryption.
    Formula: D(y) = a_inv * (y - b) mod m
    :param _alphabet: Alphabet (string or list of characters)
    :param _text: Ciphertext to decrypt (characters must be in _alphabet)
    :param a: Multiplicative key 'a' (must be coprime with the alphabet size m)
    :param b: Additive key 'b' (an integer in [0, m-1])
    :return: Decrypted text (plaintext)
    """

    m = len(_alphabet)
    if euclidean_algorithm_extended(a, m)[0] != 1:
        raise ValueError(f"'a'={a} must be coprime with the alphabet length m={m}")
    a_inv = euclidean_algorithm_extended(a, m)[1] % m

    result = ''
    for ch in _text:
        y = _alphabet.index(ch)
        x = (a_inv * (y - b)) % m
        result += _alphabet[x]
    return result


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
