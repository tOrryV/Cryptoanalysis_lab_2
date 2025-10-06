def criteria_1_0(text, forbidden_symbols=None, forbidden_bigrams=None):
    result = {}

    for length, texts in text.items():
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