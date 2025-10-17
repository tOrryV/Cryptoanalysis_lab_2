import criteria as c
import gen_text as gt
import helper as h
from error_rates import calc_error_rates_from_criteria


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
        cleaned_data += h.text_processing('data/' + filename, alphabet)

    symbols_count = h.symbol_count(cleaned_data)
    symbols_frequency = h.symbol_frequency(symbols_count)
    # h.result_output(symbols_frequency)

    bigrams_count_crossing_var = h.bigram_count_crossing(cleaned_data)
    bigrams_frequency = h.bigram_frequency(bigrams_count_crossing_var)

    # bigrams_count_not_crossing_var = h.bigram_count_not_crossing(cleaned_data)

    # res_matrix_crossing = h.create_matrix(symbols_frequency, bigrams_count_crossing_var)
    # res_matrix_not_crossing = h.create_matrix(symbols_frequency, bigrams_count_not_crossing_var)
    # h.result_output_matrix(res_matrix_crossing, 'results/bigrams_crossing.txt')
    # h.result_output_matrix(res_matrix_not_crossing, 'results/bigrams_not_crossing.txt')

    entropyH1 = h.entropy_calculate(symbols_count)
    entropyH2_cross = h.entropy_calculate(bigrams_count_crossing_var)
    # entropyH2_not_cross = h.entropy_calculate(bigrams_count_not_crossing_var)
    index_of_coincidence = h.index_of_coincidence(cleaned_data, alphabet)

    # print(f'H1: {entropyH1}\nH2 crossing: {entropyH2_cross}\nH2 not crossing: {entropyH2_not_cross}')
    # print(f'Index of coincidence for cleaned text: {index_of_coincidence}')

    len_texts = [10, 100, 1000, 10000]
    count_texts = [10000, 10000, 10000, 1000]
    generated_random_texts = h.generate_multiple_texts_by_cleaned_text(cleaned_data, len_texts, count_texts)
    # encrypted_texts_by_vigenere = gt.encrypt_texts_by_vigenere(generated_random_texts, alphabet, 1)
    encrypted_texts_by_affine = gt.encrypt_texts_by_affine(generated_random_texts, alphabet)
    # encrypted_texts_by_affine_bigram = gt.encrypt_texts_by_affine_bigram(generated_random_texts, alphabet, False, alphabet[0])

    unigram_sets = h.select_unigram_sets_from_counts(symbols_count)
    forbidden_symbols = unigram_sets['forbidden']
    popular_symbols = unigram_sets['popular']


    bigram_sets = h.select_bigram_sets_from_counts(bigrams_count_crossing_var)
    forbidden_bigrams = bigram_sets['forbidden']
    popular_bigrams = bigram_sets['popular']

    # criteria_1_0_var = c.criteria_1_0(encrypted_texts_by_affine, None, forbidden_bigrams)
    # print(criteria_1_0_var)

    criteria_1_1_var = c.criteria_1_1(encrypted_texts_by_affine, 2, forbidden_symbols)
    # print(criteria_1_1_var)

    # criteria_1_2_var = c.criteria_1_2(encrypted_texts_by_affine, None, None,
    #                                   forbidden_bigrams, bigrams_frequency)
    # print(criteria_1_2_var)

    # criteria_1_3_var = c.criteria_1_3(encrypted_texts_by_affine, forbidden_symbols, symbols_frequency)
    # print(criteria_1_3_var)

    # clean_texts_by_L = h.make_clean_texts_by_L(cleaned_data, len_texts)
    # H_dynamic, kH_dynamic = h.compute_kH_dynamic(clean_texts_by_L)
    # criteria_3_0_var = c.criteria_3_0(encrypted_texts_by_affine_bigram, H_dynamic, kH_dynamic)
    # print(criteria_3_0_var)

    # criteria_5_1_var = c.criteria_5_1(encrypted_texts_by_affine_bigram, 200, 60, None, bigrams_frequency)
    # print(criteria_5_1_var)

    errors = calc_error_rates_from_criteria(criteria_1_1_var, len_texts, count_texts)
    print(errors)

if __name__ == '__main__':
    main()
