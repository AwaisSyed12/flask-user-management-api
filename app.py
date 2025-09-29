"""
Flask REST API - User Management System
======================================
A professional REST API for managing user data with CRUD operations
Author: Awais Syed
Email: awaissyed1212@gmail.com
Features: GET/POST/PUT/DELETE endpoints, JSON responses, error handling
"""

from flask import Flask, jsonify, request
from datetime import datetime
import uuid
import re

class UserManager:
    """User management system with in-memory storage"""

    def __init__(self):
        """Initialize with sample users data"""
        self.users = {
            1: {
                'id': 1,
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'age': 30,
                'position': 'Software Developer',
                'created_at': '2025-09-29 21:42:00',
                'updated_at': '2025-09-29 21:42:00'
            },
            2: {
                'id': 2,
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'age': 28,
                'position': 'Product Manager',
                'created_at': '2025-09-29 21:42:00',
                'updated_at': '2025-09-29 21:42:00'
            },
            3: {
                'id': 3,
                'name': 'Mike Johnson',
                'email': 'mike.johnson@example.com',
                'age': 35,
                'position': 'DevOps Engineer',
                'created_at': '2025-09-29 21:42:00',
                'updated_at': '2025-09-29 21:42:00'
            }
        }
        self.next_id = 4

    def get_all_users(self):
        """Get all users"""
        return list(self.users.values())

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.users.get(user_id)

    def create_user(self, user_data):
        """Create a new user"""
        user_id = self.next_id
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        new_user = {
            'id': user_id,
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'age': user_data.get('age'),
            'position': user_data.get('position'),
            'created_at': now,
            'updated_at': now
        }

        self.users[user_id] = new_user
        self.next_id += 1
        return new_user

    def update_user(self, user_id, user_data):
        """Update existing user"""
        if user_id not in self.users:
            return None

        user = self.users[user_id]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update only provided fields
        if 'name' in user_data:
            user['name'] = user_data['name']
        if 'email' in user_data:
            user['email'] = user_data['email']
        if 'age' in user_data:
            user['age'] = user_data['age']
        if 'position' in user_data:
            user['position'] = user_data['position']

        user['updated_at'] = now
        return user

    def delete_user(self, user_id):
        """Delete user by ID"""
        if user_id in self.users:
            deleted_user = self.users.pop(user_id)
            return deleted_user
        return None

    def validate_user_data(self, data, is_update=False):
        """Validate user data"""
        errors = []

        # Required fields for creation
        if not is_update:
            required_fields = ['name', 'email', 'age', 'position']
            for field in required_fields:
                if field not in data or not data[field]:
                    errors.append(f"Field '{field}' is required")

        # Validate email format
        if 'email' in data and data['email']:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("Invalid email format")

        # Validate age
        if 'age' in data and data['age']:
            try:
                age = int(data['age'])
                if age < 0 or age > 150:
                    errors.append("Age must be between 0 and 150")
            except (ValueError, TypeError):
                errors.append("Age must be a valid number")

        # Validate name
        if 'name' in data and data['name']:
            if len(data['name'].strip()) < 2:
                errors.append("Name must be at least 2 characters long")

        # Validate position
        if 'position' in data and data['position']:
            if len(data['position'].strip()) < 2:
                errors.append("Position must be at least 2 characters long")

        return errors

# Initialize Flask app
app = Flask(__name__)
app.config['DEBUG'] = True

# Initialize user manager
user_manager = UserManager()

def create_response(data=None, message=None, status_code=200, errors=None):
    """Create standardized API response"""
    response = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status_code': status_code
    }

    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    if errors:
        response['errors'] = errors

    return jsonify(response), status_code

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_response(
        message="Resource not found",
        status_code=404
    )

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return create_response(
        message="Bad request",
        status_code=400
    )

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return create_response(
        message="Internal server error",
        status_code=500
    )

@app.route('/', methods=['GET'])
def home():
    """Welcome endpoint"""
    return create_response(
        data={
            'api_name': 'Flask User Management API',
            'version': '1.0.0',
            'description': 'REST API for managing user data with CRUD operations',
            'endpoints': {
                'GET /': 'API information',
                'GET /users': 'Get all users',
                'GET /users/<id>': 'Get user by ID',
                'POST /users': 'Create new user',
                'PUT /users/<id>': 'Update user',
                'DELETE /users/<id>': 'Delete user'
            }
        },
        message="Welcome to Flask User Management API"
    )

@app.route('/users', methods=['GET'])
def get_users():
    """GET endpoint - Retrieve all users"""
    users = user_manager.get_all_users()
    return create_response(
        data={
            'users': users,
            'total_count': len(users)
        },
        message=f"Retrieved {len(users)} users successfully"
    )

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """GET endpoint - Retrieve specific user by ID"""
    user = user_manager.get_user_by_id(user_id)

    if not user:
        return create_response(
            message=f"User with ID {user_id} not found",
            status_code=404
        )

    return create_response(
        data={'user': user},
        message="User retrieved successfully"
    )

@app.route('/users', methods=['POST'])
def create_user():
    """POST endpoint - Create new user"""
    try:
        # Check if request has JSON data
        if not request.is_json:
            return create_response(
                message="Request must contain JSON data",
                status_code=400
            )

        data = request.get_json()

        # Validate input data
        errors = user_manager.validate_user_data(data)
        if errors:
            return create_response(
                message="Validation failed",
                errors=errors,
                status_code=400
            )

        # Check if email already exists
        existing_users = user_manager.get_all_users()
        for user in existing_users:
            if user['email'].lower() == data['email'].lower():
                return create_response(
                    message="User with this email already exists",
                    status_code=409
                )

        # Create user
        new_user = user_manager.create_user(data)

        return create_response(
            data={'user': new_user},
            message="User created successfully",
            status_code=201
        )

    except Exception as e:
        return create_response(
            message="Error creating user",
            errors=[str(e)],
            status_code=500
        )

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """PUT endpoint - Update existing user"""
    try:
        # Check if user exists
        if not user_manager.get_user_by_id(user_id):
            return create_response(
                message=f"User with ID {user_id} not found",
                status_code=404
            )

        # Check if request has JSON data
        if not request.is_json:
            return create_response(
                message="Request must contain JSON data",
                status_code=400
            )

        data = request.get_json()

        # Validate input data
        errors = user_manager.validate_user_data(data, is_update=True)
        if errors:
            return create_response(
                message="Validation failed",
                errors=errors,
                status_code=400
            )

        # Check if email already exists (for different user)
        if 'email' in data:
            existing_users = user_manager.get_all_users()
            for user in existing_users:
                if user['id'] != user_id and user['email'].lower() == data['email'].lower():
                    return create_response(
                        message="Another user with this email already exists",
                        status_code=409
                    )

        # Update user
        updated_user = user_manager.update_user(user_id, data)

        return create_response(
            data={'user': updated_user},
            message="User updated successfully"
        )

    except Exception as e:
        return create_response(
            message="Error updating user",
            errors=[str(e)],
            status_code=500
        )

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """DELETE endpoint - Delete user"""
    try:
        # Attempt to delete user
        deleted_user = user_manager.delete_user(user_id)

        if not deleted_user:
            return create_response(
                message=f"User with ID {user_id} not found",
                status_code=404
            )

        return create_response(
            data={'deleted_user': deleted_user},
            message="User deleted successfully"
        )

    except Exception as e:
        return create_response(
            message="Error deleting user",
            errors=[str(e)],
            status_code=500
        )

@app.route('/users/search', methods=['GET'])
def search_users():
    """GET endpoint - Search users by name or email"""
    query = request.args.get('q', '').strip()

    if not query:
        return create_response(
            message="Search query parameter 'q' is required",
            status_code=400
        )

    all_users = user_manager.get_all_users()
    matching_users = []

    for user in all_users:
        if (query.lower() in user['name'].lower() or 
            query.lower() in user['email'].lower() or 
            query.lower() in user['position'].lower()):
            matching_users.append(user)

    return create_response(
        data={
            'users': matching_users,
            'total_count': len(matching_users),
            'search_query': query
        },
        message=f"Found {len(matching_users)} users matching '{query}'"
    )

if __name__ == '__main__':
    print("🚀 Starting Flask User Management API...")
    print("📍 API will be available at: http://localhost:5000")
    print("📚 Visit http://localhost:5000 for API documentation")
    print("\n📋 Available endpoints:")
    print("   GET    /           - API information")
    print("   GET    /users      - Get all users")
    print("   GET    /users/<id> - Get user by ID")
    print("   POST   /users      - Create new user")
    print("   PUT    /users/<id> - Update user")
    print("   DELETE /users/<id> - Delete user")
    print("   GET    /users/search?q=<query> - Search users")
    print("\n✨ Ready for requests!")

    app.run(host='0.0.0.0', port=5000, debug=True)
