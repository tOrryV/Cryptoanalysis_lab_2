def calc_error_rates_from_criteria(criteria_result, len_texts, count_texts):
    """
    Computes Type I (α) and Type II (β) error probabilities for a single criterion.

    This function calculates the statistical error rates of a binary hypothesis test distinguishing H₀ (normal text)
    and H₁ (random or abnormal text). The metric α corresponds to the probability of a false positive —
    accepting H₁ when H₀ is true; β corresponds to the probability of a false negative —
    accepting H₀ when H₁ is true.

    Mathematically:
        α = P(H₁ | H₀) = plain_accept_H₁ / N
        β = P(H₀ | H₁) = 1 - (cipher_accept_H₀ / N)

    :param criteria_result: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_accept_H1, cipher_accept_H0)} from the criterion function.
    :param len_texts: list[int]
        List of tested sequence lengths.
    :param count_texts: list[int]
        List of total number of tests (sample counts) corresponding to each sequence length.
    :return: dict[int, dict[str, float]]
        Mapping {text_length: {'alpha': α, 'beta': β}} — computed error probabilities.
    """

    result = {}
    n_by_L = dict(zip(len_texts, count_texts))

    for L, (plain_accept_H1, cipher_accept_H0) in criteria_result.items():
        n_tests = n_by_L.get(L, 0)
        alpha = (plain_accept_H1 / n_tests) if n_tests else 0.0
        beta = ((n_tests - cipher_accept_H0) / n_tests) if n_tests else 0.0
        result[L] = {'alpha': alpha, 'beta': beta}
    return result


def calc_error_rates_for_all_criteria(all_criteria, len_texts, count_texts):
    """
    Computes Type I (α) and Type II (β) error probabilities for multiple criteria.

    This function aggregates the statistical error rates across all tested criteria.
    Each criterion’s result is processed individually by `calc_error_rates_from_criteria`,
    producing a structured comparison of α and β values for model evaluation.

    :param all_criteria: dict[str, dict[int, tuple[int, int]]]
        Mapping {criterion_name: {text_length: (plain_accept_H1, cipher_accept_H0)}}.
    :param len_texts: list[int]
        List of tested sequence lengths.
    :param count_texts: list[int]
        List of total number of tests (sample counts) corresponding to each sequence length.
    :return: dict[str, dict[int, dict[str, float]]]
        Mapping {criterion_name: {text_length: {'alpha': α, 'beta': β}}} —
        complete overview of statistical performance across all criteria.
    """

    result = {}
    for crit_name, crit_result in all_criteria.items():
        result[crit_name] = calc_error_rates_from_criteria(crit_result, len_texts, count_texts)
    return result
