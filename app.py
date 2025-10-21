from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/seltzertracker')
client = MongoClient(MONGODB_URI)
db = client[os.getenv('MONGODB_DATABASE', 'seltzertracker')]

# Collections
users_collection = db.users
seltzers_collection = db.seltzers
brands_collection = db.brands

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.created_at = user_data.get('created_at', datetime.utcnow())

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Initialize default data
def init_default_data():
    # Check if brands already exist
    if brands_collection.count_documents({}) == 0:
        default_brands = [
            {
                'name': 'Polar Seltzer',
                'id': 'polar',
                'flavors': ['Lime', 'Lemon', 'Orange', 'Grapefruit', 'Cranberry', 'Raspberry', 'Black Cherry', 'Vanilla']
            },
            {
                'name': 'LaCroix',
                'id': 'lacroix',
                'flavors': ['Lime', 'Lemon', 'Orange', 'Grapefruit', 'Coconut', 'Pamplemousse', 'Passionfruit', 'Mango']
            },
            {
                'name': 'Spindrift',
                'id': 'spindrift',
                'flavors': ['Lemon', 'Orange Mango', 'Grapefruit', 'Cranberry Raspberry', 'Cucumber', 'Blackberry']
            },
            {
                'name': 'Bubly',
                'id': 'bubly',
                'flavors': ['Lime', 'Lemon', 'Cherry', 'Grapefruit', 'Orange', 'Strawberry', 'Apple', 'Mango']
            },
            {
                'name': 'AHA',
                'id': 'aha',
                'flavors': ['Lime + Watermelon', 'Orange + Grapefruit', 'Strawberry + Cucumber', 'Black Cherry + Coffee']
            },
            {
                'name': 'Perrier',
                'id': 'perrier',
                'flavors': ['Original', 'Lime', 'Lemon', 'Grapefruit', 'Green Apple', 'Pink Grapefruit']
            },
            {
                'name': 'Bubbly',
                'id': 'bubbly',
                'flavors': ['Cherry', 'Lime']
            },
            {
                'name': 'Vintage Seltzers',
                'id': 'vintage',
                'flavors': ['Cherry', 'Lime']
            }
        ]
        brands_collection.insert_many(default_brands)
        print("Default brands initialized")

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user_data = users_collection.find_one({'username': username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('index')})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user already exists
        if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
            return jsonify({'success': False, 'message': 'Username or email already exists'})
        
        # Create new user
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_data)
        user = User({'_id': result.inserted_id, **user_data})
        login_user(user)
        
        return jsonify({'success': True, 'redirect': url_for('index')})
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Page routes
@app.route('/log')
@login_required
def log():
    return render_template('log.html')

@app.route('/history')
@login_required
def history():
    return render_template('history.html')

@app.route('/search')
@login_required
def search():
    return render_template('search.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/edit/<seltzer_id>')
@login_required
def edit(seltzer_id):
    return render_template('edit.html', seltzer_id=seltzer_id)

def is_admin():
    """Check if current user is an admin"""
    if not current_user.is_authenticated:
        return False
    # Simple admin check - you can modify this logic as needed
    # For now, any logged-in user can access admin features
    # In production, you might want to add an 'is_admin' field to users
    return True

@app.route('/admin')
@login_required
def admin():
    if not is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    return render_template('admin.html')

# API Routes
@app.route('/api/seltzers', methods=['GET'])
@login_required
def get_seltzers():
    """Get all seltzers for the current user"""
    limit = request.args.get('limit', type=int)
    
    query = seltzers_collection.find({'user_id': current_user.id}).sort('created_at', -1)
    if limit:
        query = query.limit(limit)
    
    seltzers = list(query)
    
    # Convert ObjectId to string for JSON serialization
    for seltzer in seltzers:
        seltzer['_id'] = str(seltzer['_id'])
        seltzer['created_at'] = seltzer['created_at'].isoformat()
    
    return jsonify(seltzers)

@app.route('/api/seltzers/<seltzer_id>', methods=['GET'])
@login_required
def get_seltzer(seltzer_id):
    """Get a single seltzer entry"""
    seltzer = seltzers_collection.find_one({'_id': ObjectId(seltzer_id), 'user_id': current_user.id})
    if not seltzer:
        return jsonify({'error': 'Seltzer not found'}), 404
    
    seltzer['_id'] = str(seltzer['_id'])
    seltzer['created_at'] = seltzer['created_at'].isoformat()
    
    return jsonify(seltzer)

@app.route('/api/seltzers', methods=['POST'])
@login_required
def create_seltzer():
    """Create a new seltzer entry"""
    data = request.get_json()
    
    seltzer_data = {
        'user_id': current_user.id,
        'brand': data.get('brand'),
        'brand_id': data.get('brand_id'),
        'flavor': data.get('flavor'),
        'flavor_id': data.get('flavor_id'),
        'rating': int(data.get('rating', 0)),
        'date': data.get('date'),
        'time': data.get('time'),
        'notes': data.get('notes', ''),
        'created_at': datetime.utcnow()
    }
    
    result = seltzers_collection.insert_one(seltzer_data)
    seltzer_data['_id'] = str(result.inserted_id)
    seltzer_data['created_at'] = seltzer_data['created_at'].isoformat()
    
    return jsonify(seltzer_data)

@app.route('/api/seltzers/<seltzer_id>', methods=['PUT'])
@login_required
def update_seltzer(seltzer_id):
    """Update a seltzer entry"""
    data = request.get_json()
    
    # Verify ownership
    seltzer = seltzers_collection.find_one({'_id': ObjectId(seltzer_id), 'user_id': current_user.id})
    if not seltzer:
        return jsonify({'success': False, 'message': 'Seltzer not found'})
    
    update_data = {
        'brand': data.get('brand'),
        'brand_id': data.get('brand_id'),
        'flavor': data.get('flavor'),
        'flavor_id': data.get('flavor_id'),
        'rating': int(data.get('rating', 0)),
        'date': data.get('date'),
        'time': data.get('time'),
        'notes': data.get('notes', ''),
        'updated_at': datetime.utcnow()
    }
    
    seltzers_collection.update_one(
        {'_id': ObjectId(seltzer_id)},
        {'$set': update_data}
    )
    
    return jsonify({'success': True})

@app.route('/api/seltzers/<seltzer_id>', methods=['DELETE'])
@login_required
def delete_seltzer(seltzer_id):
    """Delete a seltzer entry"""
    # Verify ownership
    seltzer = seltzers_collection.find_one({'_id': ObjectId(seltzer_id), 'user_id': current_user.id})
    if not seltzer:
        return jsonify({'success': False, 'message': 'Seltzer not found'})
    
    seltzers_collection.delete_one({'_id': ObjectId(seltzer_id)})
    return jsonify({'success': True})

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """Get all brands and their flavors"""
    brands = list(brands_collection.find())
    
    for brand in brands:
        brand['_id'] = str(brand['_id'])
    
    return jsonify(brands)

@app.route('/api/brands/<brand_id>/flavors', methods=['POST'])
@login_required
def add_flavor(brand_id):
    """Add a new flavor to a brand (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admin privileges required'})
    
    data = request.get_json()
    flavor_name = data.get('flavor_name')
    
    if not flavor_name:
        return jsonify({'success': False, 'message': 'Flavor name is required'})
    
    # Check if flavor already exists
    brand = brands_collection.find_one({'id': brand_id})
    if not brand:
        return jsonify({'success': False, 'message': 'Brand not found'})
    
    if flavor_name in brand['flavors']:
        return jsonify({'success': False, 'message': 'Flavor already exists'})
    
    brands_collection.update_one(
        {'id': brand_id},
        {'$push': {'flavors': flavor_name}}
    )
    
    return jsonify({'success': True})

@app.route('/api/brands/<brand_id>/flavors', methods=['DELETE'])
@login_required
def remove_flavor(brand_id):
    """Remove a flavor from a brand (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admin privileges required'})
    
    data = request.get_json()
    flavor_name = data.get('flavor_name')
    
    if not flavor_name:
        return jsonify({'success': False, 'message': 'Flavor name is required'})
    
    brands_collection.update_one(
        {'id': brand_id},
        {'$pull': {'flavors': flavor_name}}
    )
    
    return jsonify({'success': True})

@app.route('/api/brands', methods=['POST'])
@login_required
def create_brand():
    """Create a new brand (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admin privileges required'})
    
    data = request.get_json()
    brand_name = data.get('brand_name', '').strip()
    brand_id = data.get('brand_id', '').strip()
    initial_flavors = data.get('initial_flavors', [])
    
    if not brand_name:
        return jsonify({'success': False, 'message': 'Brand name is required'})
    
    if not brand_id:
        # Generate brand_id from brand_name (lowercase, replace spaces with hyphens)
        brand_id = brand_name.lower().replace(' ', '-').replace('&', 'and')
    
    # Check if brand already exists
    if brands_collection.find_one({'$or': [{'name': brand_name}, {'id': brand_id}]}):
        return jsonify({'success': False, 'message': 'Brand with this name or ID already exists'})
    
    # Create new brand
    brand_data = {
        'name': brand_name,
        'id': brand_id,
        'flavors': initial_flavors if initial_flavors else []
    }
    
    result = brands_collection.insert_one(brand_data)
    brand_data['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'brand': brand_data})

@app.route('/api/brands/<brand_id>', methods=['DELETE'])
@login_required
def delete_brand(brand_id):
    """Delete a brand (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admin privileges required'})
    
    # Check if brand exists
    brand = brands_collection.find_one({'id': brand_id})
    if not brand:
        return jsonify({'success': False, 'message': 'Brand not found'})
    
    # Check if brand is being used in any seltzer entries
    seltzer_count = seltzers_collection.count_documents({'brand_id': brand_id})
    if seltzer_count > 0:
        return jsonify({'success': False, 'message': f'Cannot delete brand. It is being used in {seltzer_count} seltzer entries.'})
    
    # Delete the brand
    brands_collection.delete_one({'id': brand_id})
    
    return jsonify({'success': True, 'message': f'Brand "{brand["name"]}" deleted successfully'})

@app.route('/api/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user statistics"""
    # Get total seltzers
    total_seltzers = seltzers_collection.count_documents({'user_id': current_user.id})
    
    # Get average rating
    pipeline = [
        {'$match': {'user_id': current_user.id}},
        {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
    ]
    avg_rating_result = list(seltzers_collection.aggregate(pipeline))
    avg_rating = round(avg_rating_result[0]['avg_rating'], 1) if avg_rating_result else 0
    
    # Get this week's count
    week_ago = datetime.utcnow() - timedelta(days=7)
    this_week = seltzers_collection.count_documents({
        'user_id': current_user.id,
        'created_at': {'$gte': week_ago}
    })
    
    # Get top brand
    pipeline = [
        {'$match': {'user_id': current_user.id}},
        {'$group': {'_id': '$brand', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 1}
    ]
    top_brand_result = list(seltzers_collection.aggregate(pipeline))
    top_brand = top_brand_result[0]['_id'] if top_brand_result else 'None'
    
    # Get brand distribution
    brand_pipeline = [
        {'$match': {'user_id': current_user.id}},
        {'$group': {'_id': '$brand', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    brand_distribution = list(seltzers_collection.aggregate(brand_pipeline))
    
    return jsonify({
        'total_seltzers': total_seltzers,
        'avg_rating': avg_rating,
        'this_week': this_week,
        'top_brand': top_brand,
        'brand_distribution': brand_distribution
    })

@app.route('/api/search', methods=['GET'])
@login_required
def search_seltzers():
    """Search seltzers by brand, flavor, or notes"""
    query = request.args.get('q', '')
    filter_type = request.args.get('filter', 'all')
    
    search_filter = {'user_id': current_user.id}
    
    if query:
        if filter_type == 'brand':
            search_filter['brand'] = {'$regex': query, '$options': 'i'}
        elif filter_type == 'flavor':
            search_filter['flavor'] = {'$regex': query, '$options': 'i'}
        else:
            search_filter['$or'] = [
                {'brand': {'$regex': query, '$options': 'i'}},
                {'flavor': {'$regex': query, '$options': 'i'}},
                {'notes': {'$regex': query, '$options': 'i'}}
            ]
    
    seltzers = list(seltzers_collection.find(search_filter).sort('created_at', -1))
    
    for seltzer in seltzers:
        seltzer['_id'] = str(seltzer['_id'])
        seltzer['created_at'] = seltzer['created_at'].isoformat()
    
    return jsonify(seltzers)

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    # Initialize default data
    init_default_data()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
