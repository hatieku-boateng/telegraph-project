"""Morse code dictionary and encoding/decoding utilities."""

MORSE_DICT = {
    # Letters
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z",
    # Numbers
    "-----": "0", ".----": "1", "..---": "2", "...--": "3",
    "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9",
    # Punctuation
    ".-.-.-": ".", "--..--": ",", "..--..": "?",
    ".----.": "'", "-.-.--": "!", "-..-.": "/",
    "-.--.": "(", "-.--.-": ")", ".-...": "&",
    "---...": ":", "-.-.-.": ";", "-...-": "=",
    ".-.-.": "+", "-....-": "-", "..--.-": "_",
    ".-..-.": "\"", "...-..-": "$", ".--.-.": "@"
}

REVERSE_MORSE_DICT = {v: k for k, v in MORSE_DICT.items()}


def decode_morse(symbol_buffer: str) -> str:
    """Decode a dot/dash sequence to a character.
    
    Args:
        symbol_buffer: String of dots (.) and dashes (-)
        
    Returns:
        Decoded character, or '?' if unknown
    """
    return MORSE_DICT.get(symbol_buffer, "?")


def encode_text(text: str) -> str:
    """Encode text to Morse code.
    
    Args:
        text: Plain text to encode
        
    Returns:
        Morse code with spaces between letters and ' / ' between words
    """
    text = text.upper()
    encoded_tokens = []
    pending_word_gap = False

    for char in text:
        if char.isspace():
            if encoded_tokens:
                pending_word_gap = True
            continue

        if pending_word_gap:
            encoded_tokens.append("/")
            pending_word_gap = False

        encoded_tokens.append(REVERSE_MORSE_DICT.get(char, "?"))

    return " ".join(encoded_tokens)
