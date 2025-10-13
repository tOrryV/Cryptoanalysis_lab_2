def criteria_1_0(generated_texts, forbidden_symbols=None, forbidden_bigrams=None):
    result = {}

    for length, texts in generated_texts.items():
        plain_count = 0
        cipher_count = 0
        for text in texts:
            if forbidden_bigrams:
                for bg in forbidden_bigrams:
                    if bg in text['plaintext']:
                        plain_count += 1
                        break
                    if bg in text['ciphertext']:
                        cipher_count += 1
                        break
            else:
                if any(symbol in forbidden_symbols for symbol in text['plaintext']):
                    plain_count += 1
                if any(symbol in forbidden_symbols for symbol in text['ciphertext']):
                    cipher_count += 1

        result[length] = (plain_count, cipher_count)

    return result


def criteria_1_1(generated_texts, kp=2, forbidden_symbols=None, forbidden_bigrams=None):
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


def criteria_3_0(generated_texts, ):
    pass