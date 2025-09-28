import math


def text_processing(filename, _alphabet):
    with open(filename, 'r', encoding='UTF-8') as text_file:
        text = text_file.read().lower()

    words = text.split()

    for index, word in enumerate(words):
        for symbol in word:
            if symbol not in _alphabet:
                word = word.replace(symbol, '')
            elif symbol == 'ґ':
                word = word.replace(symbol, 'г')

        words[index] = word

    return ''.join(words)


def symbols_count(_text):
    symbol_count = {}

    for symbol in _text:
        if symbol in symbol_count:
            symbol_count[symbol] += 1
        else:
            symbol_count[symbol] = 1

    sorted_symbol_count = sorted(symbol_count.items(), key=lambda items: items[1], reverse=True)
    return sorted_symbol_count


def bigrams_count_crossing(_text):
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


def bigrams_count_not_crossing(_text):
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


def create_matrix(symbols, bigram):
    dict_of_bigram = {key: value for key, value in bigram}
    symbols = sorted(symbols)

    n = len(symbols)+1
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    matrix[0][0] = ''
    for i in range(1, n):
        matrix[0][i] = symbols[i-1][0]
        matrix[i][0] = symbols[i-1][0]
    #
    for i in range(1, n):
        for j in range(1, n):
            if f"{matrix[i][0]}{matrix[0][j]}" in dict_of_bigram:
                matrix[i][j] = dict_of_bigram[f"{matrix[i][0]}{matrix[0][j]}"]

    for i in range(1, n):
        matrix[0][i] = f"'{symbols[i-1][0]}'"
        matrix[i][0] = f"'{symbols[i-1][0]}'"

    return matrix


def result_output(result):
    for key, value in result:
        print(f"'{key}': {value}")


def result_output_matrix(matrix, writefile):
    matrix_filewrite = open(writefile, 'w', encoding='UTF-8')
    for row in matrix:
        result_row = '|'.join([str(item).rjust(5) for item in row])
        matrix_filewrite.write(result_row + '\n')


def entropy_calculate(sequence):
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
    len_message = len(_text)

    sum = 0
    for symbol in _alphabet:
        frequency = _text.count(symbol)
        sum += frequency * (frequency - 1)

    index = sum / (len_message * (len_message - 1))

    return index


def main():
    alphabet = [
        'а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м',
        'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я',
    ]

    cleaned_data = text_processing('data/data.txt', alphabet)
    symbols_frequency = symbols_count(cleaned_data)
    result_output(symbols_frequency)

    bigrams_count_crossing_var = bigrams_count_crossing(cleaned_data)
    bigrams_count_not_crossing_var = bigrams_count_not_crossing(cleaned_data)

    res_matrix_crossing = create_matrix(symbols_frequency, bigrams_count_crossing_var)
    res_matrix_not_crossing = create_matrix(symbols_frequency, bigrams_count_not_crossing_var)

    result_output_matrix(res_matrix_crossing, 'results/bigrams_crossing.txt')
    result_output_matrix(res_matrix_not_crossing, 'results/bigrams_not_crossing.txt')

    entropyH1 = entropy_calculate(symbols_frequency)
    entropyH2_cross = entropy_calculate(bigrams_count_crossing_var)
    entropyH2_not_cross = entropy_calculate(bigrams_count_not_crossing_var)

    print(f'\nH1: {entropyH1}\nH2 crossing: {entropyH2_cross}\nH2 not crossing: {entropyH2_not_cross}')
    print(f'Index of coincidence for cleaned text = {index_of_coincidence(cleaned_data, alphabet)}')


if __name__ == '__main__':
    main()
