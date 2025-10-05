import random
# from gen_text import generate_random_text


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


def generate_multiple_texts_by_cleaned_text(ukr_data, len_texts, count_texts):
    """
    Generate a large number of random text fragments of different lengths
    from a preprocessed Ukrainian text corpus.

    For each specified text length in `len_texts`, this function generates
    the corresponding number of random substrings defined in `count_texts`.
    Each substring is created by randomly selecting a starting position
    within the given `ukr_data` and taking `text_len` characters.

    :param ukr_data: (str) — The cleaned Ukrainian text corpus used as the source for generation.
    :param len_texts: (list[int]) — A list of text lengths to generate.
    :param count_texts: (list[int]) — A list of counts specifying how many texts to generate for each length.
                          Must have the same length as `len_texts`.
    :return: dict — A dictionary where each key is a text length (int)
                   and the corresponding value is a list of generated random text fragments (list[str]).
    """

    results = {}
    for text_len, count in zip(len_texts, count_texts):
        texts = [
            generate_rand_text_from_cleaned_data(ukr_data, text_len)
            for _ in range(count)
        ]
        results[text_len] = texts

    return results


# def generate_multiple_texts_from_alphabet(_alphabet, len_texts, count_texts):
#     """
#     Generate a large number of random text fragments of different lengths
#     from a preprocessed Ukrainian text corpus.
#
#     For each specified text length in `len_texts`, this function generates
#     the corresponding number of random substrings defined in `count_texts`.
#     Each substring is created by randomly selecting a starting position
#     within the given `ukr_data` and taking `text_len` characters.
#
#     :param _alphabet: list - Alphabet; all characters must be unique.
#     :param len_texts: (list[int]) — A list of text lengths to generate.
#     :param count_texts: (list[int]) — A list of counts specifying how many texts to generate for each length.
#                           Must have the same length as `len_texts`.
#     :return: dict — A dictionary where each key is a text length (int)
#                    and the corresponding value is a list of generated random text fragments (list[str]).
#     """
#
#     results = {}
#     for text_len, count in zip(len_texts, count_texts):
#         texts = [
#             generate_random_text(_alphabet, text_len)
#             for _ in range(count)
#         ]
#         results[text_len] = texts
#
#     return results


def select_unigram_sets_from_counts(counts, forbid_mass=0.05, popular_coverage=0.80):
    """
    Use precomputed symbol counts to select:
      - forbidden symbols: least-frequent symbols whose cumulative probability <= forbid_mass
      - popular symbols: most-frequent symbols whose cumulative probability >= popular_coverage

    :param counts: can be:
        - list[tuple[str,int]] like the output of symbols_count(text) (may be sorted or not)
        - dict[str,int] mapping symbol -> count
    :param forbid_mass: float in [0,1]
    :param popular_coverage: float in (0,1]
    :return: dict with keys:
             "forbidden": list[str], "popular": list[str]
    """

    if isinstance(counts, dict):
        items = list(counts.items())
    else:
        items = list(counts)

    items_desc = sorted(items, key=lambda kv: kv[1], reverse=True)
    total = sum(c for _, c in items_desc) or 1

    items_asc = list(reversed(items_desc))
    cum = 0.0
    forbidden = []
    for sym, cnt in items_asc:
        p = cnt / total
        if cum + p <= forbid_mass + 1e-12:
            forbidden.append(sym)
            cum += p
        else:
            break

    cum = 0.0
    popular = []
    for sym, cnt in items_desc:
        popular.append(sym)
        cum += cnt / total
        if cum >= popular_coverage - 1e-12:
            break

    res = {"forbidden": forbidden, "popular": popular}

    return res


def select_bigram_sets_from_counts(counts, forbid_mass=0.0025, popular_coverage=0.80):
    """
    Use precomputed bigram counts to select:
      - forbidden bigrams: least-frequent bigrams whose cumulative probability <= forbid_mass
      - popular bigrams: most-frequent bigrams whose cumulative probability >= popular_coverage

    :param counts: can be::
        - list[tuple[str,int]] like the bigrams_count_* (may be sorted or not)
        - dict[str,int] bigram -> count
    :param forbid_mass: float у [0,1]
    :param popular_coverage: float у (0,1]
    :return: dict with keys:
             "forbidden": list[str], "popular": list[str]
    """
    if isinstance(counts, dict):
        items = list(counts.items())
    else:
        items = list(counts)

    items_desc = sorted(items, key=lambda kv: kv[1], reverse=True)
    total = sum(c for _, c in items_desc) or 1

    items_asc = list(reversed(items_desc))
    cum = 0.0
    forbidden = []
    for bg, cnt in items_asc:
        p = cnt / total
        if cum + p <= forbid_mass + 1e-12:
            forbidden.append(bg)
            cum += p
        else:
            break

    cum = 0.0
    popular = []
    for bg, cnt in items_desc:
        popular.append(bg)
        cum += cnt / total
        if cum >= popular_coverage - 1e-12:
            break

    res = {"forbidden": forbidden, "popular": popular}

    return res
