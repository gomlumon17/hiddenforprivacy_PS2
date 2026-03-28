import pytesseract
import cv2
import re

# --- WINDOWS ONLY ---
# If tesseract is not in your PATH, uncomment the line below and point to the .exe
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def scan_resin_code(image_frame):
    """
    Processes an image frame to find recycling resin codes (1-7).
    """
    try:
        # 1. Pre-processing for better OCR accuracy
        # Convert to grayscale
        gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast / Thresholding (makes text pop)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # 2. Run OCR
        # --psm 6: Assume a single uniform block of text
        # --oem 3: Default OCR engine mode
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray, config=custom_config)

        # 3. Use Regex to find numbers 1 through 7
        # This looks for a single digit between 1 and 7 in the text
        match = re.search(r'[1-7]', text)
        
        if match:
            return match.group(0)
        return None

    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def get_resin_info(code):
    """
    Maps the detected resin number to a recyclability message.
    """
    info = {
        "1": "PET (Highly Recyclable) - Bottles, Jars.",
        "2": "HDPE (Highly Recyclable) - Milk jugs, Detergent.",
        "3": "PVC (Hard to Recycle) - Pipes, Vinyl.",
        "4": "LDPE (Check local) - Plastic bags.",
        "5": "PP (Recyclable) - Yogurt cups, Caps.",
        "6": "PS (Hard to Recycle) - Styrofoam.",
        "7": "OTHER (Non-Recyclable) - Mixed plastics."
    }
    return info.get(code, "Unknown Code")