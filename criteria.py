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