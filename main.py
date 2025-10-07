import math

from criteria import criteria_1_0, criteria_1_1, criteria_1_2, criteria_1_3
from gen_text import encrypt_texts_by_vigenere, encrypt_texts_by_affine, encrypt_texts_by_affine_bigram
from helper import generate_multiple_texts_by_cleaned_text, select_unigram_sets_from_counts, \
    select_bigram_sets_from_counts


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


def main():
    """
    To be continued...
    """

    alphabet = [
        'а', 'б', 'в', 'г', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м',
        'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я',
    ]

    filenames = ['chetverte-krylo.txt', 'it.txt', 'komanda.txt', 'monte.txt', 'orden.txt',
                 'rechi.txt', 'znedoleni.txt', 'polumya.txt']

    cleaned_data = ''
    for filename in filenames:
        cleaned_data += text_processing('data/' + filename, alphabet)

    symbols_count = symbol_count(cleaned_data)
    symbols_frequency = symbol_frequency(symbols_count)
    # result_output(symbols_frequency)

    bigrams_count_crossing_var = bigram_count_crossing(cleaned_data)
    bigrams_frequency = bigram_frequency(bigrams_count_crossing_var)
    # bigrams_count_not_crossing_var = bigram_count_not_crossing(cleaned_data)

    # res_matrix_crossing = create_matrix(symbols_frequency, bigrams_count_crossing_var)
    # res_matrix_not_crossing = create_matrix(symbols_frequency, bigrams_count_not_crossing_var)
    # result_output_matrix(res_matrix_crossing, 'results/bigrams_crossing.txt')
    # result_output_matrix(res_matrix_not_crossing, 'results/bigrams_not_crossing.txt')
    #
    # entropyH1 = entropy_calculate(symbols_frequency)
    # entropyH2_cross = entropy_calculate(bigrams_count_crossing_var)
    # entropyH2_not_cross = entropy_calculate(bigrams_count_not_crossing_var)
    #
    # print(f'H1: {entropyH1}\nH2 crossing: {entropyH2_cross}\nH2 not crossing: {entropyH2_not_cross}')
    # print(f'Index of coincidence for cleaned text: {index_of_coincidence(cleaned_data, alphabet)}')

    len_texts = [10, 100]
    count_texts = [10000, 1]
    generated_random_texts = generate_multiple_texts_by_cleaned_text(cleaned_data, len_texts, count_texts)
    # encrypted_texts_by_vigenere = encrypt_texts_by_vigenere(generated_random_texts, alphabet, 1)
    encrypted_texts_by_affine = encrypt_texts_by_affine(generated_random_texts, alphabet)
    # encrypted_texts_by_affine_bigram = encrypt_texts_by_affine_bigram(generated_random_texts, alphabet, False, alphabet[0])

    unigram_sets = select_unigram_sets_from_counts(symbols_count)
    forbidden_symbols = unigram_sets['forbidden']
    popular_symbols = unigram_sets['popular']

    bigram_sets = select_bigram_sets_from_counts(bigrams_count_crossing_var)
    forbidden_bigrams = bigram_sets['forbidden']
    popular_bigrams = bigram_sets['popular']

    criteria_1_0_var = criteria_1_0(encrypted_texts_by_affine, None, forbidden_bigrams)
    print(criteria_1_0_var)

    criteria_1_1_var = criteria_1_1(encrypted_texts_by_affine, 2, forbidden_symbols)
    print(criteria_1_1_var)

    criteria_1_2_var = criteria_1_2(encrypted_texts_by_affine, None, None,
                                    forbidden_bigrams, bigrams_frequency)
    print(criteria_1_2_var)

    criteria_1_3_var = criteria_1_3(encrypted_texts_by_affine, forbidden_symbols, symbols_frequency)
    print(criteria_1_3_var)


if __name__ == '__main__':
    main()
