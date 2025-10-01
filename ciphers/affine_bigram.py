def encrypt(_alphabet, _text, a, b, crossing=False, pad_char=None):
    """
    Affine bigram cipher encryption without precomputing all bigrams.

    Mapping:
      For an alphabet of size m, a bigram (x1, x2) is encoded as X = x1*m + x2 (0..m^2-1).
      Encryption: Y = (a*X + b) mod m^2.
      Decoding back to chars: y1, y2 = divmod(Y, m).

    :param _alphabet: Alphabet as a string; each character must be unique.
    :param _text: Plaintext composed only of characters from _alphabet.
    :param a: Multiplicative key; must be coprime with m^2 (gcd(a, m^2) == 1).
    :param b: Additive key, 0 <= b < m^2 (it will be reduced modulo m^2 anyway).
    :param crossing: If True, use overlapping bigrams (c1c2, c2c3, ...).
                     If False (default), use non-overlapping pairs (c1c2, c3c4, ...).
    :param pad_char: Optional padding character (must belong to _alphabet). Used only when
                     crossing=False and len(_text) is odd. If None, defaults to _alphabet[0].
    :return: Ciphertext string.
    """
    m = len(_alphabet)
    nmod = m * m

    if euclidean_algorithm_extended(a, nmod)[0] != 1:
        raise ValueError(f"'a'={a} must be coprime with m^2={nmod}")

    idx = {ch: i for i, ch in enumerate(_alphabet)}

    if not crossing:
        if len(_text) % 2 == 1:
            pad_char = _alphabet[0] if pad_char is None else pad_char
            if pad_char not in idx:
                raise ValueError("pad_char must be a character from _alphabet")
            _text = _text + pad_char

        it = ((i, i + 1) for i in range(0, len(_text), 2))
    else:
        if len(_text) < 2:
            return ""
        it = ((i, i + 1) for i in range(0, len(_text) - 1))

    res = []
    for i, j in it:
        c1, c2 = _text[i], _text[j]
        try:
            x1, x2 = idx[c1], idx[c2]
        except KeyError as e:
            raise ValueError(f"Character {e.args[0]!r} not in alphabet") from None

        X = x1 * m + x2
        Y = (a * X + b) % nmod
        y1, y2 = divmod(Y, m)
        res.append(_alphabet[y1] + _alphabet[y2])

    return "".join(res)


def affine_bigram_decrypt(_alphabet, _text, a, b, crossing=False):
    """
    Affine bigram cipher decryption without precomputing all bigrams.

    Mapping:
      For an alphabet of size m, bigram (y1, y2) -> Y = y1*m + y2.
      Decryption: X = a_inv * (Y - b) mod m^2, where a_inv = a^{-1} mod m^2.
      Decoding back to chars: x1, x2 = divmod(X, m).

    :param _alphabet: Alphabet as a string; each character must be unique.
    :param _text: Ciphertext composed only of characters from _alphabet.
    :param a: Multiplicative key; must be coprime with m^2 (gcd(a, m^2) == 1).
    :param b: Additive key, interpreted modulo m^2.
    :param crossing: Set True if the encryption used overlapping bigrams; otherwise False.
    :return: Decrypted text string (note: for non-overlapping mode and even-length input,
             output length equals input length; for crossing, output has length len(text)).
    """
    m = len(_alphabet)
    nmod = m * m

    if euclidean_algorithm_extended(a, nmod)[0] != 1:
        raise ValueError(f"'a'={a} must be coprime with m^2={nmod}")

    a_inv = euclidean_algorithm_extended(a, nmod)[1] % nmod
    idx = {ch: i for i, ch in enumerate(_alphabet)}

    if not crossing:
        if len(_text) % 2 != 0:
            raise ValueError("Ciphertext length must be even in non-overlapping mode")
        it = ((i, i + 1) for i in range(0, len(_text), 2))
    else:
        if len(_text) < 2:
            return ""
        it = ((i, i + 1) for i in range(0, len(_text) - 1))

    res = []
    for i, j in it:
        c1, c2 = _text[i], _text[j]
        try:
            y1, y2 = idx[c1], idx[c2]
        except KeyError as e:
            raise ValueError(f"Character {e.args[0]!r} not in alphabet") from None

        Y = y1 * m + y2
        X = (a_inv * ((Y - b) % nmod)) % nmod
        x1, x2 = divmod(X, m)
        res.append(_alphabet[x1] + _alphabet[x2])

    return "".join(res)


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
