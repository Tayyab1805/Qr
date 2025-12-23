from flask import Flask, render_template, request, jsonify, send_file
import qrcode
import io
import base64
from datetime import datetime
import os

app = Flask(__name__)

# Ensure uploads directory exists
os.makedirs('static/qrcodes', exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Please enter text or URL'}), 400
        
        # QR code settings
        version = int(data.get('version', 1))
        box_size = int(data.get('box_size', 10))
        border = int(data.get('border', 4))
        fill_color = data.get('fill_color', '#000000')
        back_color = data.get('back_color', '#ffffff')
        format_type = data.get('format', 'png')
        
        # Error correction level
        error_correction = data.get('error_correction', 'L')
        error_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        # Create QR code
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_map.get(error_correction, qrcode.constants.ERROR_CORRECT_L),
            box_size=box_size,
            border=border,
        )
        
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG' if format_type == 'png' else 'JPEG')
        img_bytes.seek(0)
        
        # Convert to base64 for display
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'qrcode_{timestamp}.{format_type}'
        
        # Save file
        filepath = f'static/qrcodes/{filename}'
        with open(filepath, 'wb') as f:
            f.write(img_bytes.getvalue())
        
        return jsonify({
            'success': True,
            'image': f'data:image/{format_type};base64,{img_base64}',
            'filename': filename,
            'download_url': f'/download/{filename}',
            'text': text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_qr(filename):
    try:
        return send_file(
            f'static/qrcodes/{filename}',
            as_attachment=True,
            download_name=filename
        )
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/wifi', methods=['POST'])
def generate_wifi_qr():
    try:
        data = request.json
        ssid = data.get('ssid', '').strip()
        password = data.get('password', '').strip()
        encryption = data.get('encryption', 'WPA')
        
        if not ssid:
            return jsonify({'error': 'Please enter WiFi SSID'}), 400
        
        # Format for WiFi QR code
        wifi_text = f'WIFI:T:{encryption};S:{ssid};P:{password};;'
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(wifi_text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color='#000000', back_color='#ffffff')
        
        # Convert to base64
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'wifi_qr_{timestamp}.png'
        filepath = f'static/qrcodes/{filename}'
        
        with open(filepath, 'wb') as f:
            f.write(img_bytes.getvalue())
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'filename': filename,
            'download_url': f'/download/{filename}',
            'wifi_text': wifi_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
