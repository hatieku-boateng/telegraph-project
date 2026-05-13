"""
Morse code processing routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..morse import decode_morse, encode_text, MORSE_DICT

morse_bp = Blueprint('morse', __name__, url_prefix='/api')

@morse_bp.route('/morse/encode', methods=['POST'])
@jwt_required()
def encode_text_route():
    """Encode text to Morse code"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        morse_code = encode_text(text)
        return jsonify({
            'text': text,
            'morse_code': morse_code
        }), 200
    except Exception as e:
        return jsonify({'error': f'Encoding failed: {str(e)}'}), 500


@morse_bp.route('/morse/decode', methods=['POST'])
@jwt_required()
def decode_morse_route():
    """Decode Morse code to text"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    morse_code = data.get('morse_code', '').strip()
    if not morse_code:
        return jsonify({'error': 'Morse code is required'}), 400

    try:
        tokens = morse_code.split()
        decoded_chars = [
            ' ' if token == '/' else decode_morse(token)
            for token in tokens
        ]
        decoded = ''.join(decoded_chars)
        return jsonify({
            'morse_code': morse_code,
            'text': decoded
        }), 200
    except Exception as e:
        return jsonify({'error': f'Decoding failed: {str(e)}'}), 500


@morse_bp.route('/morse/validate', methods=['POST'])
@jwt_required()
def validate_morse():
    """Validate Morse code format"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    morse_code = data.get('morse_code', '').strip()
    if not morse_code:
        return jsonify({'error': 'Morse code is required'}), 400

    try:
        tokens = morse_code.split()
        is_valid = all(token in MORSE_DICT or token == '/' for token in tokens)
        return jsonify({
            'morse_code': morse_code,
            'is_valid': is_valid
        }), 200
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500


@morse_bp.route('/morse/reference', methods=['GET'])
@jwt_required()
def get_morse_reference():
    """Get Morse code reference table"""
    try:
        reference = {
            'morse_to_text': MORSE_DICT,
            'text_to_morse': {v: k for k, v in MORSE_DICT.items()}
        }
        return jsonify(reference), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get reference: {str(e)}'}), 500