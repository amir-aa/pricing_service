import pytest
from flask import json
from app import app, Service, Parameter, ParameterOption, PriceCalculation, calculate_service_price, init_db, database
from decimal import Decimal

# Fixture to set up the Flask app and database
@pytest.fixture
def client():
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'sqlite:///:memory:'
    database.init('sqlite:///:memory:')  # Use an in-memory SQLite database for testing

    # Initialize the database
    init_db()

    # Create a test client
    with app.test_client() as client:
        with app.app_context():
            yield client

    # Clean up the database after the test
    with app.app_context():
        PriceCalculation.drop_table()
        ParameterOption.drop_table()
        Parameter.drop_table()
        Service.drop_table()

# Test creating a new service
def test_create_service(client):
    data = {
        'name': 'Test Service',
        'description': 'This is a test service',
        'base_price': 100
    }
    response = client.post('/services', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'message' in response_data
    assert 'service_id' in response_data

# Test creating a new parameter
def test_create_parameter(client):
    # First, create a service
    test_create_service(client)
    
    data = {
        'service_id': 1,
        'name': 'test_param',
        'description': 'Test parameter',
        'parameter_type': 'multiplier',
        'is_required': True,
        'default_value': '1',
        'options': [
            {'value': '1', 'modifier': 1.0},
            {'value': '2', 'modifier': 1.5}
        ]
    }
    response = client.post('/parameters', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'message' in response_data

# Test retrieving all parameters
def test_get_parameters(client):
    # First, create a service and parameter
    test_create_parameter(client)
    
    response = client.get('/parameters')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

# Test calculating the price with parameters
def test_calculate_price(client):
    # First, create a service and parameter
    test_create_parameter(client)
    
    data = {
        'service_id': 1,
        'parameters': {
            'test_param': '2'
        }
    }
    response = client.post('/calculate-price', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'calculated_price' in result
    assert result['calculated_price'] == 150.0  # 100 * 1.5


# Test price calculation with an invalid parameter value
def test_calculate_price_invalid_parameter_value(client):
    # First, create a service and parameter
    test_create_parameter(client)
    
    data = {
        'service_id': 1,
        'parameters': {
            'test_param': 'invalid_value'  # Invalid value
        }
    }
    response = client.post('/calculate-price', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 500
    response_data = json.loads(response.data)
    assert 'error' in response_data
    assert "Invalid value 'invalid_value' for parameter 'test_param'" in response_data['error']

# Test the calculate_service_price function directly
def test_calculate_service_price_function(client):
    # Create a service
    service = Service.create(
        name='Test Service',
        description='This is a test service',
        base_price=100
    )
    
    # Create a parameter and options
    param = Parameter.create(
        service=service,
        name='test_param',
        parameter_type='multiplier',
        is_required=True,
        default_value='1'
    )
    ParameterOption.create(parameter=param, value='1', modifier=1.0)
    ParameterOption.create(parameter=param, value='2', modifier=1.5)

    # Test calculation
    params = {'test_param': '2'}
    calculated_price = calculate_service_price(service.id, params)
    assert calculated_price == Decimal('150.0')

# Test creating a service with missing data
def test_create_service_missing_data(client):
    data = {
        'description': 'This is a test service',
        'base_price': 100
    }
    response = client.post('/services', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 500
    response_data = json.loads(response.data)
    assert 'error' in response_data

# Test creating a parameter with missing data ! in this case id is missed!
def test_create_parameter_missing_data(client):
    # First, create a service
    test_create_service(client)
    
    data = {
        
        'name': 'test_param',
        'parameter_type': 'multiplier',
        'is_required': True,
        'default_value': '1'
    }
    response = client.post('/parameters', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 500
    response_data = json.loads(response.data)
    assert 'error' in response_data

class TestGetServices:
	def test_get_services_status_code(self, client):
		response = client.get('/services')
		assert response.status_code == 200
          
class TestGetServices:
	def test_get_services(self, client):
		# Arrange
		Service.create(name='Service 1', description='Description 1', base_price=100.00)
		Service.create(name='Service 2', description='Description 2', base_price=200.00)
		
		# Act
		response = client.get('/services')
		
		# Assert
		assert response.status_code == 200
		data = response.get_json()
		assert isinstance(data, list)
		assert len(data) == 2
		assert all('name' in service for service in data)