from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret_key_here'

# --- JSON helper funksiyasi ---
def load_json(filepath, default={}):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump(default, f)
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# --- Login check decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Login sahifasi ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect(url_for('menu'))
    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- Menu sahifasi ---
@app.route('/menu')
@login_required
def menu():
    data = load_json('data/food_data.json')
    return render_template('menu.html', data=data)

# --- Product detail sahifasi ---
@app.route('/menu/<category>/<item_name>')
@login_required
def product_detail(category, item_name):
    data = load_json('data/food_data.json')
    likes = load_json('data/likes.json', {})
    comments = load_json('data/comments.json', {})
    item = None
    if category in data:
        for food in data[category]:
            if food['name'] == item_name:
                item = food
                break
    if item:
        return render_template('product_detail.html', item=item, category=category, likes=likes, comments=comments)
    else:
        return "Mahsulot topilmadi", 404

# --- Like bosish ---
@app.route('/like/<category>/<item_name>', methods=['POST'])
@login_required
def like_item(category, item_name):
    likes = load_json('data/likes.json', {})
    key = f"{category}:{item_name}"
    likes[key] = likes.get(key, 0) + 1
    save_json('data/likes.json', likes)
    flash("Like bosildi!")
    return redirect(url_for('product_detail', category=category, item_name=item_name))

# --- Izoh qoldirish ---
@app.route('/comment/<category>/<item_name>', methods=['POST'])
@login_required
def comment_item(category, item_name):
    comments = load_json('data/comments.json', {})
    key = f"{category}:{item_name}"
    comment = request.form['comment']
    if key not in comments:
        comments[key] = []
    comments[key].append(comment)
    save_json('data/comments.json', comments)
    flash("Izoh saqlandi!")
    return redirect(url_for('product_detail', category=category, item_name=item_name))

# --- Buyurtma yuborish ---
@app.route('/order/<category>/<item_name>', methods=['POST'])
@login_required
def submit_order(category, item_name):
    orders = load_json('data/orders.json', [])
    order = {
        'user': session['user'],
        'item': item_name,
        'category': category,
        'name': request.form['name'],
        'address': request.form['address'],
        'phone': request.form['phone']
    }
    orders.append(order)
    save_json('data/orders.json', orders)
    flash("Buyurtma muvaffaqiyatli yuborildi!")
    return redirect(url_for('product_detail', category=category, item_name=item_name))

if __name__ == '__main__':
    app.run(debug=True)
