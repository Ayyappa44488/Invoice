from flask import Flask, request, jsonify,render_template
from invoice import extract_invoice_data_from_pdf
app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html')
    
    
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['fileInput']
        f.save("invoice.pdf")
        data= extract_invoice_data_from_pdf("invoice.pdf")
        data= jsonify(data)
        return data
    
    
@app.route('/login')
def login():
    return render_template('login.html')
    
if __name__ == "__main__":
    app.run(debug=True)