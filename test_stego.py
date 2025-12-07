from stego import encode_image, decode_image, get_image_capacity
from PIL import Image
import io

def create_test_image():
    img = Image.new('RGB', (100, 100), color = 'blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_features():
    print("--- Testing Capacity ---")
    img_io = create_test_image()
    cap = get_image_capacity(img_io)
    print(f"Image Capacity: {cap} bytes")
    expected_cap = (100 * 100 * 3) // 8
    if cap == expected_cap:
        print("SUCCESS: Capacity calculation correct.")
    else:
        print(f"FAILURE: Expected {expected_cap}, got {cap}")

    print("\n--- Testing Encryption ---")
    img_io.seek(0)
    secret = "Top Secret Message"
    password = "supersecurepassword"
    
    print(f"Encoding '{secret}' with password '{password}'...")
    encoded_io = encode_image(img_io, secret, password)
    
    print("Decoding with correct password...")
    decoded = decode_image(encoded_io, password)
    if decoded == secret:
        print("SUCCESS: Decoded correctly.")
    else:
        print(f"FAILURE: Got '{decoded}'")
        
    print("Decoding with WRONG password...")
    try:
        decode_image(encoded_io, "wrongpass")
        print("FAILURE: Should have raised error.")
    except ValueError as e:
        print(f"SUCCESS: Caught expected error: {e}")
    except Exception as e:
        print(f"FAILURE: Caught unexpected error: {e}")

if __name__ == "__main__":
    test_features()
