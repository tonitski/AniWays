
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import uuid, re, os

app = Flask(__name__)

# Use a secret key from the environment.
# The fallback is only for local development.
app.secret_key = os.environ.get("SECRET_KEY") or "local-development-only-change-me"


PRODUCTS = []
SUBCATEGORIES = {}   # category -> [subcategory, ...] in display order


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def add(cat, sub, name, price, emoji, desc, options):
    """Add a product. Its image file is static/images/<id>.jpg (id = slug of the name)."""
    pid = slug(name)
    if any(p['id'] == pid for p in PRODUCTS):
        pid = slug(sub + ' ' + name)
    PRODUCTS.append({'id': pid, 'name': name, 'category': cat, 'subcategory': sub, 'price': price,
                     'emoji': emoji, 'description': desc, 'options': options, 'image': pid + '.jpg'})
    SUBCATEGORIES.setdefault(cat, [])
    if sub not in SUBCATEGORIES[cat]:
        SUBCATEGORIES[cat].append(sub)


# ---------------- APPAREL ----------------
SIZES = ['S', 'M', 'L', 'XL', 'XXL']
for n, pr in [('Plain Long-Sleeve Shirt', 299), ('Breathable Quick-Dry Shirt', 349), ('Sun-Protection Shirt', 379),
              ('Camouflage Long-Sleeve Shirt', 349), ('Farm-Themed Graphic Shirt', 329), ('Minimalist Long-Sleeve Shirt', 299),
              ('Reflective Work Shirt', 399), ('Hooded Long-Sleeve Shirt', 389), ('Long-Sleeve Shirt with Face Cover', 369),
              ('Lightweight Outdoor Work Shirt', 319)]:
    add('Apparel', 'Shirts', n, pr, '👕', 'Long-sleeve shirt for outdoor farm work. Choose a color and size.',
        {'Color': ['Green', 'Navy', 'Brown', 'Black'], 'Size': SIZES})

for n, pr in [('Cargo Work Pants', 349), ('Waterproof Pants', 449), ('Quick-Dry Pants', 359), ('Reinforced Work Pants', 399),
              ('Stretchable Farm Pants', 379), ('Camouflage Pants', 369), ('Lightweight Outdoor Trousers', 339),
              ('Heavy-Duty Utility Pants', 429)]:
    add('Apparel', 'Pants', n, pr, '👖', 'Comfortable, durable pants for work in the field.',
        {'Color': ['Khaki', 'Green', 'Black', 'Navy'], 'Size': SIZES})

BOOT_SIZES = [str(i) for i in range(36, 45)]
for n, pr in [('Rubber Farm Boots', 499), ('Knee-High Boots', 549), ('Waterproof Work Boots', 599), ('Safety Boots', 699),
              ('Lightweight Outdoor Shoes', 449), ('Slip-Resistant Boots', 579)]:
    add('Apparel', 'Boots & Shoes', n, pr, '🥾', 'Footwear for muddy paths and wet fields.',
        {'Color': ['Black', 'Green', 'Brown'], 'Size': BOOT_SIZES})

for n, pr in [('Rubber Gloves', 99), ('Gardening Gloves', 129), ('Cut-Resistant Work Gloves', 199), ('Waterproof Gloves', 159),
              ('Heavy-Duty Farm Gloves', 189), ('Coated Grip Gloves', 149)]:
    add('Apparel', 'Gloves', n, pr, '🧤', 'Protective gloves for planting and everyday farm work.',
        {'Size': ['S', 'M', 'L', 'XL']})

for n, pr in [('Baseball Cap', 129), ('Wide-Brim Sun Hat', 149), ('Bucket Hat', 139), ('Neck-Flap Sun Hat', 159),
              ('Hat with Face Cover', 169), ('Breathable Outdoor Hat', 139), ('Waterproof Hat', 159)]:
    add('Apparel', 'Caps & Hats', n, pr, '🧢', 'Shade and sun protection while working outdoors.',
        {'Color': ['Green', 'Brown', 'Black', 'Beige']})

for n, pr in [('Raincoat', 399), ('Two-Piece Rain Suit', 549), ('Waterproof Jacket', 499), ('Reflective Raincoat', 549),
              ('Poncho', 199), ('Face-Covering Outdoor Jacket', 529)]:
    add('Apparel', 'Rainwear & Jackets', n, pr, '🧥', 'Rain protection for field work.',
        {'Color': ['Green', 'Yellow', 'Navy'], 'Size': SIZES})

for n, pr in [('Protective Coveralls', 599), ('High-Visibility Workwear', 449), ('Sun-Protection Arm Sleeves', 99)]:
    add('Apparel', 'Protective Wear', n, pr, '🦺', 'Protective workwear for safer farm work.',
        {'Color': ['Green', 'Orange', 'Navy', 'Black'], 'Size': SIZES})

# ---------------- SEEDS ----------------
SEED_OPT = {'Pack Size': ['Small Pack', 'Family Pack', 'Farm Pack']}
SEED_DESC = 'Seeds for home gardens and farms. Check packet variety and expiry details.'
for n in ['Eggplant', 'Ladyfinger (Okra)', 'Tomato', 'Beans', 'Chili', 'Squash', 'Carrot', 'Cabbage', 'Pechay', 'Ampalaya',
          'Cucumber', 'Lettuce', 'Onion', 'Radish', 'Mustard Greens']:
    add('Seeds', 'Vegetable Seeds', n + ' Seeds', 45, '🌱', SEED_DESC, SEED_OPT)
add('Seeds', 'Vegetable Seeds', 'Mixed Vegetable Seeds', 69, '🌱', SEED_DESC, SEED_OPT)
for n in ['Corn', 'Rice', 'Watermelon', 'Melon']:
    add('Seeds', 'Grain & Fruit Seeds', n + ' Seeds', 59, '🌾', SEED_DESC, SEED_OPT)

# ---------------- FERTILIZER & CROP CARE ----------------
FERT_DESC = 'Farm crop-care product listing. Read the official label, verify local registration, and follow safety instructions.'
FERT_OPT = {'Pack Size': ['Small', 'Medium', 'Large']}
for cat_sub, items in [
    ('Liquid Fertilizer', [('Fruit Fertilizer Juice', 199), ('Plant Fertilizer Juice', 179), ('Fish Fertilizer Juice', 219),
                           ('Organic Liquid Fertilizer', 229)]),
    ('Chemical Fertilizer', [('Urea 46-0-0', 399), ('Complete Fertilizer 14-14-14', 429), ('Ammonium Sulfate', 359),
                             ('Muriate of Potash', 449), ('Ammonium Phosphate', 459), ('Rice-Specific Fertilizer', 429)]),
    ('Organic & Soil', [('Vermicast', 249), ('Compost Fertilizer', 199), ('Soil Conditioner', 279)]),
    ('Crop Protection', [('Virtako Insecticide', 299), ('Nativo Fungicide', 289), ('2,4-D Herbicide', 259),
                         ('Frontier Herbicide', 329), ('Surekill Molluscicide', 189)]),
]:
    for n, pr in items:
        add('Fertilizer & Crop Care', cat_sub, n, pr, '🧴', FERT_DESC, FERT_OPT)

# ---------------- FARM SNACKS ----------------
SNACK_OPT = {'Flavor': ['Original', 'BBQ', 'Sour Cream', 'Chilli', 'Cheese'], 'Pack Size': ['Small', 'Regular', 'Family Pack']}
for n, pr in [('Banana Chips', 79), ('Taro Chips', 89), ('Kangkong Chips', 69), ('Ampalaya Chips', 79), ('Kamote Chips', 75),
              ('Jackfruit Chips', 99), ('Cassava Chips', 69), ('Ube Chips', 95), ('Mushroom Chips', 99), ('Coconut Chips', 89)]:
    add('Farm Snacks', 'Chips', n, pr, '🍌', 'Crunchy Filipino snack. Choose a flavor and pack size.', SNACK_OPT)
for n, pr in [('Dried Mangoes', 119), ('Dried Pineapple', 99)]:
    add('Farm Snacks', 'Dried Fruit', n, pr, '🥭', 'Sweet dried Filipino fruit. Choose a pack size.',
        {'Pack Size': ['Small', 'Regular', 'Family Pack']})

# ---------------- FARM EQUIPMENT ----------------
TYPE = {'Type': ['Standard', 'Heavy Duty']}
D = 'Useful tool for gardening and farm work.'
for sub, items in [
    ('Sprayers', [('Knapsack Sprayer', 899), ('Electric Sprayer', 1799), ('Hand Sprayer', 399), ('Sprayer Replacement Parts', 149),
                  ('Nozzles and Hoses', 199)]),
    ('Hand Tools', [('Garden Trowel', 99), ('Spade', 299), ('Sickle', 149), ('Pitchfork', 349), ('Shovel', 279), ('Hoe', 229),
                    ('Gardening Fork', 129), ('Rake', 249), ('Bolo', 299), ('Pruning Shears', 199), ('Grass Cutter', 2499),
                    ('Wheelbarrow', 1499)]),
    ('Water & Irrigation', [('Watering Can', 179), ('Garden Hose', 499), ('Water Pump', 2999), ('Irrigation Pipes', 349),
                            ('Drip Irrigation Kit', 899)]),
    ('Planting & Harvest', [('Seedling Tray', 89), ('Plant Pots', 79), ('Harvesting Basket', 159), ('Rice Harvesting Tools', 349),
                            ('Grain Tarpaulin', 599), ('Harvesting Sacks', 129), ('Farm Tool Storage Box', 699)]),
    ('Measuring Tools', [('Measuring Tape', 99), ('Soil pH Meter', 499), ('Portable Weighing Scale', 799)]),
    ('Safety Gear', [('Protective Goggles', 149), ('Respirator', 349), ('Safety Helmet', 299), ('Ear Protection', 199)]),
]:
    for n, pr in items:
        add('Farm Equipment', sub, n, pr, '🛠️', D, TYPE)

CATEGORIES = ['All', 'Apparel', 'Seeds', 'Fertilizer & Crop Care', 'Farm Snacks', 'Farm Equipment']


def get_product(pid): return next((p for p in PRODUCTS if p['id'] == pid), None)


def get_cart():
    result = []; total = 0
    for entry in session.get('cart', []):
        p = get_product(entry['id'])
        if p:
            qty = max(1, int(entry.get('qty', 1))); line = p['price'] * qty; total += line
            result.append({'product': p, 'qty': qty, 'options': entry.get('options', {}), 'line': line})
    return result, total


@app.context_processor
def globals_for_templates():
    items, _ = get_cart()
    return {'cart_count': sum(x['qty'] for x in items), 'categories': CATEGORIES}


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            flash('Please create an account or log in first.', 'warning'); return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


@app.route('/')
def home(): return render_template('home.html', products=PRODUCTS[:8])


@app.route('/shop')
def shop():
    category = request.args.get('category', 'All')
    sub = request.args.get('type', 'All')
    q = request.args.get('q', '').lower().strip()
    products = PRODUCTS
    if category != 'All': products = [p for p in products if p['category'] == category]
    subs = SUBCATEGORIES.get(category, [])
    if sub not in subs: sub = 'All'
    if sub != 'All': products = [p for p in products if p['subcategory'] == sub]
    if q: products = [p for p in products if q in p['name'].lower() or q in p['description'].lower()]
    return render_template('shop.html', products=products, selected_category=category, selected_sub=sub,
                           subcategories=subs, q=q)


@app.route('/product/<pid>')
def product(pid):
    p = get_product(pid)
    if not p: return 'Product not found', 404
    return render_template('product.html', p=p)


@app.post('/add-to-cart')
def add_to_cart():
    p = get_product(request.form.get('product_id'))
    if not p: flash('Product not found.', 'danger'); return redirect(url_for('shop'))
    try: qty = max(1, int(request.form.get('qty', 1)))
    except ValueError: qty = 1
    options = {k[7:]: v for k, v in request.form.items() if k.startswith('option_') and v}
    cart = session.get('cart', []); found = next((x for x in cart if x['id'] == p['id'] and x.get('options', {}) == options), None)
    if found: found['qty'] += qty
    else: cart.append({'id': p['id'], 'qty': qty, 'options': options})
    session['cart'] = cart; flash(f"{p['name']} added to Ani!", 'success')
    return redirect(request.referrer or url_for('shop'))


@app.route('/cart')
def cart():
    items, total = get_cart(); return render_template('cart.html', items=items, total=total)


@app.post('/remove-cart')
def remove_cart():
    pid = request.form.get('product_id'); session['cart'] = [x for x in session.get('cart', []) if x['id'] != pid]; return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items, total = get_cart()
    if not items: flash('Your Ani is empty. Add products first.', 'warning'); return redirect(url_for('shop'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip(); phone = request.form.get('phone', '').strip(); address = request.form.get('address', '').strip(); payment = request.form.get('payment', 'COD')
        if not name or not phone or not address: flash('Complete all delivery details.', 'danger'); return redirect(url_for('checkout'))
        order = {'id': 'ANI-' + uuid.uuid4().hex[:8].upper(), 'created': datetime.now().strftime('%b %d, %Y %I:%M %p'), 'name': name, 'phone': phone, 'address': address, 'payment': payment, 'items': items, 'total': total, 'status': 'Processing', 'timeline': ['Processing'], 'notification': 'Order received and is being prepared.'}
        orders = session.get('orders', []); orders.insert(0, order); session['orders'] = orders; session['cart'] = []
        flash('Order placed. This is a simulated payment; no money was charged.', 'success'); return redirect(url_for('order_detail', order_id=order['id']))
    return render_template('checkout.html', items=items, total=total)


@app.route('/orders')
@login_required
def orders(): return render_template('orders.html', orders=session.get('orders', []))


@app.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    o = next((x for x in session.get('orders', []) if x['id'] == order_id), None)
    if not o: return 'Order not found in this browser session.', 404
    return render_template('order.html', order=o)


@app.route('/notifications')
@login_required
def notifications(): return render_template('notifications.html', orders=session.get('orders', []))


@app.route('/about')
def about(): return render_template('about.html')


@app.route('/contact')
def contact(): return render_template('contact.html')


@app.route('/anisays')
def anisays(): return render_template('anisays.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip(); email = request.form.get('email', '').strip().lower(); password = request.form.get('password', '')
        if not name or not email or len(password) < 6: flash('Enter your name, email, and a password of at least 6 characters.', 'danger'); return redirect(url_for('signup'))
        users = session.get('demo_users', {})
        if email in users: flash('Account already exists in this demo session. Log in instead.', 'warning'); return redirect(url_for('login'))
        users[email] = {'name': name, 'password': password}; session['demo_users'] = users; session['user'] = {'name': name, 'email': email}; flash('Demo account created!', 'success'); return redirect(url_for('home'))
    return render_template('login.html', mode='signup')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower(); password = request.form.get('password', ''); users = session.get('demo_users', {})
        if email in users and users[email]['password'] == password:
            session['user'] = {'name': users[email]['name'], 'email': email}; flash('Welcome back!', 'success'); return redirect(url_for('home'))
        flash('Demo login failed. Create an account first in this browser session.', 'warning')
    return render_template('login.html', mode='login')


@app.route('/logout')
def logout(): session.pop('user', None); flash('You have logged out.', 'success'); return redirect(url_for('home'))


@app.route('/admin')
def admin(): return render_template('admin.html', orders=session.get('orders', []))


@app.post('/admin/update-status')
def update_status():
    oid = request.form.get('order_id'); status = request.form.get('status'); allowed = ['Processing', 'Shipped', 'Out for Delivery', 'Delivered']
    if status not in allowed: flash('Invalid status.', 'danger'); return redirect(url_for('admin'))
    orders = session.get('orders', []); order = next((x for x in orders if x['id'] == oid), None)
    if order:
        order['status'] = status
        if status not in order['timeline']: order['timeline'].append(status)
        order['notification'] = f'Order {oid} status updated to {status}.'; session['orders'] = orders; flash('Order status updated.', 'success')
    else: flash('Order not found in this session.', 'warning')
    return redirect(url_for('admin'))


if __name__ == '__main__': app.run(debug=True)
