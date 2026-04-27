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
    morse_words = []
    
    for word in text.split():
        morse_letters = []
        for char in word:
            morse_letters.append(REVERSE_MORSE_DICT.get(char, "?"))
        morse_words.append(" ".join(morse_letters))
    
    return " / ".join(morse_words)
