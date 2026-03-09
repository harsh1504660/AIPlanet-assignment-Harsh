"""
Multimodal Input Processing for Math Mentor
Handles Image OCR, Audio ASR, and Text inputs
"""

import os
import base64
import tempfile
from pathlib import Path
from typing import Tuple, Optional, Dict
import re


# ─────────────────────────────────────────────
# IMAGE OCR PROCESSING
# ─────────────────────────────────────────────

def process_image_ocr(image_bytes: bytes, image_type: str = "image/png") -> Dict:
    """
    Extract text from image using OCR.
    Returns: {text, confidence, method_used, error}
    """
    result = {
        "text": "",
        "confidence": 0.0,
        "method_used": "none",
        "error": None,
        "raw_results": []
    }

    # Method 1: Try Claude Vision (most accurate for math)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        
        # Encode image to base64
        b64_image = base64.standard_b64encode(image_bytes).decode("utf-8")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_type,
                            "data": b64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": """Extract ALL text and mathematical expressions from this image.
Return ONLY the extracted text/math, preserving the mathematical notation as closely as possible.
Use proper math notation: x² for x squared, √ for square root, ∫ for integral, etc.
If it's a handwritten problem, transcribe it accurately."""
                    }
                ]
            }]
        )
        
        extracted = response.content[0].text.strip()
        if extracted:
            result["text"] = extracted
            result["confidence"] = 0.92
            result["method_used"] = "claude_vision"
            return result
    except Exception as e:
        result["error"] = f"Claude Vision: {str(e)}"

    # Method 2: Try EasyOCR
    try:
        import easyocr
        import numpy as np
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        ocr_results = reader.readtext(img_array)
        
        if ocr_results:
            texts = [item[1] for item in ocr_results]
            confidences = [item[2] for item in ocr_results]
            
            result["text"] = " ".join(texts)
            result["confidence"] = sum(confidences) / len(confidences)
            result["method_used"] = "easyocr"
            result["raw_results"] = [{"text": t, "confidence": c} for t, c in zip(texts, confidences)]
            return result
    except Exception as e:
        result["error"] = (result.get("error", "") + f" | EasyOCR: {str(e)}")

    # Method 3: Try Tesseract
    try:
        import pytesseract
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_bytes))
        
        # Get detailed output
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # Filter by confidence
        words = []
        confidences = []
        for i, conf in enumerate(data['conf']):
            if conf > 0:
                words.append(data['text'][i])
                confidences.append(conf / 100.0)
        
        if words:
            result["text"] = " ".join(words)
            result["confidence"] = sum(confidences) / len(confidences) if confidences else 0
            result["method_used"] = "tesseract"
            return result
    except Exception as e:
        result["error"] = (result.get("error", "") + f" | Tesseract: {str(e)}")

    # If all methods fail
    if not result["text"]:
        result["text"] = "Could not extract text from image."
        result["confidence"] = 0.0
    
    return result


def preprocess_math_ocr(ocr_text: str) -> str:
    """Clean and normalize OCR output for math problems."""
    text = ocr_text
    
    # Common OCR corrections for math
    corrections = {
        # Number/letter confusions
        r'\bO\b': '0',  # Capital O → zero in context
        r'l(?=\d)': '1',  # lowercase l before digit
        r'(?<=\d)l': '1',  # lowercase l after digit
        
        # Math notation fixes
        r'\^(\d)': r'^\1',  # Keep exponents
        r'sqrt\s*\(': '√(',
        r'pi\b': 'π',
        r'\btheta\b': 'θ',
        r'\balpha\b': 'α',
        r'\bbeta\b': 'β',
        r'\binfty\b': '∞',
        r'\bsum\b': 'Σ',
        
        # Fix common OCR artifacts
        r'\s+': ' ',  # Multiple spaces to single
        r'(?<=\d)\s+(?=\d)': '',  # Remove spaces between digits in same number
    }
    
    for pattern, replacement in corrections.items():
        try:
            text = re.sub(pattern, replacement, text)
        except:
            pass
    
    return text.strip()


# ─────────────────────────────────────────────
# AUDIO PROCESSING
# ─────────────────────────────────────────────
import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
def process_audio_asr(audio_bytes: bytes, audio_format: str = "mp3") -> Dict:
    """
    Convert audio to text using ASR.
    Returns: {text, confidence, method_used, error}
    """
    print("audio function is called ")
    result = {
        "text": "",
        "confidence": 0.0,
        "method_used": "none",
        "error": None
    }

    suffix = f".{audio_format}"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    try:

        # ---------- METHOD 1: Gemini ----------
        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")

            mime_type = f"audio/{audio_format}"
            audio_file = genai.upload_file(path=tmp_path)
            response = model.generate_content([
                audio_file,
                "Transcribe this audio. This is a JEE mathematics problem. Use proper math notation."
            ])

            result["text"] = response.text.strip()
            result["confidence"] = 0.86
            result["method_used"] = "gemini_audio"
            print(result)
            return result

        except Exception as e:
            result["error"] = f"Gemini ASR: {str(e)}"


        # ---------- METHOD 2: Local Whisper ----------
        try:
            import whisper

            model = whisper.load_model("base")

            transcription = model.transcribe(
                tmp_path,
                initial_prompt="JEE mathematics problem: "
            )

            result["text"] = transcription["text"].strip()
            result["confidence"] = 0.82
            result["method_used"] = "whisper_local"

            return result

        except Exception as e:
            result["error"] = (result.get("error", "") +
                               f" | Whisper Local: {str(e)}")

    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass

    return result

def preprocess_math_speech(transcript: str) -> str:
    """Convert speech-to-text output to proper math notation."""
    text = transcript
    
    # Math phrase conversions
    conversions = [
        # Powers
        (r'\bsquared?\b', '²'),
        (r'\bcubed?\b', '³'),
        (r'\braised to the power of (\w+)', r'^\1'),
        (r'\bto the (\w+) power\b', r'^\1'),
        (r'\bto the power (\w+)\b', r'^\1'),
        
        # Roots
        (r'\bsquare root of\b', '√'),
        (r'\bcube root of\b', '∛'),
        (r'\bsquare root\b', '√'),
        
        # Basic operations
        (r'\btimes\b', '×'),
        (r'\bdivided by\b', '÷'),
        (r'\bplus or minus\b', '±'),
        (r'\bgreater than or equal to\b', '≥'),
        (r'\bless than or equal to\b', '≤'),
        (r'\bnot equal to\b', '≠'),
        
        # Constants and symbols
        (r'\bpi\b', 'π'),
        (r'\btheta\b', 'θ'),
        (r'\binfinity\b', '∞'),
        (r'\balpha\b', 'α'),
        (r'\bbeta\b', 'β'),
        (r'\bdelta\b', 'δ'),
        
        # Functions
        (r'\bsin inverse\b', 'sin⁻¹'),
        (r'\bcos inverse\b', 'cos⁻¹'),
        (r'\btan inverse\b', 'tan⁻¹'),
        (r'\blog base (\w+)\b', r'log₍\1₎'),
        (r'\bnatural log of\b', 'ln'),
        
        # Fractions (rough)
        (r'\bone half\b', '1/2'),
        (r'\bone third\b', '1/3'),
        (r'\btwo thirds\b', '2/3'),
        (r'\bone fourth\b', '1/4'),
        (r'\bthree fourths\b', '3/4'),
    ]
    
    text_lower = text.lower()
    for pattern, replacement in conversions:
        text_lower = re.sub(pattern, replacement, text_lower, flags=re.IGNORECASE)
    
    return text_lower.strip()


# ─────────────────────────────────────────────
# MATH CALCULATOR TOOL
# ─────────────────────────────────────────────

def safe_evaluate(expression: str) -> Tuple[Optional[float], str]:
    """
    Safely evaluate a mathematical expression.
    Returns (result, error_message)
    """
    try:
        import sympy
        result = sympy.sympify(expression)
        if result.is_number:
            return float(result), ""
        return str(result), ""
    except Exception as e:
        pass
    
    # Fallback: very restricted eval
    try:
        import math
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
            "pi": math.pi, "e": math.e, "inf": math.inf,
            "factorial": math.factorial,
            "floor": math.floor, "ceil": math.ceil,
        }
        result = eval(expression, safe_dict)
        return result, ""
    except Exception as e:
        return None, str(e)
