def encrypt(_alphabet, _text, _key):
    """
    The encrypt function takes in a string of characters, and returns an encrypted version of that string.
    The encryption is done by shifting each character in the input message to the right by a number equal to its index
    in the alphabet. For example, if we have an alphabet with 26 letters (a-z), then 'a' will be shifted 0 places, 'b' 1 place, etc.
    :param _alphabet: Define the alphabet that will be used to encrypt the message
    :param _text: Pass the text to be encrypted
    :param _key: Encrypt the text
    :return: A string that is the encrypted text
    """

    result = ''
    for i in range(len(_text)):
        symbol_index = _alphabet.index(_text[i])
        key_index = _alphabet.index(_key[i % len(_key)])
        value = (symbol_index + key_index) % len(_alphabet)
        result += _alphabet[value]

    return result


def decrypt(_alphabet, _text, _key):
    """
    The decrypt function takes in a message and key, and returns the decrypted message.
    :param _alphabet: Define the alphabet used in the encryption and decryption
    :param _text: Store the text to be decrypted
    :param _key: Decrypt the text
    :return: A string of the decrypted text
    """

    result = ''
    for i in range(len(_text)):
        symbol_index = _alphabet.index(_text[i])
        key_index = _alphabet.index(_key[i % len(_key)])
        value = (symbol_index - key_index) % len(_alphabet)
        result += _alphabet[value]

    return result
