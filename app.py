import webbrowser
from flask import Flask, render_template, request, send_from_directory
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os
import io
import qrcode
from PIL import Image

app = Flask(__name__)

# Saving the PDFs
UPLOAD_FOLDER = 'receipts'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Generate the receipt
@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    client_name = request.form['client_name']
    staff_name = request.form['staff_name']
    items = request.form.getlist('items[]')
    quantities = request.form.getlist('quantities[]')
    rates = request.form.getlist('rates[]')

    # Date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime('%d/%m/%Y')
    time_str = current_datetime.strftime('%H:%M:%S')

    # PDF memory
    buffer = io.BytesIO()
    # Page size
    page_width = 80 / 25.4 * 72  
    page_height = 150 / 25.4 * 72  
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Font size 
    font_size = 8  
    c.setFont("Helvetica-Bold", font_size)

    # Title section
    c.drawString(10, page_height - 20, "LUCHEZ EATERY")
    c.setFont("Helvetica", font_size)
    c.drawString(10, page_height - 35, "4 Ways Village, Kiambu Rd, Nairobi")
    c.drawString(10, page_height - 50, "Tel: 0791922303")
    c.drawString(10, page_height - 65, "Email: lunchezeatery@gmail.com")
    c.drawString(10, page_height - 80, f"Client Name: {client_name}")
    c.drawString(10, page_height - 95, f"Staff Name: {staff_name}")
    c.drawString(10, page_height - 110, f"Date: {date_str}")
    c.drawString(10, page_height - 125, f"Time: {time_str}")
    

    # Header for items
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(10, page_height - 140, "Item")
    c.drawString(75, page_height - 140, "Qty")  
    c.drawString(115, page_height - 140, "Rate")  
    c.drawString(170, page_height - 140, "Amount")  

    # items
    y_position = page_height - 155
    total_amount = 0
    line_height = 10  
    for item, qty, rate in zip(items, quantities, rates):
        try:
            qty = int(qty)
            rate = float(rate)
            amount = qty * rate
            c.setFont("Helvetica", font_size)
            c.drawString(10, y_position, item)
            c.drawString(75, y_position, str(qty))  
            c.drawString(115, y_position, f"{rate:.2f}")  
            c.drawString(170, y_position, f"{amount:.2f}")  
            total_amount += amount
            y_position -= line_height

            
            if y_position < 40:
                c.showPage()  
                y_position = page_height - 20  
                c.setFont("Helvetica-Bold", font_size)
                c.drawString(10, y_position, "LUCHEZ EATERY")
                y_position += 20
                c.setFont("Helvetica", font_size)
                c.drawString(10, y_position, f"Client Name: {client_name}")
                y_position += 20
                c.drawString(10, y_position, f"Staff Name: {staff_name}")
                y_position += 20
                c.drawString(10, y_position, f"Date: {date_str}")
                y_position += 10
                c.drawString(10, y_position, f"Time: {time_str}")
                y_position += 10
                
                c.setFont("Helvetica-Bold", font_size)
                c.drawString(10, y_position, "Item")
                c.drawString(75, y_position, "Qty")  
                c.drawString(115, y_position, "Rate")  
                c.drawString(170, y_position, "Amount")  
                y_position += line_height

        except ValueError:
            return f"Invalid data for item: {item}. Quantity must be an integer and rate must be a float.", 400

    # Display total amount
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(10, y_position - 10, f"Total: {total_amount:.2f}")
    c.drawString(10, y_position - 25, "Thank you for dining with us!")

    #QR Code for company name
    qr_code_data = "LUCHEZ EATERY"
    qr_code = qrcode.make(qr_code_data)
    qr_code_path = "qrcode_temp.png"
    qr_code.save(qr_code_path)

    # QR code placing
    c.drawImage(qr_code_path, 10, y_position - 80, width=50, height=50) 

    # Remove the temporary QR code image
    os.remove(qr_code_path)

    # save the PDF
    pdf_filename = f"{client_name.replace(' ', '_')}_{current_datetime.strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    c.save()


    # Save the PDF 
    with open(pdf_path, 'wb') as f:
        f.write(buffer.getvalue())

    return f"Receipt generated! You can download it from <a href='/download/{pdf_filename}'>here</a>."
# Route for downloading the PDF
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__': 
    # Automatically open the default web browser to the Flask app
    webbrowser.open("http://127.0.0.1:5000/")
    
    # Run the Flask app  
    app.run(debug=True)
