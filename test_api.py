"""
Test Suite for Flask User Management API
=======================================
Comprehensive tests for REST API endpoints
Author: Awais Syed
Email: awaissyed1212@gmail.com
"""

import pytest
import json
from app import app, user_manager

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def reset_users():
    """Reset users data for each test"""
    # Reset to initial state
    user_manager.users = {
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
        }
    }
    user_manager.next_id = 3
    yield

class TestAPIEndpoints:
    """Test class for API endpoints"""

    def test_home_endpoint(self, client):
        """Test GET / endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert data['data']['api_name'] == 'Flask User Management API'

    def test_get_all_users(self, client, reset_users):
        """Test GET /users endpoint"""
        response = client.get('/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'users' in data['data']
        assert len(data['data']['users']) >= 2

    def test_get_user_by_id(self, client, reset_users):
        """Test GET /users/<id> endpoint"""
        response = client.get('/users/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['user']['name'] == 'John Doe'

    def test_get_nonexistent_user(self, client, reset_users):
        """Test GET /users/<id> with non-existent ID"""
        response = client.get('/users/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'User with ID 999 not found' in data['message']

    def test_create_user(self, client, reset_users):
        """Test POST /users endpoint"""
        new_user = {
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 25,
            'position': 'Tester'
        }

        response = client.post('/users', 
                              data=json.dumps(new_user),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['user']['name'] == 'Test User'
        assert data['data']['user']['email'] == 'test@example.com'

    def test_create_user_validation(self, client, reset_users):
        """Test POST /users with invalid data"""
        invalid_user = {
            'name': '',  # Invalid: empty name
            'email': 'invalid-email',  # Invalid: bad email format
            'age': -5,   # Invalid: negative age
            'position': ''  # Invalid: empty position
        }

        response = client.post('/users',
                              data=json.dumps(invalid_user),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
        assert len(data['errors']) > 0

    def test_create_duplicate_email(self, client, reset_users):
        """Test POST /users with duplicate email"""
        duplicate_user = {
            'name': 'Duplicate User',
            'email': 'john.doe@example.com',  # Already exists
            'age': 30,
            'position': 'Developer'
        }

        response = client.post('/users',
                              data=json.dumps(duplicate_user),
                              content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['message']

    def test_update_user(self, client, reset_users):
        """Test PUT /users/<id> endpoint"""
        update_data = {
            'name': 'John Updated',
            'position': 'Senior Developer'
        }

        response = client.put('/users/1',
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['user']['name'] == 'John Updated'
        assert data['data']['user']['position'] == 'Senior Developer'

    def test_update_nonexistent_user(self, client, reset_users):
        """Test PUT /users/<id> with non-existent ID"""
        update_data = {'name': 'Updated Name'}

        response = client.put('/users/999',
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 404

    def test_delete_user(self, client, reset_users):
        """Test DELETE /users/<id> endpoint"""
        response = client.delete('/users/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted_user' in data['data']

        # Verify user is deleted
        response = client.get('/users/1')
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client, reset_users):
        """Test DELETE /users/<id> with non-existent ID"""
        response = client.delete('/users/999')
        assert response.status_code == 404

    def test_search_users(self, client, reset_users):
        """Test GET /users/search endpoint"""
        response = client.get('/users/search?q=John')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['users']) >= 1
        assert 'John' in data['data']['users'][0]['name']

    def test_search_users_empty_query(self, client, reset_users):
        """Test GET /users/search without query parameter"""
        response = client.get('/users/search')
        assert response.status_code == 400

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
