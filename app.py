from flask import Flask, render_template, request, send_file, jsonify
from stego import encode_image, decode_image, get_image_capacity

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
