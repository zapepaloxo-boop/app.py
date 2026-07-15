from flask import Flask, render_template_string, request, send_file, redirect
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import re

app = Flask(__name__)

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพ
os.makedirs('bills', exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T&K Service Premium Creator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
        body { background-color: #f1f5f9; color: #334155; padding: 16px; }
        .app-bar { background: linear-gradient(135deg, #1e3a8a, #0f172a); color: white; text-align: center; padding: 20px; border-radius: 12px; margin-bottom: 20px; font-size: 20px; font-weight: bold; }
        .card { background: white; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }
        .card h2 { font-size: 16px; font-weight: bold; color: #0f172a; margin-bottom: 18px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }
        .form-group { margin-bottom: 14px; }
        .row { display: flex; gap: 15px; margin-bottom: 14px; }
        .col { flex: 1; }
        label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: bold; color: #475569; }
        input, select, textarea { width: 100%; padding: 11px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; color: #334155; background-color: #fff; }
        .btn { display: block; width: 100%; padding: 14px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; text-align: center; cursor: pointer; text-decoration: none; }
        .btn-primary { background-color: #2563eb; color: white; box-shadow: 0 4px 6px rgb(37 99 235 / 0.2); }
        .btn-primary:hover { background-color: #1d4ed8; }
        .btn-success { background-color: #059669; color: white; margin-top: 15px; box-shadow: 0 4px 6px rgb(5 150 105 / 0.2); }
        .receipt-box { text-align: center; background-color: #f8fafc; padding: 15px; border-radius: 12px; border: 2px dashed #cbd5e1; }
        .receipt-preview { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }
        .item-row { display: flex; gap: 10px; margin-bottom: 8px; }
        .item-name { flex: 3; }
        .item-price { flex: 1; }
        .success-message { background-color: #d1fae5; color: #065f46; padding: 12px; border-radius: 8px; margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="app-bar">T&K SYSTEMS BILL CREATOR</div>
    
    <div class="card">
        <h2>Bill Details</h2>
        <form action="/create_bill" method="POST">
            <div class="row">
                <div class="col">
                    <label>Customer Name *</label>
                    <input type="text" name="name" placeholder="Enter customer name" required>
                </div>
                <div class="col">
                    <label>Phone Number *</label>
                    <input type="text" name="phone" placeholder="Enter phone number" required>
                </div>
            </div>
            
            <div class="form-group">
                <label>Address</label>
                <input type="text" name="address" placeholder="Enter address">
            </div>

            <div class="row">
                <div class="col">
                    <label>Job Type</label>
                    <select name="job_type">
                        <option>Maintenance</option>
                        <option>IT / Electronics</option>
                        <option>Installation</option>
                        <option>Other Services</option>
                    </select>
                </div>
                <div class="col">
                    <label>Device Type</label>
                    <select name="device">
                        <option>Air Conditioner</option>
                        <option>Washing Machine</option>
                        <option>Television</option>
                        <option>Refrigerator</option>
                        <option>Water Heater</option>
                        <option>Electrical System</option>
                        <option>Other</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>Problem Description</label>
                <textarea name="symptom" rows="2" placeholder="Describe the problem"></textarea>
            </div>

            <h2 style="font-size:14px; margin-top:20px; color:#1e3a8a;">Items / Parts / Services</h2>
            <div class="form-group">
                <div class="item-row">
                    <input type="text" name="item1" class="item-name" placeholder="Item 1">
                    <input type="number" name="p1" class="item-price" placeholder="Price" value="0" step="0.01">
                </div>
                <div class="item-row">
                    <input type="text" name="item2" class="item-name" placeholder="Item 2">
                    <input type="number" name="p2" class="item-price" placeholder="Price" value="0" step="0.01">
                </div>
                <div class="item-row">
                    <input type="text" name="item3" class="item-name" placeholder="Item 3">
                    <input type="number" name="p3" class="item-price" placeholder="Price" value="0" step="0.01">
                </div>
            </div>

            <button type="submit" class="btn btn-primary">Generate Bill</button>
        </form>
    </div>
    
    <div class="card">
        <h2>Latest Bill</h2>
        <div class="receipt-box">
            {% if last_img %}
                <div class="success-message">Bill created successfully!</div>
                <img src="/get_image/{{ last_img }}" class="receipt-preview">
                <a href="/get_image/{{ last_img }}" download class="btn btn-success">Download Bill</a>
            {% else %}
                <p style="color: #94a3b8; font-size: 14px; padding: 40px 0;">Fill in the details above and click Generate Bill</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    last_img = request.args.get('last_img', None)
    return render_template_string(HTML_TEMPLATE, last_img=last_img)

@app.route('/create_bill', methods=['POST'])
def create_bill():
    try:
        name = request.form.get('name', 'N/A').strip()
        phone = request.form.get('phone', 'N/A').strip()
        address = request.form.get('address', '').strip()
        device = request.form.get('device', 'N/A').strip()
        job_type = request.form.get('job_type', 'N/A').strip()
        symptom = request.form.get('symptom', '').strip()
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        bill_id = datetime.now().strftime("%d%H%M%S")
        
        items = []
        total_price = 0.0
        for i in range(1, 4):
            item_text = request.form.get(f'item{i}', '').strip()
            item_p = request.form.get(f'p{i}', '0')
            try:
                p_val = float(item_p) if item_p else 0.0
            except (ValueError, TypeError):
                p_val = 0.0
            if item_text:
                items.append((item_text, p_val))
                total_price += p_val

        # Create image
        img = Image.new('RGB', (550, 1200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Load fonts - use default if system fonts not available
        try:
            font_bold = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 18)
            font_normal = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 14)
            font_small = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 12)
        except:
            try:
                font_bold = ImageFont.truetype("Arial.ttf", 18)
                font_normal = ImageFont.truetype("Arial.ttf", 14)
                font_small = ImageFont.truetype("Arial.ttf", 12)
            except:
                font_bold = font_normal = font_small = ImageFont.load_default()
        
        # Draw header
        draw.rectangle([(0, 0), (550, 60)], fill='#1E3A8A')
        draw.text((275, 30), "T&K ELECTRICAL SERVICE", fill='white', font=font_bold, anchor="mm")
        
        y = 80
        draw.text((40, y), "BILL / RECEIPT", fill='#0f172a', font=font_bold)
        y += 25
        
        draw.text((40, y), f"Bill ID: TK-{bill_id}", fill='#334155', font=font_normal)
        y += 20
        
        draw.text((40, y), f"Date: {current_date}", fill='#64748b', font=font_normal)
        y += 20
        
        draw.line([(40, y), (510, y)], fill='#cbd5e1', width=2)
        y += 15
        
        draw.text((40, y), f"Job Type: {job_type}", fill='#1e3a8a', font=font_bold)
        y += 20
        
        draw.text((40, y), f"Customer: {name}", fill='#334155', font=font_normal)
        y += 18
        
        draw.text((40, y), f"Phone: {phone}", fill='#334155', font=font_normal)
        y += 18
        
        if address:
            draw.text((40, y), f"Address: {address}", fill='#334155', font=font_normal)
            y += 18
        
        draw.text((40, y), f"Device: {device}", fill='#334155', font=font_normal)
        y += 18
        
        draw.text((40, y), f"Problem: {symptom if symptom else 'General checkup'}", fill='#334155', font=font_normal)
        y += 20
        
        draw.line([(40, y), (510, y)], fill='#cbd5e1', width=2)
        y += 15
        
        draw.text((40, y), "ITEMS / SERVICES", fill='#0f172a', font=font_bold)
        y += 22
        
        if not items:
            draw.text((40, y), "- General maintenance -", fill='#64748b', font=font_normal)
            y += 20
        else:
            for it_title, it_cost in items:
                draw.text((40, y), f"* {it_title}", fill='#334155', font=font_normal)
                draw.text((500, y), f"{it_cost:,.2f}", fill='#334155', font=font_normal, anchor="rm")
                y += 20
        
        draw.line([(40, y + 5), (510, y + 5)], fill='#1E3A8A', width=3)
        y += 20
        
        draw.text((40, y), "TOTAL", fill='#0f172a', font=font_bold)
        draw.text((500, y), f"{total_price:,.2f} THB", fill='#1E3A8A', font=font_bold, anchor="rm")
        y += 25
        
        draw.line([(40, y), (510, y)], fill='#cbd5e1', width=1)
        y += 15
        
        draw.text((40, y), "SERVICE TERMS", fill='#1e3a8a', font=font_bold)
        y += 18
        
        cond_lines = [
            "1. Warranty: 30 days from delivery",
            "2. Deposit: 50% for special parts",
            "3. Thank you for choosing T&K SERVICE"
        ]
        
        for line in cond_lines:
            draw.text((40, y), line, fill='#475569', font=font_small)
            y += 16
        
        # Save image
        filename = f"bill_TK{bill_id}.png"
        filepath = os.path.join('bills', filename)
        img.save(filepath)
        
        print(f"SUCCESS: Bill created: {filename}")
        return redirect(f"/?last_img={filename}")
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500

@app.route('/get_image/<filename>')
def get_image(filename):
    """Download bill image"""
    if not re.match(r'^bill_TK\d{8}\.png$', filename):
        return "Invalid file", 400
    
    try:
        filepath = os.path.join('bills', filename)
        if not os.path.abspath(filepath).startswith(os.path.abspath('bills')):
            return "Invalid file", 400
            
        return send_file(
            filepath,
            mimetype='image/png',
            as_attachment=False,
        )
    except FileNotFoundError:
        return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    print("Starting T&K SERVICE CREATOR")
    print("Open: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
