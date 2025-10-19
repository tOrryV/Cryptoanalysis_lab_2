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


def generate_multiple_random_texts(_alphabet, plaintexts_by_len):
    """
    Generate random ciphertext–plaintext pairs for each text length using generate_random_text.

    :param _alphabet: list
        Alphabet used for generating ciphertexts.
    :param plaintexts_by_len: dict[int, list[str]]
        Mapping {text_length: [plaintext1, plaintext2, ...]} — plaintexts grouped by length.
    :return: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]}.
    """

    results = {}
    for text_len, plaintexts in plaintexts_by_len.items():
        pairs = []
        for p in plaintexts:
            c = generate_random_text(_alphabet, text_len)
            pairs.append({"plaintext": p, "ciphertext": c})
        results[text_len] = pairs
    return results


def generate_multiple_recurse_texts(_alphabet, plaintexts_by_len):
    """
    Generate recursive ciphertext–plaintext pairs for each text length using generate_recurse_text.

    :param _alphabet: list
        Alphabet used for generating ciphertexts.
    :param plaintexts_by_len: dict[int, list[str]]
        Mapping {text_length: [plaintext1, plaintext2, ...]} — plaintexts grouped by length.
    :return: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]}.
    """

    results = {}
    for text_len, plaintexts in plaintexts_by_len.items():
        pairs = []
        for p in plaintexts:
            c = generate_recurse_text(_alphabet, text_len)
            pairs.append({"plaintext": p, "ciphertext": c})
        results[text_len] = pairs
    return results


def encrypt_texts_by_vigenere(texts_by_length, alphabet, vigenere_keys_len):
    """
    Encrypt pre-generated texts with the Vigenere cipher for multiple key lengths,
    returning an easy-to-index nested mapping: result[length][key_len] -> list[...].

    :param texts_by_length: dict[int, list[str]]
        Mapping {text_length: [plaintext1, plaintext2, ...]} produced by generate_multiple_texts.
    :param alphabet: list
        Alphabet used by the Vigenere cipher.
    :param vigenere_keys_len: Iterable[int] | None
        Key lengths to use.
    :return: dict[int, dict[int, list]]
        result[length][key_len] -> list of ciphertexts (or dicts if include_meta=True).
    """

    result = {}
    for length, texts in texts_by_length.items():
        result[length] = {}
        bucket = []
        for plaintext in texts:
            key = generate_random_text(alphabet, vigenere_keys_len)
            ciphertext = v.encrypt(alphabet, plaintext, key)
            bucket.append({
                "plaintext": plaintext,
                "ciphertext": ciphertext
            })
        result[length] = bucket
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


def generate_of_non_coherent_text(len_text):
    """
    Generate a non-coherent text consisting of a single repeated character ('а').

    :param len_text: int
        Desired length of the generated text.
    :return: str
        String of length `len_text` composed entirely of the character 'а'.
    """

    return 'а' * len_text
