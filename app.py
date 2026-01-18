from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
import time
from datetime import datetime, timedelta
import secrets
from functools import wraps
import stripe
import easypost
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for session

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Create the database directory if it doesn't exist



# Initialize Stripe with your secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Initialize EasyPost client
easypost_client = easypost.EasyPostClient(os.getenv('EASYPOST_API_KEY'))

# Mock database for saved addresses
SAVED_ADDRESSES = {}

# Admin credentials (in production, these should be stored securely)
ADMIN_USERNAME = "user"
ADMIN_PASSWORD = "12345678"
# Session lifetime in seconds (30 minutes)
SESSION_LIFETIME = 1800
# Management page access token
MANAGEMENT_TOKEN = secrets.token_hex(16)

# Load jersey data from JSON file or create empty list if file doesn't exist
def load_jerseys():
    if os.path.exists('jerseys.json'):
        with open('jerseys.json', 'r') as f:
            return json.load(f)
    return []

# Save jersey data to JSON file
def save_jerseys(jerseys):
    with open('jerseys.json', 'w') as f:
        json.dump(jerseys, f, indent=4)

# Enhanced login required decorator with extra security
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login', next=request.url))
        
        # Check if session has expired
        if 'last_activity' not in session or time.time() - session['last_activity'] > SESSION_LIFETIME:
            session.pop('logged_in', None)
            session.pop('username', None)
            session.pop('last_activity', None)
            session.pop('admin_verified', None)
            session.pop('management_token', None)
            flash('Your session has expired. Please log in again.', 'error')
            return redirect(url_for('login', next=request.url))
        
        # Update last activity time
        session['last_activity'] = time.time()
        
        # Validate management token for admin pages (extra protection)
        if request.endpoint in ['manage', 'add_jersey', 'update_priority', 'delete_jersey']:
            if 'management_token' not in session or session['management_token'] != MANAGEMENT_TOKEN or 'admin_verified' not in session:
                session.pop('logged_in', None)
                session.pop('username', None)
                session.pop('last_activity', None)
                session.pop('admin_verified', None)
                session.pop('management_token', None)
                flash('Unauthorized access. Please log in again.', 'error')
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# Create initial data if not exists
if not os.path.exists('jerseys.json'):
    initial_jerseys = [
        {
            "id": 1,
            "name": "Real Madrid Home Jersey 2023/24",
            "image": "static/images/madrid_home.jpg",
            "price": 89.99,
            "seller": "Official Store",
            "seller_rating": 5,
            "description": "Official Real Madrid home jersey for the 2023/24 season.",
            "date_added": "2023-08-01",
            "details": "100% polyester, breathable material, club crest embroidered.",
            "priority": 3
        },
        {
            "id": 2,
            "name": "Barcelona Away Jersey 2023/24",
            "image": "static/images/barca_away.jpg",
            "price": 79.99,
            "seller": "Football Shop",
            "seller_rating": 4.8,
            "description": "Official FC Barcelona away jersey for the 2023/24 season.",
            "date_added": "2023-08-05",
            "details": "Lightweight material, breathable design, club logo.",
            "priority": 2
        },
        {
            "id": 3,
            "name": "Manchester United Third Kit 2023/24",
            "image": "static/images/mu_third.jpg",
            "price": 94.99,
            "seller": "United Megastore",
            "seller_rating": 4.9,
            "description": "Official Manchester United third kit for the 2023/24 season.",
            "date_added": "2023-08-10",
            "details": "Authentic player version, premium quality, club emblem.",
            "priority": 1
        },
        {
            "id": 4,
            "name": "Liverpool Home Jersey 2023/24",
            "image": "static/images/liverpool_home.jpg",
            "price": 84.99,
            "seller": "LFC Shop",
            "seller_rating": 4.7,
            "description": "Official Liverpool FC home jersey for the 2023/24 season.",
            "date_added": "2023-07-25",
            "details": "Standard fit, durable material, club crest.",
            "priority": 2
        },
        {
            "id": 5,
            "name": "Bayern Munich Home Jersey 2023/24",
            "image": "static/images/bayern_home.jpg",
            "price": 89.99,
            "seller": "Bayern Store",
            "seller_rating": 4.9,
            "description": "Official Bayern Munich home jersey for the 2023/24 season.",
            "date_added": "2023-07-15",
            "details": "Authentic version, premium fabric, club logo.",
            "priority": 1
        }
    ]
    save_jerseys(initial_jerseys)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sell')
def sell():
    sort_by = request.args.get('sort', 'date')  # Default sort by date
    search = request.args.get('search', '')
    
    jerseys = load_jerseys()
    
    # Filter by search term
    if search:
        jerseys = [j for j in jerseys if search.lower() in j['name'].lower() or 
                   search.lower() in j['description'].lower()]
    
    # Sort jerseys
    if sort_by == 'price_low':
        jerseys = sorted(jerseys, key=lambda x: x['price'])
    elif sort_by == 'price_high':
        jerseys = sorted(jerseys, key=lambda x: x['price'], reverse=True)
    elif sort_by == 'seller':
        jerseys = sorted(jerseys, key=lambda x: x['seller_rating'], reverse=True)
    elif sort_by == 'priority':
        jerseys = sorted(jerseys, key=lambda x: x['priority'])
    else:  # sort by date (default)
        jerseys = sorted(jerseys, key=lambda x: x['date_added'], reverse=True)
    
    return render_template('sell.html', jerseys=jerseys, sort_by=sort_by, search=search)

@app.route('/jersey/<int:jersey_id>')
def jersey_detail(jersey_id):
    jerseys = load_jerseys()
    jersey = next((j for j in jerseys if j['id'] == jersey_id), None)
    
    if jersey:
        return render_template('jersey_detail.html', jersey=jersey)
    return "Jersey not found", 404

@app.route('/auction')
def auction():
    return render_template('auction.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Set session variables for authenticated user
            session['logged_in'] = True
            session['username'] = username
            session['last_activity'] = time.time()
            session['admin_verified'] = True
            session['management_token'] = MANAGEMENT_TOKEN
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            # Redirect to admin verification page before granting access to manage
            return redirect(url_for('admin_verify'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

# Admin verification route - additional protection layer
@app.route('/admin_verify', methods=['GET', 'POST'])
def admin_verify():
    # Only allow access if already logged in
    if 'logged_in' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        verify_password = request.form.get('verify_password')
        
        if verify_password == ADMIN_PASSWORD:
            # Grant access to the management page
            session['admin_verified'] = True
            flash('Admin verification successful', 'success')
            return redirect(url_for('manage'))
        else:
            flash('Verification failed. Incorrect password.', 'error')
    
    return render_template('admin_verify.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('last_activity', None)
    session.pop('admin_verified', None)
    session.pop('management_token', None)
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

# Management interface
@app.route('/manage')
@login_required
def manage():
    jerseys = load_jerseys()
    # Sort jerseys by ID for management
    jerseys = sorted(jerseys, key=lambda x: x['id'])
    return render_template('manage.html', jerseys=jerseys)

# Add new jersey
@app.route('/add_jersey', methods=['POST'])
@login_required
def add_jersey():
    # Verify password again for sensitive operations
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        flash('Invalid password', 'error')
        return redirect(url_for('manage'))
    
    # Get jersey data from form
    jerseys = load_jerseys()
    new_id = max([j['id'] for j in jerseys], default=0) + 1
    
    name = request.form.get('name')
    price = float(request.form.get('price'))
    seller = request.form.get('seller')
    seller_rating = float(request.form.get('seller_rating'))
    description = request.form.get('description')
    details = request.form.get('details')
    priority = int(request.form.get('priority'))
    
    # Handle image upload
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        # Create a unique filename
        filename = f"jersey_{new_id}_{image_file.filename}"
        image_path = os.path.join('static/images', filename)
        image_file.save(image_path)
    else:
        # Default image if none provided
        image_path = 'static/images/default_jersey.jpg'
    
    # Create new jersey entry
    new_jersey = {
        "id": new_id,
        "name": name,
        "image": image_path,
        "price": price,
        "seller": seller,
        "seller_rating": seller_rating,
        "description": description,
        "date_added": datetime.now().strftime("%Y-%m-%d"),
        "details": details,
        "priority": priority
    }
    
    jerseys.append(new_jersey)
    save_jerseys(jerseys)
    
    flash('Jersey added successfully', 'success')
    return redirect(url_for('manage'))

# Update jersey priority
@app.route('/update_priority/<int:jersey_id>', methods=['POST'])
@login_required
def update_priority(jersey_id):
    # Verify password again
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        flash('Invalid password', 'error')
        return redirect(url_for('manage'))
    
    priority = int(request.form.get('priority'))
    jerseys = load_jerseys()
    
    # Find the jersey and update its priority
    for jersey in jerseys:
        if jersey['id'] == jersey_id:
            jersey['priority'] = priority
            break
    
    save_jerseys(jerseys)
    flash('Priority updated successfully', 'success')
    return redirect(url_for('manage'))

# Delete jersey
@app.route('/delete_jersey/<int:jersey_id>', methods=['POST'])
@login_required
def delete_jersey(jersey_id):
    # Verify password again
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        flash('Invalid password', 'error')
        return redirect(url_for('manage'))
    
    jerseys = load_jerseys()
    
    # Find the jersey to delete
    jersey_to_delete = next((j for j in jerseys if j['id'] == jersey_id), None)
    if jersey_to_delete:
        # Remove the image file if it exists and isn't a default
        image_path = jersey_to_delete['image']
        if image_path != 'static/images/default_jersey.jpg' and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass  # Ignore errors in deleting file
                
        # Remove the jersey from the list
        jerseys = [j for j in jerseys if j['id'] != jersey_id]
        save_jerseys(jerseys)
        flash('Jersey deleted successfully', 'success')
    
    return redirect(url_for('manage'))

@app.route('/payment/<int:jersey_id>')
def payment(jersey_id):
    """Render the payment page with Stripe publishable key."""
    # Verify the jersey exists
    jerseys = load_jerseys()
    jersey = next((j for j in jerseys if j['id'] == jersey_id), None)
    
    if not jersey:
        flash('Jersey not found', 'error')
        return redirect(url_for('sell'))
        
    return render_template('payment.html', 
                         stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'),
                         jersey=jersey)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a PaymentIntent for the specified payment method."""
    try:
        data = request.json
        amount = data.get('amount', 1000)  # Default to $10.00
        payment_method = data.get('payment_method', 'card')

        # Configure payment method options
        payment_method_types = ['card']
        payment_method_options = {}

        # Add Alipay if selected
        if payment_method == 'alipay':
            payment_method_types = ['alipay']

        # Add WeChat Pay if selected
        elif payment_method == 'wechat_pay':
            payment_method_types = ['wechat_pay']
            payment_method_options = {
                'wechat_pay': {
                    'client': 'web'
                }
            }

        # Create a PaymentIntent with the specified configuration
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method_types=payment_method_types,
            payment_method_options=payment_method_options
        )

        return jsonify({
            'clientSecret': intent.client_secret
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/create-payment-session', methods=['POST'])
def create_payment_session():
    """Create a payment session with shipping and address information."""
    try:
        data = request.json
        jerseys = load_jerseys()
        jersey_id = data.get('jersey_id')
        jersey = next((j for j in jerseys if str(j['id']) == str(jersey_id)), None)
        
        if not jersey:
            raise ValueError('Jersey not found')
            
        shipping_rate = data.get('shipping_rate')
        if not shipping_rate:
            raise ValueError('Shipping rate not selected')
            
        # Save address for logged-in users
        if 'logged_in' in session:
            username = session['username']
            if username not in SAVED_ADDRESSES:
                SAVED_ADDRESSES[username] = []
            
            # Create address object
            address = {
                'name': data['name'],
                'street': data['street'],
                'city': data['city'],
                'state': data['state'],
                'zip': data['zip'],
                'country': data['country'],
                'email': data['email'],
                'phone': data['phone']
            }
            
            # Add address if it doesn't exist
            if address not in SAVED_ADDRESSES[username]:
                SAVED_ADDRESSES[username].append(address)
        
        # Calculate total amount including shipping
        shipping_cost = float(shipping_rate.get('rate', 0))
        total_amount = int((jersey['price'] + shipping_cost) * 100)  # Convert to cents
        
        # Format shipping address
        shipping_address = f"{data['name']}, {data['street']}, {data['city']}, {data['state']} {data['zip']}, {data['country']}"
        shipping_method = f"{shipping_rate.get('carrier')} {shipping_rate.get('service')}"

        # Store order details in session for confirmation page
        session['order_details'] = {
            'jersey_name': jersey['name'],
            'amount': total_amount,
            'shipping_method': shipping_method,
            'shipping_address': shipping_address,
            'email': data['email'],
            'jersey_id': jersey_id  # Add jersey_id to session
        }

        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',
            metadata={
                'jersey_id': jersey_id,
                'jersey_name': jersey['name'],
                'email': data['email'],
                'phone': data['phone'],
                'shipping_address': shipping_address,
                'shipping_method': shipping_method,
                'shipping_cost': str(shipping_cost)
            }
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'amount': total_amount,
            'jersey_name': jersey['name']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/payment-complete')
def payment_complete():
    """Handle the payment completion and show order confirmation."""
    try:
        # Get the payment intent ID from the query parameters
        payment_intent_id = request.args.get('payment_intent')
        if not payment_intent_id:
            # Also try to get it from the client secret
            client_secret = request.args.get('payment_intent_client_secret')
            if client_secret:
                payment_intent_id = client_secret.split('_secret_')[0]
            
        if not payment_intent_id:
            print("Payment Intent ID missing from URL parameters:", request.args)
            raise ValueError('Payment intent ID not found in URL parameters')

        # Retrieve the payment intent from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        print(f"Retrieved payment intent: {payment_intent.id}, status: {payment_intent.status}")
        
        if payment_intent.status != 'succeeded':
            # Get error message from metadata if available
            error_message = payment_intent.last_payment_error.message if payment_intent.last_payment_error else None
            print(f"Payment not succeeded. Status: {payment_intent.status}, Error: {error_message}")
            # Get the jersey ID from metadata to construct the return URL
            jersey_id = payment_intent.metadata.get('jersey_id')
            return_url = url_for('checkout_info', jersey_id=jersey_id) if jersey_id else None
            return redirect(url_for('payment_failed', error=error_message, return_url=return_url))

        # Get order details from session
        order_details = session.get('order_details')
        if not order_details:
            print("Order details missing from session")
            raise ValueError('Order details not found in session')
            
        print(f"Order details found: {order_details}")
            
        # Clear the order details from session
        session.pop('order_details', None)
        
        return render_template('payment_complete.html', **order_details)
        
    except Exception as e:
        print(f"Error in payment completion: {str(e)}")
        # Try to get jersey_id from session order details
        jersey_id = None
        order_details = session.get('order_details', {})
        if order_details and 'jersey_id' in order_details:
            jersey_id = order_details['jersey_id']
        return_url = url_for('checkout_info', jersey_id=jersey_id) if jersey_id else None
        return redirect(url_for('payment_failed', error=str(e), return_url=return_url))

@app.route('/payment-failed')
def payment_failed():
    """Handle payment failures and show error message."""
    error_message = request.args.get('error', 'Your payment could not be processed.')
    # Use the provided return_url or try to get it from the referrer
    return_url = request.args.get('return_url') or request.referrer or url_for('index')
    return render_template('payment_failed.html', error_message=error_message, return_url=return_url)

@app.route('/checkout-info/<int:jersey_id>')
def checkout_info(jersey_id):
    """Render the checkout information form."""
    jerseys = load_jerseys()
    jersey = next((j for j in jerseys if j['id'] == jersey_id), None)
    
    if not jersey:
        flash('Jersey not found', 'error')
        return redirect(url_for('index'))
    
    # Get saved addresses for logged-in user
    saved_addresses = []
    if 'logged_in' in session and session['username'] in SAVED_ADDRESSES:
        saved_addresses = SAVED_ADDRESSES[session['username']]
    
    return render_template('checkout_info.html', 
                         jersey=jersey,
                         saved_addresses=saved_addresses,
                         stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'))

@app.route('/calculate-shipping', methods=['POST'])
def calculate_shipping():
    """Calculate shipping rates using EasyPost."""
    try:
        data = request.json
        print("Received shipping calculation request:", data)
        
        # Validate required fields
        required_fields = ['name', 'street', 'city', 'state', 'zip', 'country', 'email', 'phone']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            # Create EasyPost Address object using the client
            to_address = easypost_client.address.create(
                name=data['name'],
                street1=data['street'],
                city=data['city'],
                state=data['state'],
                zip=data['zip'],
                country=data['country'],
                email=data['email'],
                phone=data['phone']
            )
            print("Created destination address:", to_address)
            
            # Create from address using the client
            from_address = easypost_client.address.create(
                company='Your Store Name',
                street1='123 Warehouse St',
                city='Los Angeles',
                state='CA',
                zip='90001',
                country='US',
                phone='888-123-4567'
            )
            print("Created source address:", from_address)
            
            # Create parcel object using the client
            parcel = easypost_client.parcel.create(
                length=10.0,
                width=8.0,
                height=4.0,
                weight=16.0  # weight in ounces
            )
            print("Created parcel:", parcel)
            
            # Create shipment and get rates using the client
            shipment = easypost_client.shipment.create(
                to_address=to_address,
                from_address=from_address,
                parcel=parcel
            )
            print("Created shipment:", shipment)
            
            if not shipment.rates:
                raise ValueError("No shipping rates available for this address")
            
            # Format rates for frontend
            rates = [{
                'id': rate.id,
                'carrier': rate.carrier,
                'service': rate.service,
                'rate': float(rate.rate),
                'delivery_days': rate.delivery_days or 'Unknown'
            } for rate in shipment.rates]
            
            print("Available rates:", rates)
            return jsonify({'rates': rates})
            
        except Exception as e:
            print("EasyPost API error:", str(e))
            raise ValueError(f"Shipping calculation failed: {str(e)}")
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Initialize database
    # init_db()
    
    app.run(debug=True) 