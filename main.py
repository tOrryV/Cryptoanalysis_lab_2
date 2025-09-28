def text_processing(filename):
    with open(filename, 'r', encoding='UTF-8') as text_file:
        text = text_file.read().lower()

    alphabet = [
        'а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м',
        'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я',
    ]

    words = text.split()

    for index, word in enumerate(words):
        for symbol in word:
            if symbol not in alphabet:
                word = word.replace(symbol, '')
            elif symbol == 'ґ':
                word = word.replace(symbol, 'г')

        words[index] = word

    return ''.join(words)


data = text_processing('data/data.txt')
