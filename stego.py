from PIL import Image
import io
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

ENC_TAG = "##ENC##"

def get_image_capacity(image_file):
    """Returns the maximum number of characters that can be hidden in the image."""
    try:
        image = Image.open(image_file)
        # 3 channels (RGB), 1 bit per channel. 8 bits per character.
        # Capacity in bytes = (pixels * 3) / 8
        total_pixels = image.size[0] * image.size[1]
        max_bytes = (total_pixels * 3) // 8
        return max_bytes
    except Exception as e:
        return 0

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_message(message, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(message.encode())
    # Return format: TAG + Base64(Salt) + : + Token
    return ENC_TAG + base64.b64encode(salt).decode() + ":" + token.decode()

def decrypt_message(encrypted_string, password):
    if not encrypted_string.startswith(ENC_TAG):
        # Not encrypted by us, or raw text
        return encrypted_string
    
    try:
        # Remove TAG
        content = encrypted_string[len(ENC_TAG):]
        salt_b64, token_str = content.split(":", 1)
        
        salt = base64.b64decode(salt_b64)
        key = derive_key(password, salt)
        f = Fernet(key)
        
        decrypted_data = f.decrypt(token_str.encode())
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError("Invalid password or corrupted data")

def genData(data):
    newd = []
    for i in data:
        newd.append(format(ord(i), '08b'))
    return newd

def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pix = [value for value in next(imdata)[:3] +
                                next(imdata)[:3] +
                                next(imdata)[:3]]

        for j in range(0, 8):
            if (datalist[i][j] == '0') and (pix[j] % 2 != 0):
                pix[j] -= 1
            elif (datalist[i][j] == '1') and (pix[j] % 2 == 0):
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if(pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

def encode_image(image_file, data, password=None):
    image = Image.open(image_file)
    newimg = image.copy()
    if newimg.mode != 'RGB':
        newimg = newimg.convert('RGB')
    
    if password:
        data = encrypt_message(data, password)
        
    encode_enc(newimg, data)
    
    img_byte_arr = io.BytesIO()
    newimg.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def decode_image(image_file, password=None):
    image = Image.open(image_file)
    data = ''
    imgdata = iter(image.getdata())

    while (True):
        pixels = [value for value in next(imgdata)[:3] +
                                next(imgdata)[:3] +
                                next(imgdata)[:3]]

        binstr = ''
        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            # End of message
            if password:
                return decrypt_message(data, password)
            elif data.startswith(ENC_TAG):
                 # It is encrypted but no password provided
                 raise ValueError("This message is encrypted. Please provide a password.")
            else:
                return data
