import criteria as c
import gen_text as gt
import helper as h
from error_rates import calc_error_rates_for_all_criteria, calc_error_rates_from_criteria
from excel import generate_excel


def evaluate_all(encrypted_texts, forbidden_symbols, forbidden_bigrams, symbols_frequency, bigrams_frequency,
                 H_dynamic_sym, kH_dynamic_sym, H_dynamic_big, kH_dynamic_big, R, kC_L, win_len_1_1=2, n_5_1=200,
                 m_5_1=60):
    """
    Run a full suite of criteria (1.0–1.3, 3.0, 5.1) over generated texts and
    collect per-length decision counts for plaintexts and ciphertexts.

    For each criterion and for each length L, the result stores a tuple
    (plain_count, cipher_count) — how many plaintexts/ciphertexts triggered H₁.

    :param encrypted_texts: dict[int, list[dict[str, str]]]
        Mapping {L: [{"plaintext": str, "ciphertext": str}, ...]} to be evaluated.
    :param forbidden_symbols: list[str]
        Forbidden symbols set A_prh for l=1 (used in Criteria 1.0–1.3).
    :param forbidden_bigrams: list[str]
        Forbidden bigrams set A_prh for l=2 (used in Criteria 1.0–1.3).
    :param symbols_frequency: Mapping[str, float] | Sequence[tuple[str, float]]
        Reference frequencies for symbols (used in 1.2, 1.3, 5.1).
    :param bigrams_frequency: Mapping[str, float] | Sequence[tuple[str, float]]
        Reference frequencies for bigrams (used in 1.2, 1.3, 5.1).
    :param H_dynamic_sym: dict[int, float]
        Reference entropy H_l for symbols, per length L (from dynamic estimation).
    :param kH_dynamic_sym: dict[int, float]
        Entropy deviation threshold k_H for symbols, per length L.
    :param H_dynamic_big: dict[int, float]
        Reference entropy H_l for bigrams, per length L.
    :param kH_dynamic_big: dict[int, float]
        Entropy deviation threshold k_H for bigrams, per length L.
    :param win_len_1_1: int, optional (default=2)
        Threshold k_p for Criterion 1.1 (minimum distinct forbidden l-grams).
    :param n_5_1: int, optional (default=200)
        Parameter j: number of top frequent l-grams in Criterion 5.1.
    :param m_5_1: int, optional (default=60)
        Threshold k_empt for Criterion 5.1 (empty-bin cutoff).

    :return: dict[str, dict[int, tuple[int, int]]]
        Mapping {criterion_name: {L: (plain_count, cipher_count)}} for:
        "criteria_1_0_sym", "criteria_1_0_big", "criteria_1_1_sym", "criteria_1_1_big",
        "criteria_1_2_sym", "criteria_1_2_big", "criteria_1_3_sym", "criteria_1_3_big",
        "criteria_3_0_sym", "criteria_3_0_big", "criteria_5_1_sym", "criteria_5_1_big".
    """

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
           "criteria_5_1_big": c.criteria_5_1(encrypted_texts, n_5_1, m_5_1, None, bigrams_frequency),
           "criteria_structural": c.criteria_structural(encrypted_texts, 'lzma', kC_L, R)}

    return out


def _compute_errors_for_encrypted(encrypted, *, forbidden_symbols, forbidden_bigrams, symbols_frequency,
                                  bigrams_frequency, H_dynamic_sym, kH_dynamic_sym, H_dynamic_big, kH_dynamic_big,
                                  len_texts, count_texts, R, kC_L):
    """
    Evaluate all criteria on encrypted texts and compute Type I/II error rates per length.

    This helper runs the full criterion suite (via `evaluate_all`) on the provided
    plaintext–ciphertext pairs and then converts raw decision counts into statistical
    error probabilities α (false positive) and β (false negative) for each L using
    `calc_error_rates_for_all_criteria`.

    :param encrypted: dict[int, list[dict[str, str]]]
        Mapping {L: [{"plaintext": ..., "ciphertext": ...}, ...]} to evaluate.
    :param forbidden_symbols: list[str]
        Forbidden symbols set A_prh for l=1 (used in Criteria 1.0–1.3).
    :param forbidden_bigrams: list[str]
        Forbidden bigrams set A_prh for l=2 (used in Criteria 1.0–1.3).
    :param symbols_frequency: Mapping[str, float] | Sequence[tuple[str, float]]
        Reference symbol frequencies for the language model (used in 1.2, 1.3, 5.1).
    :param bigrams_frequency: Mapping[str, float] | Sequence[tuple[str, float]]
        Reference bigram frequencies for the language model (used in 1.2, 1.3, 5.1).
    :param H_dynamic_sym: dict[int, float]
        Reference entropy H_l for symbols, per L (from dynamic estimation).
    :param kH_dynamic_sym: dict[int, float]
        Entropy deviation threshold k_H for symbols, per L.
    :param H_dynamic_big: dict[int, float]
        Reference entropy H_l for bigrams, per L.
    :param kH_dynamic_big: dict[int, float]
        Entropy deviation threshold k_H for bigrams, per L.
    :param len_texts: list[int]
        List of sequence lengths L (in the same order as `count_texts`).
    :param count_texts: list[int]
        Number of test samples for each corresponding L.

    :return: dict[str, dict[int, dict[str, float]]]
        Mapping {criterion_name: {L: {'alpha': α, 'beta': β}}} — error rates per criterion and length.
    """

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
        R=R, kC_L=kC_L
    )
    return calc_error_rates_for_all_criteria(all_criteria, len_texts, count_texts)


def run_all_generations_errors(*, generated_random_texts, alphabet, len_texts, count_texts, forbidden_symbols,
                               forbidden_bigrams, symbols_frequency, bigrams_frequency, H_dynamic_sym, kH_dynamic_sym,
                               H_dynamic_big, kH_dynamic_big, R, kC_L, vigenere_keys=(1, 5, 10)):
    """
    Run all text-generation/encryption pipelines and compute error rates for each criterion.

    For each Vigenere key in `vigenere_keys`, and for the affine, affine-bigram, random,
    and recursive generators, this function:
    1) produces plaintext–ciphertext pairs, 2) evaluates the full criterion suite
    (1.0–1.3, 3.0, 5.1), and 3) converts decisions into Type I/II error rates (α, β)
    per text length L.

    :param generated_random_texts: dict[int, list[str]]
        Mapping {L: [plaintext1, plaintext2, ...]} — source plaintexts grouped by length.
    :param alphabet: list
        Alphabet used by ciphers and generators.
    :param len_texts: list[int]
        Sequence of lengths L (same order as `count_texts`) used for error-rate normalization.
    :param count_texts: list[int]
        Number of test samples for each corresponding L.
    :param forbidden_symbols: list[str]
        Forbidden set A_prh for l=1 (used in Criteria 1.0–1.3).
    :param forbidden_bigrams: list[str]
        Forbidden set A_prh for l=2 (used in Criteria 1.0–1.3).
    :param symbols_frequency: Mapping[str, float] | Sequence[tuple[str, float]]
        Reference symbol frequencies (used in Criteria 1.2, 1.3, 5.1).
    :param bigrams_frequency: Mapping[str, float] | Sequence[tuple[str, float]]
        Reference bigram frequencies (used in Criteria 1.2, 1.3, 5.1).
    :param H_dynamic_sym: dict[int, float]
        Reference entropy H_l for symbols per length L (for Criterion 3.0).
    :param kH_dynamic_sym: dict[int, float]
        Entropy deviation threshold k_H for symbols per length L (for Criterion 3.0).
    :param H_dynamic_big: dict[int, float]
        Reference entropy H_l for bigrams per length L (for Criterion 3.0 with bigrams=True).
    :param kH_dynamic_big: dict[int, float]
        Entropy deviation threshold k_H for bigrams per length L (for Criterion 3.0 with bigrams=True).
    :param vigenere_keys: Iterable[int], optional (default=(1, 5, 10))
        Key lengths to use for Vigenere encryption pipelines.

    :return: dict[str, dict[str, dict[int, dict[str, float]]]]
        Mapping {generator_name: {criterion_name: {L: {'alpha': α, 'beta': β}}}}, where
        generator_name ∈ {"vigenere_k{K}", "affine", "affine_bigram", "random", "recursive"}.
    """

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
            R=R, kC_L=kC_L
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
            R=R, kC_L=kC_L
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

    unigram_sets = h.select_unigram_sets_from_counts(symbols_count)
    forbidden_symbols = unigram_sets['forbidden']

    bigram_sets = h.select_bigram_sets_from_counts(bigrams_count_crossing_var)
    forbidden_bigrams = bigram_sets['forbidden']

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

    H_dynamic_sym, kH_dynamic_sym = h.compute_kH_dynamic(generated_random_texts)
    H_dynamic_big, kH_dynamic_big = h.compute_kH_dynamic(generated_random_texts, True)
    R, kC_L = h.compute_structural_baseline_random(generated_random_texts, compressor="lzma", alpha=0.05)

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
        R=R, kC_L=kC_L
    )

    generate_excel(all_errors, "results/cipher_results_FP_FN_test.xlsx")

    print(f'====================== TASK 5 ======================')
    text_for_analysis = { 10000: [gt.generate_of_non_coherent_text(10000)]}
    encrypted_texts_by_affine = gt.encrypt_texts_by_affine(text_for_analysis, alphabet)
    criteria_1_0_var = c.criteria_1_0(encrypted_texts_by_affine, None, forbidden_bigrams)
    errors = calc_error_rates_from_criteria(criteria_1_0_var, [10000], [1])
    print(f'FP: {errors[10000]['alpha']} \nFN: {errors[10000]['beta']}')


if __name__ == '__main__':
    main()
