import random
from ciphers import affine as aff
from ciphers import affine_bigram as affb
from ciphers import vigenere as v
from helper import _random_affine_keys


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

    rand = random.SystemRandom()
    res = rand.choice(_alphabet) + rand.choice(_alphabet)

    for _ in range(text_len - 2):
        idx = (_alphabet.index(res[-1]) + _alphabet.index(res[-2])) % len(_alphabet)
        res += _alphabet[idx]

    return res


def encrypt_texts_by_vigenere(texts_by_length, alphabet, vigenere_keys_len=None):
    """
    Encrypt pre-generated texts with the Vigenère cipher for multiple key lengths,
    returning an easy-to-index nested mapping: result[length][key_len] -> list[...].

    :param texts_by_length: dict[int, list[str]]
        Mapping {text_length: [plaintext1, plaintext2, ...]} produced by generate_multiple_texts.
    :param alphabet: list
        Alphabet used by the Vigenère cipher.
    :param vigenere_keys_len: Iterable[int] | None
        Key lengths to use. Defaults to [1, 5, 10].
    :return: dict[int, dict[int, list]]
        result[length][key_len] -> list of ciphertexts (or dicts if include_meta=True).
    """
    if vigenere_keys_len is None:
        vigenere_keys_len = [1, 5, 10]

    result = {}
    for length, texts in texts_by_length.items():
        result[length] = {}
        for key_len in vigenere_keys_len:
            bucket = []
            for plaintext in texts:
                key = generate_random_text(alphabet, key_len)
                ciphertext = v.encrypt(alphabet, plaintext, key)
                bucket.append({
                    "plaintext": plaintext,
                    "ciphertext": ciphertext
                })
            result[length][key_len] = bucket
    return result


def encrypt_texts_by_affine(texts_by_length, alphabet):
    """
    Encrypt pre-generated texts with the (monoalphabetic) affine cipher
    E(x) = (a*x + b) mod m, returning an easy-to-index mapping:
    result[length] -> list[...].

    :param texts_by_length: dict[int, list[str]]
        Mapping {text_length: [plaintext1, plaintext2, ...]} from generate_multiple_texts.
    :param alphabet: list
        Alphabet used by the affine cipher; all characters must be unique.
    :return: dict[int, list]
        result[length] -> list of ciphertexts (or dicts if include_meta=True).
    """

    m = len(alphabet)
    result = {}

    for length, texts in texts_by_length.items():
        bucket = []
        for plaintext in texts:
            a, b = _random_affine_keys(m)
            ciphertext = aff.encrypt(alphabet, plaintext, a, b)
            bucket.append({
                "plaintext": plaintext,
                "ciphertext": ciphertext
            })
        result[length] = bucket

    return result


def encrypt_texts_by_affine_bigram(texts_by_length, alphabet, crossing=True, pad_char=None):
    """
    Encrypt pre-generated texts with the affine bigram cipher over alphabet of size m.
    Bigram encoding: X = x1*m + x2, Y = (a*X + b) mod m^2, then decode Y -> (y1, y2).

    Easy-to-index mapping: result[length] -> list[...].

    :param texts_by_length: dict[int, list[str]]
        Mapping {text_length: [plaintext1, plaintext2, ...]} from generate_multiple_texts.
    :param alphabet: list
        Alphabet; all characters must be unique.
    :param crossing: bool
        If True, use overlapping bigrams; if False, non-overlapping pairs.
    :param pad_char: str | None
        Padding character (must belong to `alphabet`) used when crossing=False and len(text) is odd.
    :return: dict[int, list]
        result[length] -> list of ciphertexts (or dicts if include_meta=True).
    """
    m = len(alphabet)
    result = {}

    for length, texts in texts_by_length.items():
        bucket = []
        for plaintext in texts:
            a, b = _random_affine_keys(m, True)
            ciphertext = affb.encrypt(alphabet, plaintext, a, b, crossing=crossing, pad_char=pad_char)
            bucket.append({
                "plaintext": plaintext,
                "ciphertext": ciphertext
            })
        result[length] = bucket

    return result

