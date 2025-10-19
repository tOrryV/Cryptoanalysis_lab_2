import criteria as c
import gen_text as gt
import helper as h
from error_rates import calc_error_rates_for_all_criteria
from excel import generate_excel


def evaluate_all(encrypted_texts, forbidden_symbols, forbidden_bigrams, symbols_frequency, bigrams_frequency,
                 H_dynamic_sym, kH_dynamic_sym, H_dynamic_big, kH_dynamic_big, win_len_1_1=2, n_5_1=200, m_5_1=60):
    out = {"criteria_1_0_sym": c.criteria_1_0(encrypted_texts, forbidden_symbols),
           "criteria_1_0_big": c.criteria_1_0(encrypted_texts, None, forbidden_bigrams),
           "criteria_1_1_sym": c.criteria_1_1(encrypted_texts, win_len_1_1, forbidden_symbols),
           "criteria_1_1_big": c.criteria_1_1(encrypted_texts, win_len_1_1, None, forbidden_bigrams),
           "criteria_1_2_sym": c.criteria_1_2(encrypted_texts, forbidden_symbols, symbols_frequency),
           "criteria_1_2_big": c.criteria_1_2(encrypted_texts, None, None,
                                              forbidden_bigrams, bigrams_frequency),
           "criteria_1_3_sym": c.criteria_1_3(encrypted_texts, forbidden_symbols, symbols_frequency),
           "criteria_1_3_big": c.criteria_1_3(encrypted_texts, None, None,
                                              forbidden_bigrams, bigrams_frequency),
           "criteria_3_0_sym": c.criteria_3_0(encrypted_texts, H_dynamic_sym, kH_dynamic_sym),
           "criteria_3_0_big": c.criteria_3_0(encrypted_texts, H_dynamic_big, kH_dynamic_big, True),
           "criteria_5_1_sym": c.criteria_5_1(encrypted_texts, n_5_1, m_5_1, symbols_frequency),
           "criteria_5_1_big": c.criteria_5_1(encrypted_texts, n_5_1, m_5_1, None, bigrams_frequency)}

    return out


def _compute_errors_for_encrypted(encrypted, *, forbidden_symbols, forbidden_bigrams, symbols_frequency,
                                  bigrams_frequency, H_dynamic_sym, kH_dynamic_sym, H_dynamic_big, kH_dynamic_big,
                                  len_texts, count_texts):
    all_criteria = evaluate_all(
        encrypted,
        forbidden_symbols=forbidden_symbols,
        forbidden_bigrams=forbidden_bigrams,
        symbols_frequency=symbols_frequency,
        bigrams_frequency=bigrams_frequency,
        H_dynamic_sym=H_dynamic_sym,
        kH_dynamic_sym=kH_dynamic_sym,
        H_dynamic_big=H_dynamic_big,
        kH_dynamic_big=kH_dynamic_big,
    )
    return calc_error_rates_for_all_criteria(all_criteria, len_texts, count_texts)


def run_all_generations_errors(*, generated_random_texts, alphabet, len_texts, count_texts, forbidden_symbols,
                               forbidden_bigrams, symbols_frequency, bigrams_frequency, H_dynamic_sym, kH_dynamic_sym,
                               H_dynamic_big, kH_dynamic_big, vigenere_keys=(1, 5, 10)):
    out = {}

    for k in vigenere_keys:
        enc = gt.encrypt_texts_by_vigenere(generated_random_texts, alphabet, k)
        out[f"vigenere_k{k}"] = _compute_errors_for_encrypted(
            enc,
            forbidden_symbols=forbidden_symbols,
            forbidden_bigrams=forbidden_bigrams,
            symbols_frequency=symbols_frequency,
            bigrams_frequency=bigrams_frequency,
            H_dynamic_sym=H_dynamic_sym,
            kH_dynamic_sym=kH_dynamic_sym,
            H_dynamic_big=H_dynamic_big,
            kH_dynamic_big=kH_dynamic_big,
            len_texts=len_texts,
            count_texts=count_texts,
        )

    gens = [
        ("affine",        gt.encrypt_texts_by_affine(generated_random_texts, alphabet)),
        ("affine_bigram", gt.encrypt_texts_by_affine_bigram(generated_random_texts, alphabet, True, alphabet[0])),
        ("random",        gt.generate_multiple_random_texts(alphabet, generated_random_texts)),
        ("recursive",     gt.generate_multiple_recurse_texts(alphabet, generated_random_texts)),
    ]
    for name, enc in gens:
        out[name] = _compute_errors_for_encrypted(
            enc,
            forbidden_symbols=forbidden_symbols,
            forbidden_bigrams=forbidden_bigrams,
            symbols_frequency=symbols_frequency,
            bigrams_frequency=bigrams_frequency,
            H_dynamic_sym=H_dynamic_sym,
            kH_dynamic_sym=kH_dynamic_sym,
            H_dynamic_big=H_dynamic_big,
            kH_dynamic_big=kH_dynamic_big,
            len_texts=len_texts,
            count_texts=count_texts,
        )

    return out


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

    unigram_sets = h.select_unigram_sets_from_counts(symbols_count)
    forbidden_symbols = unigram_sets['forbidden']

    bigram_sets = h.select_bigram_sets_from_counts(bigrams_count_crossing_var)
    forbidden_bigrams = bigram_sets['forbidden']

    clean_texts_by_L = h.make_clean_texts_by_L(cleaned_data, len_texts)
    H_dynamic_sym, kH_dynamic_sym = h.compute_kH_dynamic(clean_texts_by_L)
    H_dynamic_big, kH_dynamic_big = h.compute_kH_dynamic(clean_texts_by_L, True)

    all_errors = run_all_generations_errors(
        generated_random_texts=generated_random_texts,
        alphabet=alphabet,
        len_texts=len_texts,
        count_texts=count_texts,
        forbidden_symbols=forbidden_symbols,
        forbidden_bigrams=forbidden_bigrams,
        symbols_frequency=symbols_frequency,
        bigrams_frequency=bigrams_frequency,
        H_dynamic_sym=H_dynamic_sym,
        kH_dynamic_sym=kH_dynamic_sym,
        H_dynamic_big=H_dynamic_big,
        kH_dynamic_big=kH_dynamic_big,
    )

    generate_excel(all_errors, "cipher_results_FP_FN.xlsx")

    # text_for_analysis = {
    #     10: [gt.generate_of_non_coherent_text(10)]
    # }
    # encrypted_texts_by_affine = gt.encrypt_texts_by_affine(text_for_analysis, alphabet)
    # print(encrypted_texts_by_affine)
    # criteria_1_0_var = c.criteria_1_0(encrypted_texts_by_affine, None, forbidden_bigrams)
    # print(criteria_1_0_var)
    # errors = calc_error_rates_from_criteria(criteria_1_0_var, [10], [1])
    # print(errors)


if __name__ == '__main__':
    main()
