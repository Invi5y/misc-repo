from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, csv
from io import StringIO, BytesIO
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DB = 'store.db'

# --- Database setup ---
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    # Inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )''')
    # Purchases and items
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS purchase_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(purchase_id) REFERENCES purchases(id),
        FOREIGN KEY(item_id) REFERENCES inventory(id)
    )''')
    # Seed admin
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        pw = generate_password_hash('adminpass')
        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", ('admin', pw, 'admin'))
    conn.commit()
    conn.close()

init_db()

# --- Helpers ---
def get_db():
    return sqlite3.connect(DB)

def query_user(username):
    db = get_db(); c = db.cursor()
    c.execute("SELECT id,password,role FROM users WHERE username=?", (username,))
    u = c.fetchone(); db.close(); return u

def login_user(user):
    session['user_id'] = user[0]
    session['role'] = user[2]

def logout_user():
    session.clear()

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Access denied.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# --- Public routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Customer auth ---
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pw = generate_password_hash(request.form['password'])
        db = get_db(); c = db.cursor()
        try:
            c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", (username, pw, 'customer'))
            db.commit()
        except sqlite3.IntegrityError:
            flash('Username taken')
            db.close()
            return redirect(url_for('register'))
        db.close(); flash('Registered! Please log in.'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']; p = request.form['password']
        user = query_user(u)
        if user and user[2]=='customer' and check_password_hash(user[1], p):
            login_user(user); return redirect(url_for('shop'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user(); return redirect(url_for('index'))

# --- Manager auth ---
@app.route('/manager', methods=['GET','POST'])
def manager_login():
    if request.method=='POST':
        u = request.form['username']; p = request.form['password']
        user = query_user(u)
        if user and user[2] in ['admin','employee'] and check_password_hash(user[1], p):
            login_user(user); return redirect(url_for('manage_inventory'))
        flash('Invalid manager credentials')
    return render_template('manager_login.html')

# --- Customer routes ---
@app.route('/shop')
@login_required
@role_required('customer')
def shop():
    db = get_db(); c = db.cursor()
    c.execute("SELECT id,name,description,price,quantity FROM inventory")
    items = c.fetchall(); db.close()
    return render_template('shop.html', items=items)

@app.route('/cart', methods=['GET','POST'])
@login_required
@role_required('customer')
def cart():
    if 'cart' not in session: session['cart']={}
    cart = session['cart']; db = get_db(); c = db.cursor()
    if request.method=='POST':
        iid = request.form['item_id']; qty = int(request.form['quantity'])
        cart[iid] = cart.get(iid,0)+qty; session['cart']=cart
    cart_items=[]; total=0
    for iid,qty in cart.items():
        c.execute("SELECT name,price,quantity FROM inventory WHERE id=?",(iid,))
        row = c.fetchone()
        if row:
            name, price, avail = row; q=min(qty,avail); sub=q*price; total+=sub
            cart_items.append({'id':iid,'name':name,'price':price,'qty':q,'subtotal':sub})
    db.close(); return render_template('cart.html', cart=cart_items, total=total)

@app.route('/checkout', methods=['POST'])
@login_required
@role_required('customer')
def checkout():
    cart=session.get('cart',{});db=get_db();c=db.cursor();items=[];total=0
    for iid,qty in cart.items():
        c.execute("SELECT price,quantity FROM inventory WHERE id=?",(iid,))
        r=c.fetchone()
        if not r or qty>r[1]: flash('Insufficient stock'); db.close(); return redirect(url_for('cart'))
        total+=r[0]*qty; items.append((iid,qty,r[0]))
    ts=datetime.utcnow().isoformat(); c.execute("INSERT INTO purchases(user_id,timestamp,total) VALUES(?,?,?)",(session['user_id'],ts,total)); pid=c.lastrowid
    for iid,qty,price in items:
        c.execute("INSERT INTO purchase_items(purchase_id,item_id,quantity,price) VALUES(?,?,?,?)", (pid,iid,qty,price))
        c.execute("UPDATE inventory SET quantity=quantity-? WHERE id=?", (qty,iid))
    db.commit(); db.close(); session.pop('cart',None); return redirect(url_for('confirmation', purchase_id=pid))

@app.route('/confirmation/<int:purchase_id>')
@login_required
@role_required('customer')
def confirmation(purchase_id):
    return render_template('confirmation.html', purchase_id=purchase_id)

@app.route('/history')
@login_required
@role_required('customer')
def history():
    db=get_db();c=db.cursor();purchases=[]
    c.execute("SELECT id,timestamp,total FROM purchases WHERE user_id=?",(session['user_id'],))
    for pid,ts,tot in c.fetchall():
        c.execute(
            "SELECT i.name,i.description,pi.quantity,pi.price FROM purchase_items pi JOIN inventory i ON pi.item_id=i.id WHERE pi.purchase_id=?",
            (pid,)
        )
        entries=c.fetchall(); purchases.append({'id':pid,'timestamp':ts,'total':tot,'entries':entries})
    db.close(); return render_template('history.html', purchases=purchases)

@app.route('/history_csv')
@login_required
@role_required('customer')
def history_csv():
    db=get_db();c=db.cursor();rows=[]
    c.execute("SELECT id,timestamp FROM purchases WHERE user_id=?",(session['user_id'],))
    for pid,ts in c.fetchall():
        c.execute(
            "SELECT i.name,i.description,pi.quantity,pi.price FROM purchase_items pi JOIN inventory i ON pi.item_id=i.id WHERE pi.purchase_id=?",(pid,)
        )
        for name,desc,qty,price in c.fetchall(): rows.append([pid,ts,name,desc,qty,price,qty*price])
    db.close(); si=StringIO();w=csv.writer(si);w.writerow(['ID','Timestamp','Item','Desc','Qty','Price','Subtotal']);w.writerows(rows)
    b=BytesIO();b.write(si.getvalue().encode());b.seek(0);return send_file(b, as_attachment=True, download_name='history.csv', mimetype='text/csv')

# --- Manager routes ---
@app.route('/manage/users')
@login_required
@role_required('admin')
def manage_users():
    db=get_db();c=db.cursor();c.execute("SELECT id,username,role FROM users WHERE role!='customer'");users=c.fetchall();db.close()
    return render_template('users.html', users=users)

@app.route('/manage/users/add', methods=['GET','POST'])
@login_required
@role_required('admin')
def add_user():
    if request.method=='POST':
        username=request.form['username'];pw=generate_password_hash(request.form['password']);role=request.form['role']
        db=get_db();c=db.cursor()
        try:c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",(username,pw,role));db.commit()
        except sqlite3.IntegrityError:flash('Username taken')
        db.close();return redirect(url_for('manage_users'))
    return render_template('add_user.html')

@app.route('/manage/users/delete/<int:user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    if user_id==session['user_id']:flash('Cannot delete yourself')
    else:db=get_db();c=db.cursor();c.execute("DELETE FROM users WHERE id=?",(user_id,));db.commit();db.close()
    return redirect(url_for('manage_users'))

@app.route('/manage/inventory')
@login_required
@role_required('admin','employee')
def manage_inventory():
    db=get_db();c=db.cursor();c.execute("SELECT id,name,description,price,quantity FROM inventory");items=c.fetchall();db.close()
    return render_template('management.html', items=items)

@app.route('/manage/inventory/add', methods=['GET','POST'])
@login_required
@role_required('admin','employee')
def add_inventory():
    if request.method=='POST':
        name=request.form['item_name'];desc=request.form['description'];price=float(request.form['price']);qty=int(request.form['quantity'])
        db=get_db();c=db.cursor();c.execute("INSERT INTO inventory(name,description,price,quantity) VALUES(?,?,?,?)",(name,desc,price,qty));db.commit();db.close()
        return redirect(url_for('manage_inventory'))
    return render_template('add_item.html')

@app.route('/manage/inventory/delete/<int:item_id>')
@login_required
@role_required('admin','employee')
def delete_inventory(item_id):
    db=get_db();c=db.cursor();c.execute("DELETE FROM inventory WHERE id=?",(item_id,));db.commit();db.close()
    return redirect(url_for('manage_inventory'))

@app.route('/manage/inventory/download')
@login_required
@role_required('admin','employee')
def download_inventory():
    db=get_db();c=db.cursor();c.execute("SELECT name,description,price,quantity FROM inventory");data=c.fetchall();db.close()
    si=StringIO();w=csv.writer(si);w.writerow(['Name','Description','Price','Quantity']);w.writerows(data)
    b=BytesIO();b.write(si.getvalue().encode());b.seek(0);return send_file(b, as_attachment=True, download_name='inventory.csv', mimetype='text/csv')

if __name__=='__main__':
    app.run(debug=True)
