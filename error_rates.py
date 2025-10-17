def calc_error_rates_from_criteria(criteria_result, len_texts, count_texts):
    result = {}

    for L, (plain_accept_H1, cipher_accept_H0) in criteria_result.items():
        if L in len_texts:
            idx = len_texts.index(L)
            n_tests = count_texts[idx]
        else:
            continue

        alpha = plain_accept_H1 / n_tests if n_tests else 0.0

        beta = (n_tests - cipher_accept_H0) / n_tests if n_tests else 0.0

        result[L] = {
            'alpha': alpha,
            'beta': beta,
            # 'plain_accept_H1': plain_accept_H1,
            # 'cipher_accept_H0': cipher_accept_H0,
            # 'tests_total': n_tests
        }

    return result
