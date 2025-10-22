import bz2
import lzma
import zlib
import helper as h


def criteria_1_0(generated_texts, forbidden_symbols=None, forbidden_bigrams=None):
    """
    Criterion 1.0 — Detection of forbidden l-grams in plaintext and ciphertext sequences.

    This criterion identifies the presence of *forbidden l-grams* — combinations of symbols
    that are impossible or extremely rare in meaningful text. Such l-grams are defined by the
    set A_prh ⊂ (Z_m)^l, which contains h_p forbidden elements determined from frequency analysis
    of a natural language corpus.

    Algorithm:
        0. Compute frequencies of l-grams over the language alphabet Z_m and define the forbidden set A_prh.
        1. Inspect the sequence X of length L (plaintext and ciphertext).
        2. If any l-gram x ∈ A_prh appears in X, hypothesis H₁ is accepted (sequence contains forbidden l-gram);
           otherwise, hypothesis H₀ is accepted.

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]} representing generated sequences.
    :param forbidden_symbols: list[str] | None
        List of forbidden single characters defining the forbidden set A_prh for l=1.
    :param forbidden_bigrams: list[str] | None
        List of forbidden bigrams defining the forbidden set A_prh for l=2.
    :return: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_count, cipher_count)} where each tuple represents
        the number of plaintexts and ciphertexts containing at least one forbidden l-gram.
    """

    result = {}

    for length, texts in generated_texts.items():
        plain_count = 0
        cipher_count = 0
        for text in texts:
            if forbidden_bigrams is not None:
                if any(bg in text['plaintext'] for bg in forbidden_bigrams):
                    plain_count += 1
                if any(bg in text['ciphertext'] for bg in forbidden_bigrams):
                    cipher_count += 1
            else:
                if any(ch in forbidden_symbols for ch in text['plaintext']):
                    plain_count += 1
                if any(ch in forbidden_symbols for ch in text['ciphertext']):
                    cipher_count += 1
        result[length] = (plain_count, cipher_count)
    return result


def criteria_1_1(generated_texts, kp=2, forbidden_symbols=None, forbidden_bigrams=None):
    """
    Criterion 1.1 — Detection of multiple forbidden l-grams exceeding a threshold kₚ.

    This criterion extends Criterion 1.0 by introducing a threshold kₚ (1 < kₚ ≤ hₚ) —
    the minimum number of distinct forbidden l-grams required to accept hypothesis H₁.
    The set A_ap represents the set of forbidden l-grams actually encountered in the
    analyzed sequence X. If |A_ap ∩ A_prh| ≥ kₚ, hypothesis H₁ is accepted; otherwise, H₀.

    Algorithm:
        0. Compute frequencies of l-grams over the alphabet Z_m and define the forbidden set A_prh.
        1. Initialize A_ap as an empty set.
        2. For each l-gram x ∈ X, if x ∈ A_prh, add it to A_ap.
        3. If |A_ap ∩ A_prh| ≥ kₚ, accept H₁; otherwise, accept H₀.

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]} representing generated sequences.
    :param kp: int
        Threshold number of distinct forbidden l-grams required to trigger hypothesis H₁.
    :param forbidden_symbols: list[str] | None
        List of forbidden symbols defining A_prh for l=1.
    :param forbidden_bigrams: list[str] | None
        List of forbidden bigrams defining A_prh for l=2.
    :return: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_count, cipher_count)}, where each tuple represents
        the number of plaintexts and ciphertexts containing at least kₚ forbidden l-grams.
    """

    result = {}

    for length, texts in generated_texts.items():
        plain_count = 0
        cipher_count = 0

        for text in texts:
            if forbidden_bigrams is not None:
                found_plain = {bg for bg in forbidden_bigrams if bg in text['plaintext']}
                found_cipher = {bg for bg in forbidden_bigrams if bg in text['ciphertext']}
            else:
                found_plain = {ch for ch in forbidden_symbols if ch in text['plaintext']}
                found_cipher = {ch for ch in forbidden_symbols if ch in text['ciphertext']}

            if len(found_plain) >= kp:
                plain_count += 1
            if len(found_cipher) >= kp:
                cipher_count += 1

        result[length] = (plain_count, cipher_count)

    return result


def criteria_1_2(generated_texts, forbidden_symbols=None, symbols_frequency=None,
                 forbidden_bigrams=None, bigrams_frequency=None):
    """
    Criterion 1.2 — Detection of forbidden l-grams with abnormally high frequency.

    This criterion extends the forbidden l-gram analysis by considering *frequency deviation*
    from expected language statistics. For each forbidden l-gram x ∈ A_prh, its observed frequency fₓ
    within the analyzed sequence X is compared with the reference frequency kₓ determined
    from the natural language model. If any fₓ > kₓ, hypothesis H₁ is accepted (sequence exhibits
    unnatural frequency distribution); otherwise, H₀ is accepted.

    Algorithm:
        0. Compute reference frequencies kₓ for all l-grams over alphabet Z_m (language model).
        1. For each sequence X (plaintext and ciphertext), calculate observed frequencies fₓ
           of all forbidden l-grams x ∈ A_prh.
        2. If ∃x : fₓ > kₓ, accept H₁; otherwise, accept H₀.

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]} representing analyzed sequences.
    :param forbidden_symbols: list[str] | None
        List of forbidden single symbols (for l=1 analysis).
    :param symbols_frequency: dict[str, float] | None
        Reference frequencies of single symbols in natural language (kₓ for l=1).
    :param forbidden_bigrams: list[str] | None
        List of forbidden bigrams (for l=2 analysis).
    :param bigrams_frequency: dict[str, float] | None
        Reference frequencies of bigrams in natural language (kₓ for l=2).
    :return: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_count, cipher_count)} — number of plaintexts and ciphertexts
        where at least one forbidden l-gram exceeds its reference frequency threshold.
    """

    result = {}

    if forbidden_bigrams:
        ref_freq = dict(bigrams_frequency)
    else:
        ref_freq = dict(symbols_frequency)

    for length, texts in generated_texts.items():
        plain_count = 0
        cipher_count = 0

        for text in texts:
            if forbidden_bigrams:
                total_plain = len(text['plaintext']) - 1
                found_plain = {}
                for i in range(total_plain):
                    bg = text['plaintext'][i:i+2]
                    if bg in forbidden_bigrams:
                        found_plain[bg] = found_plain.get(bg, 0) + 1

                for bg, cnt in found_plain.items():
                    freq = cnt / total_plain
                    if freq > ref_freq.get(bg, 0):
                        plain_count += 1
                        break

                total_cipher = len(text['ciphertext']) - 1
                found_cipher = {}
                for i in range(total_cipher):
                    bg = text['ciphertext'][i:i+2]
                    if bg in forbidden_bigrams:
                        found_cipher[bg] = found_cipher.get(bg, 0) + 1

                for bg, cnt in found_cipher.items():
                    freq = cnt / total_cipher
                    if freq > ref_freq.get(bg, 0):
                        cipher_count += 1
                        break
            else:
                total_plain = len(text['plaintext'])
                found_plain = {}
                for ch in text['plaintext']:
                    if ch in forbidden_symbols:
                        found_plain[ch] = found_plain.get(ch, 0) + 1

                for ch, cnt in found_plain.items():
                    freq = cnt / total_plain
                    if freq > ref_freq.get(ch, 0):
                        plain_count += 1
                        break

                total_cipher = len(text['ciphertext'])
                found_cipher = {}
                for ch in text['ciphertext']:
                    if ch in forbidden_symbols:
                        found_cipher[ch] = found_cipher.get(ch, 0) + 1

                for ch, cnt in found_cipher.items():
                    freq = cnt / total_cipher
                    if freq > ref_freq.get(ch, 0):
                        cipher_count += 1
                        break

        result[length] = (plain_count, cipher_count)

    return result


def criteria_1_3(generated_texts, forbidden_symbols=None, symbols_frequency=None,
                 forbidden_bigrams=None, bigrams_frequency=None):
    """
    Criterion 1.3 — Detection of forbidden l-grams based on total frequency deviation.

    This criterion generalizes Criterion 1.2 by aggregating the frequencies of all forbidden
    l-grams within the analyzed sequence. The cumulative observed frequency Fₚ is compared
    to the expected cumulative reference frequency Kₚ derived from the natural language model.
    If Fₚ > Kₚ, hypothesis H₁ is accepted (sequence shows excessive occurrence of forbidden
    structures); otherwise, H₀ is accepted.

    Mathematically:
        Fₚ = Σ_{x∈A_prh} f(x)       — total observed frequency of forbidden l-grams
        Kₚ = Σ_{x∈A_prh} kₓ         — total expected frequency from the language model
    Decision rule:
        If Fₚ > Kₚ → accept H₁
        Else → accept H₀

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]} representing generated sequences.
    :param forbidden_symbols: list[str] | None
        List of forbidden single symbols forming the set A_prh (for l=1 analysis).
    :param symbols_frequency: dict[str, float] | None
        Reference frequencies of symbols kₓ in natural language (for l=1).
    :param forbidden_bigrams: list[str] | None
        List of forbidden bigrams forming the set A_prh (for l=2 analysis).
    :param bigrams_frequency: dict[str, float] | None
        Reference frequencies of bigrams kₓ in natural language (for l=2).
    :return: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_count, cipher_count)} — number of plaintexts and ciphertexts
        where the total observed frequency Fₚ of forbidden l-grams exceeds Kₚ.
    """

    result = {}

    if forbidden_bigrams:
        ref_freq = dict(bigrams_frequency)
        Kp = sum(ref_freq.get(bg, 0) for bg in forbidden_bigrams)
    else:
        ref_freq = dict(symbols_frequency)
        Kp = sum(ref_freq.get(ch, 0) for ch in forbidden_symbols)

    for length, texts in generated_texts.items():
        plain_count = 0
        cipher_count = 0

        for text in texts:
            if forbidden_bigrams:
                total = len(text['plaintext']) - 1
                Fp = 0
                for i in range(total):
                    bg = text['plaintext'][i:i+2]
                    if bg in forbidden_bigrams:
                        Fp += 1
                Fp = Fp / total

                if Fp > Kp:
                    plain_count += 1

                total = len(text['ciphertext']) - 1
                Fc = 0
                for i in range(total):
                    bg = text['ciphertext'][i:i+2]
                    if bg in forbidden_bigrams:
                        Fc += 1
                Fc = Fc / total

                if Fc > Kp:
                    cipher_count += 1
            else:
                total = len(text['plaintext'])
                Fp = sum(1 for ch in text['plaintext'] if ch in forbidden_symbols) / total

                if Fp > Kp:
                    plain_count += 1

                total = len(text['ciphertext'])
                Fc = sum(1 for ch in text['ciphertext'] if ch in forbidden_symbols) / total

                if Fc > Kp:
                    cipher_count += 1

        result[length] = (plain_count, cipher_count)

    return result


def criteria_3_0(generated_texts, H, kH=0.1, bigrams=False):
    """
    Criterion 3.0 — Entropy deviation test for l-grams (symbols or bigrams).

    Compute the per-symbol entropy Hₗ of the language model (reference) and compare it with
    the entropy H′ₗ of each analyzed sequence X. If |H′ₗ − Hₗ| > k_H, accept hypothesis H₁
    (sequence is non-linguistic/abnormal); otherwise accept H₀. When `bigrams=True`, entropy is
    computed over crossing bigrams; otherwise over single symbols.

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]} of sequences to test.
    :param H: float | dict[int, float]
        Reference per-symbol entropy Hₗ of the language (scalar for all lengths or per-length dict).
    :param kH: float | dict[int, float]
        Allowed deviation threshold k_H (scalar or per-length dict).
    :param bigrams: bool
        If True, use bigram frequency counts; if False, use single-symbol counts.
    :return: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_count, cipher_count)} — numbers of plaintexts and ciphertexts
        whose entropy deviates from the reference by more than k_H.
    """

    result = {}

    count_mode = h.bigram_count_crossing if bigrams else h.symbol_count
    entropy = h.entropy_calculate

    for length, texts in generated_texts.items():
        H_curr = H[length] if isinstance(H, dict) else H
        kH_curr = kH[length] if isinstance(kH, dict) else kH

        plain_count = 0
        cipher_count = 0

        for text in texts:
            p = text['plaintext']
            c = text['ciphertext']

            entropy_plain = entropy(count_mode(p))
            entropy_cipher = entropy(count_mode(c))

            if abs(entropy_plain - H_curr) > kH_curr:
                plain_count += 1
            if abs(entropy_cipher - H_curr) > kH_curr:
                cipher_count += 1

        result[length] = (plain_count, cipher_count)

    return result


def criteria_5_1(generated_texts, j, kempt, symbols_frequency=None, bigrams_frequency=None):
    """
    Criterion 5.1 — Frequency emptiness test for top-j frequent l-grams.

    This criterion evaluates the representativeness of a sequence by checking how many of the most
    frequent l-grams from the reference language (top j elements) do *not* appear in the analyzed
    sequence X. The number of such “empty bins” (f_empt) is compared to a threshold k_empt.
    If f_empt ≥ k_empt, hypothesis H₁ is accepted (sequence is abnormal or lacks typical patterns);
    otherwise H₀ is accepted.

    Mathematically:
        f_empt = j - |{x ∈ B_frq ∩ X}|
    Decision rule:
        If f_empt ≥ k_empt → accept H₁
        Else → accept H₀

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {text_length: [{"plaintext": ..., "ciphertext": ...}, ...]} — test data sequences.
    :param j: int
        Number of top most frequent l-grams (from reference distribution) forming B_frq.
    :param kempt: int
        Threshold number of empty bins allowed before accepting H₁.
    :param symbols_frequency: list[tuple[str, float]] | None
        List of tuples (symbol, frequency) for single-character statistics.
    :param bigrams_frequency: list[tuple[str, float]] | None
        List of tuples (bigram, frequency) for bigram statistics.
    :return: dict[int, tuple[int, int]]
        Mapping {text_length: (plain_count, cipher_count)} — number of plaintexts and ciphertexts
        where the number of missing frequent l-grams exceeds the threshold k_empt.
    """

    result = {}

    if bigrams_frequency:
        top = [bg for bg, _ in bigrams_frequency][:j]
    else:
        top = [ch for ch, _ in symbols_frequency][:j]
    top_set = set(top)

    for length, texts in generated_texts.items():
        plain_count = 0
        cipher_count = 0

        for text in texts:
            p = text['plaintext']
            c = text['ciphertext']

            if bigrams_frequency:
                present_p = set()
                for i in range(len(p) - 1):
                    bg = p[i:i+2]
                    if bg in top_set:
                        present_p.add(bg)

                present_c = set()
                for i in range(len(c) - 1):
                    bg = c[i:i+2]
                    if bg in top_set:
                        present_c.add(bg)
            else:
                present_p = {ch for ch in p if ch in top_set}
                present_c = {ch for ch in c if ch in top_set}

            f_empty_p = j - len(present_p)
            f_empty_c = j - len(present_c)

            if f_empty_p >= kempt:
                plain_count += 1
            if f_empty_c >= kempt:
                cipher_count += 1

        result[length] = (plain_count, cipher_count)

    return result


def criteria_structural(generated_texts, compressor="lzma", kC=0.0, baseline_random=None):
    """
    Criterion (Structural) — Compression-based test for detecting random/abnormal text.

    Classifies a sequence as H₁ (“random/abnormal”) if it is poorly compressible under a
    chosen algorithm. With per-length random baselines R_L, a tolerance k_C defines how
    much better than random a sequence must compress to be considered non-random (H₀).

    Decision rule for a sequence X of length L with compression ratio r(X):
        If baseline_random[L] is given:
            Accept H₁  ⇔  r(X) ≥ R_L − k_C(L)
        Else (global threshold is used):
            Accept H₁  ⇔  r(X) ≥ k_C
    Here r(X) = compressed_size(X) / original_size(X) in bytes.

    :param generated_texts: dict[int, list[dict[str, str]]]
        Mapping {L: [{"plaintext": str, "ciphertext": str}, ...]} to evaluate.
    :param compressor: str, optional (default="lzma")
        Compression backend: one of {"lzma", "deflate", "bzip2"}.
    :param kC: float | dict[int, float], optional (default=0.0)
        Tolerance for declaring H₁. If dict is provided, uses per-length k_C(L),
        analogous to kH in Criterion 3.0; otherwise uses a scalar cutoff.
    :param baseline_random: dict[int, float] | None
        Optional per-length baselines for random text, {L: R_L}. If omitted, kC is treated
        as the absolute cutoff.

    :return: dict[int, tuple[int, int]]
        Mapping {L: (plain_H1_count, cipher_H1_count)} — numbers of plaintexts and ciphertexts
        classified as H₁ under the rule above.
    """

    def _compress_ratio(s: str) -> float:
        data = s.encode("utf-8", errors="ignore")
        if not data:
            return 1.0
        if compressor == "lzma":
            comp = lzma.compress(data)
        elif compressor == "deflate":
            comp = zlib.compress(data, level=9)
        elif compressor == "bzip2":
            comp = bz2.compress(data, compresslevel=9)
        else:
            raise ValueError(f"Unknown compressor: {compressor}")
        return len(comp) / len(data)

    def _kC_for(_L):
        if isinstance(kC, dict):
            return float(kC.get(_L, 0.0))
        return float(kC)

    result = {}
    for L, pairs in generated_texts.items():
        R_L = None if baseline_random is None else baseline_random.get(L)
        kC_L = _kC_for(L)

        plain_struct = 0
        cipher_struct = 0

        for item in pairs:
            rp = _compress_ratio(item["plaintext"])
            rc = _compress_ratio(item["ciphertext"])

            if R_L is not None:
                if rp < R_L - kC_L:
                    plain_struct += 1
                if rc < R_L - kC_L:
                    cipher_struct += 1
            else:
                if rp <= kC_L:
                    plain_struct += 1
                if rc <= kC_L:
                    cipher_struct += 1

        result[L] = (plain_struct, cipher_struct)

    return result
