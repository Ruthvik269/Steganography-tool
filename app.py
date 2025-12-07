from flask import Flask, render_template, request, send_file, jsonify
from stego import encode_image, decode_image, get_image_capacity
import io
import base64
import qrcode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/capacity', methods=['POST'])
def capacity():
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image'}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        cap = get_image_capacity(image)
        return jsonify({'capacity': cap})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/encode', methods=['POST'])
def encode():
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Missing image or text'}), 400
    
    image = request.files['image']
    text = request.form['text']
    password = request.form.get('password') # Optional
    
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        encoded_img_io = encode_image(image, text, password)
        return send_file(encoded_img_io, mimetype='image/png', as_attachment=True, download_name='encoded_image.png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image'}), 400
    
    image = request.files['image']
    password = request.form.get('password') # Optional
    
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        decoded_text = decode_image(image, password)
        return jsonify({'text': decoded_text})
    except ValueError as ve:
        # Specific error for password issues
        return jsonify({'error': str(ve)}), 403
    except Exception as e:
        return jsonify({'error': 'Could not decode message. Ensure this image was encoded by this tool.'}), 500

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    """Generate QR code containing a shareable link or base64 image data"""
    try:
        data = request.json
        qr_content = data.get('content', '')
        
        if not qr_content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({'qr_code': f'data:image/png;base64,{qr_base64}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/encode-base64', methods=['POST'])
def encode_base64():
    """Encode image and return as base64 for sharing"""
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Missing image or text'}), 400
    
    image = request.files['image']
    text = request.form['text']
    password = request.form.get('password')
    
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        encoded_img_io = encode_image(image, text, password)
        img_base64 = base64.b64encode(encoded_img_io.getvalue()).decode()
        return jsonify({
            'image_base64': f'data:image/png;base64,{img_base64}',
            'filename': 'encoded_image.png'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-share-link', methods=['POST'])
def get_share_link():
    """Generate a shareable link (in production, this would use a file storage service)"""
    try:
        # For now, return the localhost URL
        # In production, upload to cloud storage and return the URL
        base_url = request.host_url
        share_url = f"{base_url}#shared"
        return jsonify({'share_link': share_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
