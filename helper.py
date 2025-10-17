import math
import random


def text_processing(filename, _alphabet):
    """
    Reads a text file, cleans and normalizes its content for encryption.
    - Converts all characters to lowercase.
    - Splits the text into words.
    - Removes any characters that are not present in the provided alphabet.
    - Replaces the Ukrainian letter 'ґ' with 'г'.
    - Returns the processed text as a continuous string without spaces.
    :param filename: Path to the text file to be processed.
    :param _alphabet: String containing the allowed characters (alphabet).
    :return: A cleaned and normalized string ready for encryption.
    """
    with open(filename, 'r', encoding='UTF-8') as text_file:
        text = text_file.read().lower()

    words = text.split()

    for index, word in enumerate(words):
        for symbol in word:
            if symbol == 'ґ':
                word = word.replace(symbol, 'г')
            elif symbol not in _alphabet:
                word = word.replace(symbol, '')

        words[index] = word

    return ''.join(words)


def symbol_count(_text):
    """
    Counts the frequency of each character in the given text.
    - Iterates over all characters in the text.
    - Counts how many times each character appears.
    - Returns the result as a sorted list of (character, count) pairs,
      ordered by frequency in descending order.
    :param _text: String containing the text to analyze.
    :return: List of tuples (symbol, count) sorted by count in descending order.
    """
    _symbol_count = {}

    for symbol in _text:
        if symbol in _symbol_count:
            _symbol_count[symbol] += 1
        else:
            _symbol_count[symbol] = 1

    sorted_symbol_count = sorted(_symbol_count.items(), key=lambda items: items[1], reverse=True)
    return sorted_symbol_count


def symbol_frequency(_symbol_counts):
    """
    Converts absolute character counts to relative frequencies.
    - Takes a list of (character, count) pairs (e.g., the output of symbol_count).
    - Calculates the total number of characters by summing all counts.
    - Divides each character's count by the total to get its relative frequency.
    - Returns a list of (character, frequency) pairs, where frequency is rounded
      to three decimal places. The order of symbols remains the same as in the input.

    :param _symbol_counts: List of tuples (symbol, count) representing the absolute
                           number of occurrences of each character.
    :return: List of tuples (symbol, frequency) where frequency is a float in [0,1],
             rounded to three decimal places.
    """
    total = sum(count for _, count in _symbol_counts) if _symbol_counts else 1
    freq = [(sym, round(count / total, 3)) for sym, count in _symbol_counts]
    return freq


def bigram_count_crossing(_text):
    """
    Counts the frequency of overlapping (crossing) bigrams in the given text.
    - A bigram is a pair of consecutive characters (e.g., "аб", "ба").
    - Overlapping means that each new bigram starts one character after the previous one
      (e.g., for "абвг" → "аб", "бв", "вг").
    - Returns the bigrams sorted by their frequency in descending order.
    :param _text: String to analyze for overlapping bigrams.
    :return: List of tuples (bigram, count) sorted by count in descending order.
    """

    bigrams_count = {}
    step = 1

    for symbol in _text:
        bigram = symbol + _text[step]
        if bigram in bigrams_count:
            bigrams_count[bigram] += 1
        else:
            bigrams_count[bigram] = 1
        if step != len(_text) - 1:
            step += 1

    sorted_bigrams_count = sorted(bigrams_count.items(), key=lambda key: key[1], reverse=True)
    return sorted_bigrams_count


def bigram_count_not_crossing(_text):
    """
    Counts the frequency of non-overlapping bigrams in the given text.
    - A bigram is a pair of consecutive characters (e.g., "аб", "ба").
    - Non-overlapping means that each new bigram starts after the previous two characters
      (e.g., for "абвг" → "аб", "вг").
    - If the text length is odd, the last single character is ignored.
    - Returns the bigrams sorted by their frequency in descending order.
    :param _text: String to analyze for non-overlapping bigrams.
    :return: List of tuples (bigram, count) sorted by count in descending order.
    """

    bigrams_count = {}
    step = 1

    if len(_text) % 2 == 0:
        end = None
    else:
        end = -1

    for symbol in _text[:end:2]:
        bigram = symbol + _text[step]
        if bigram in bigrams_count:
            bigrams_count[bigram] += 1
        else:
            bigrams_count[bigram] = 1
        step += 2

    sorted_bigrams_count = sorted(bigrams_count.items(), key=lambda key: key[1], reverse=True)
    return sorted_bigrams_count


def bigram_frequency(_bigram_counts):
    """
    Converts absolute bigram counts to relative frequencies.
    - Takes a list of (bigram, count) pairs (e.g., the output of your bigram counting).
    - Calculates the total number of bigrams by summing all counts.
    - Divides each bigram's count by the total to get its relative frequency.
    - Returns a list of (bigram, frequency) pairs, where frequency is rounded
      to three decimal places. The order of bigrams remains the same as in the input.

    :param _bigram_counts: List of tuples (bigram, count) representing the absolute
                           number of occurrences of each bigram.
    :return: List of tuples (bigram, frequency) where frequency is a float in [0,1],
             rounded to three decimal places.
    """
    total = sum(count for _, count in _bigram_counts) if _bigram_counts else 1
    freq = [(bg, round(count / total, 3)) for bg, count in _bigram_counts]
    return freq


def create_matrix(symbols, bigram):
    """
    Builds a (n+1) x (n+1) frequency matrix for bigrams with labeled header rows/columns.
    - `symbols` is sorted and used to form the matrix headers (first row/column).
    - `bigram` is converted to a dict for O(1) lookup by bigram string.
    - Cells [i][j] (i>0, j>0) contain the frequency of the bigram formed by
      row header + column header if present; otherwise 0.
    - After filling numeric values, header labels are wrapped in single quotes.
    :param symbols: Iterable of items where the first element is a character
                    (e.g., list of tuples like [('а', 123), ('б', 98), ...]).
    :param bigram: Iterable of (bigram_str, count) pairs
                   (e.g., [('аб', 10), ('ба', 7), ...]).
    :return: 2D list representing the labeled frequency matrix.
             matrix[0][0] == '' (top-left corner),
             matrix[0][j] and matrix[i][0] contain quoted single-character headers.
    """

    dict_of_bigram = {key: value for key, value in bigram}
    symbols = sorted(symbols)

    n = len(symbols) + 1
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    matrix[0][0] = ''
    for i in range(1, n):
        matrix[0][i] = symbols[i-1][0]
        matrix[i][0] = symbols[i-1][0]

    for i in range(1, n):
        for j in range(1, n):
            if f"{matrix[i][0]}{matrix[0][j]}" in dict_of_bigram:
                matrix[i][j] = dict_of_bigram[f"{matrix[i][0]}{matrix[0][j]}"]

    for i in range(1, n):
        matrix[0][i] = f"'{symbols[i-1][0]}'"
        matrix[i][0] = f"'{symbols[i-1][0]}'"

    return matrix


def entropy_calculate(sequence):
    """
    Calculates the Shannon entropy of a sequence of symbols.

    - Accepts a list of (symbol, frequency) pairs.
    - Converts frequencies into probabilities and applies the Shannon entropy formula:
        H = -Σ(p * log2(p))
    - If the symbols are bigrams (length 2), the result is divided by 2
      to normalize per character.

    :param sequence: List of tuples [(symbol, frequency), ...].
                     Example: [('a', 10), ('b', 5), ...] or [('ab', 7), ('ba', 3), ...].
    :return: Shannon's entropy value (float).
    """
    n = len(sequence[0][0])

    sequence_count = 0
    for symbol in sequence:
        sequence_count += symbol[1]

    probability_H = []
    for symbol in sequence:
        freq = symbol[1]
        probability = freq / sequence_count
        probability_H.append(probability)

    H = 0
    for freq in probability_H:
        H -= freq * math.log2(freq)

    if n == 2:
        H = H / 2

    return H


def index_of_coincidence(_text, _alphabet):
    """
    Calculates the Index of Coincidence (IC) for a given text.

    - IC measures the probability that two randomly chosen letters
      from the text are the same.
    - Formula: IC = Σ f_i (f_i - 1) / [N (N - 1)],
      where f_i is the frequency of symbol i and N is the total length of the text.

    :param _text: Text string to analyze.
    :param _alphabet: String containing all possible symbols to count.
    :return: Index of Coincidence value (float).
    """
    len_message = len(_text)

    sum = 0
    for symbol in _alphabet:
        frequency = _text.count(symbol)
        sum += frequency * (frequency - 1)

    index = sum / (len_message * (len_message - 1))

    return index


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


def result_output(result):
    """
    Prints key–value pairs line by line in the format:
    '<key>': <value>
    :param result: Iterable of (key, value) items to print.
    :return: None
    """

    for key, value in result:
        print(f"'{key}': {value}")


def result_output_matrix(matrix, writefile):
    """
    Writes a 2D matrix to a text file, one row per line.
    Cells are right-aligned to width 6 and separated by the '|' character.
    :param matrix: 2D list (rows of items) to be written.
    :param writefile: Path to the output text file.
    :return: None
    """

    matrix_filewrite = open(writefile, 'w', encoding='UTF-8')
    for row in matrix:
        result_row = '|'.join([str(item).rjust(6) for item in row])
        matrix_filewrite.write(result_row + '\n')


def make_clean_texts_by_L(full_text, lengths, overlap=0.5, max_samples_per_L=1000):
    clean_texts_by_L = {}

    for L in lengths:
        step = int(L * (1 - overlap)) or 1
        samples = []

        for i in range(0, len(full_text) - L, step):
            fragment = full_text[i:i + L]
            if len(fragment.strip()) == L:
                samples.append(fragment)
            if len(samples) >= max_samples_per_L:
                break

        clean_texts_by_L[L] = samples

    return clean_texts_by_L


def compute_kH_dynamic(clean_texts_by_L, bigrams=False, alpha=0.05):
    result_H = {}
    result_kH = {}

    count_mode = bigram_count_crossing if bigrams else symbol_count

    for L, samples in clean_texts_by_L.items():
        H_values = []
        for sample in samples:
            H_values.append(entropy_calculate(count_mode(sample)))

        H_mean = sum(H_values) / len(H_values)
        deltas = [abs(H - H_mean) for H in H_values]
        deltas.sort()
        idx = int((1 - alpha) * (len(deltas) - 1))
        kH = deltas[idx]

        result_H[L] = H_mean
        result_kH[L] = kH

    return result_H, result_kH
