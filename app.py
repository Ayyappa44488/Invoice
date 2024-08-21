from flask import Flask, request, jsonify,render_template,session,redirect,url_for
from invoice import extract_invoice_data_from_pdf
import mysql.connector
app = Flask(__name__)
app.secret_key = "ayyappa"
conn = mysql.connector.connect(host="localhost",user="root",password="",database="invoice")
cursor=conn.cursor()


@app.route('/')
def index():
        return render_template('index.html')

    
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        print(request.files)
        f = request.files['fileInput']
        filename=f.filename
        f.save(r"static\uploads\{}".format(filename))
        data= extract_invoice_data_from_pdf(r"static\uploads\{}".format(filename))
        account_number = data["Account Number"] if data["Account Number"] is not None else "NULL"
        bank_name = data["Bank Name"] if data["Bank Name"] is not None else "NULL"
        bill_to_address = data["Bill to Address"] if data["Bill to Address"] is not None else "NULL"
        bill_to_name = data["Bill to Name"] if data["Bill to Name"] is not None else "NULL"
        department = data["Department"] if data["Department"] is not None else "NULL"
        employee_id = data["ID"] if data["ID"] is not None else "NULL"
        ifsc_code = data["IFSC Code"] if data["IFSC Code"] is not None else "NULL"
        invoice_date = data["Invoice Date"] if data["Invoice Date"] is not None else "NULL"
        invoice_number = data["Invoice Number"] if data["Invoice Number"] is not None else "NULL"
        subtotal = float(data["Subtotal"].replace("INR ", "").replace(",", "")) if data["Subtotal"] is not None else "NULL"
        tax = data["Tax"] if data["Tax"] is not None else "NULL"
        total_amount = float(data["Total Amount"].replace("INR ", "").replace(",", "")) if data["Total Amount"] is not None else "NULL"
        type=data["Type"]
        reviewed = 0
        check_query="select * from data where invoice_no = %s;"
        cursor.execute(check_query,(invoice_number,))
        if cursor.fetchone():
            return render_template('parse_invoice.html',message="Invoice Already Exists")
        else:
            query = """
                INSERT INTO data 
                (ac_no, bank_name, bill_to_address, bill_to_name, dept, id, 
                ifsc_code, invoice_date, invoice_no, subtotal, tax, total,reviewed,filename,type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
            """
            values = (account_number, bank_name, bill_to_address, bill_to_name, department, employee_id,
                    ifsc_code, invoice_date, invoice_number, subtotal, tax, total_amount,reviewed,filename,type)

            # Executing the query
            cursor.execute(query, values)
            conn.commit()
            return redirect(url_for('parse_invoice'))
    
    
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/validate', methods=['POST'])
def validate():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin@gmail.com' and password == 'admin@123':
            session['username'] = "admin"
            return redirect('/')
        elif username == 'checker@gmail.com' and password == 'checker@123':
            session['username'] = "checker"
            return redirect('/')
        return "Invalid Credentials"


@app.route('/parse_invoice')
def parse_invoice():
    return render_template('parse_invoice.html')


@app.route('/viewdata')
def viewdata():
    query="select * from data where reviewed = 0;"
    cursor.execute(query,)
    data=cursor.fetchall()
    return render_template('viewdata.html',data=data,url="edit_data",name="review")


@app.route('/edit_data/<string:id>')
def edit_data(id):
    query="select * from data where invoice_no = %s;"
    cursor.execute(query,(id,))
    data=cursor.fetchone()
    return render_template('edit_data.html',data=data,url="update_data",name="review")


@app.route('/update_data/<string:id>',methods=['POST'])
def update_data(id):
    if request.method == 'POST':
        account_number = request.form['ac_no']
        bank_name = request.form['bank_name']
        bill_to_address = request.form['bill_to_address']
        bill_to_name = request.form['bill_to_name']
        department = request.form['department']
        employee_id = request.form['emp_id']
        ifsc_code = request.form['ifsc_code']
        invoice_date = request.form['invoice_date']
        invoice_number = request.form['invoice_no']
        subtotal = request.form['subtotal']
        tax = request.form['tax']
        total_amount = request.form['total']
        reviewed=1
        type=request.form['type']
        query = """
            UPDATE data SET ac_no = %s, bank_name = %s, bill_to_address = %s, bill_to_name = %s, dept = %s, id = %s, 
            ifsc_code = %s, invoice_date = %s, invoice_no = %s, subtotal = %s, tax = %s, total = %s,reviewed = %s,type = %s WHERE invoice_no = %s
        """
        values = (account_number, bank_name, bill_to_address, bill_to_name, department, employee_id,
                ifsc_code, invoice_date, invoice_number, subtotal, tax, total_amount,reviewed,type,id)
        cursor.execute(query, values)
        conn.commit()
        return redirect(url_for('viewdata'))


@app.route("/admin_data")
def admin_data():
    query="select * from data where reviewed = 1;"
    cursor.execute(query,)
    data=cursor.fetchall()
    return render_template('viewdata.html',data=data,url="admin_view",name="view")


@app.route("/admin_view/<string:id>")
def admin_view(id):
    query="select * from data where reviewed = 1 and invoice_no=%s;"
    values=(id,)
    cursor.execute(query,values)
    data=cursor.fetchone()
    return render_template('admin_data.html',data=data)


@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
