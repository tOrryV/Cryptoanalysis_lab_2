def calc_error_rates_from_criteria(criteria_result, len_texts, count_texts):

    result = {}
    n_by_L = dict(zip(len_texts, count_texts))

    for L, (plain_accept_H1, cipher_accept_H0) in criteria_result.items():
        n_tests = n_by_L.get(L, 0)
        alpha = (plain_accept_H1 / n_tests) if n_tests else 0.0
        beta = ((n_tests - cipher_accept_H0) / n_tests) if n_tests else 0.0
        result[L] = {'alpha': alpha, 'beta': beta}
    return result


def calc_error_rates_for_all_criteria(all_criteria, len_texts, count_texts):
    result = {}
    for crit_name, crit_result in all_criteria.items():
        result[crit_name] = calc_error_rates_from_criteria(crit_result, len_texts, count_texts)
    return result
