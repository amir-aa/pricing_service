from flask import Flask, request, jsonify
from peewee import *
from playhouse.pool import PooledMySQLDatabase
import datetime
import json

# Database connection pooling
db = PooledMySQLDatabase(
    'price_calculator',
    max_connections=32,
    stale_timeout=300,
    user='your_username',
    password='your_password',
    host='localhost',
    port=3306
)

app = Flask(__name__)

# Base Model Class
class BaseModel(Model):
    class Meta:
        database = db

# Models
class PriceCalculation(BaseModel):
    timestamp = DateTimeField(default=datetime.datetime.now)
    input_params = TextField()  # Store JSON string of input parameters
    calculated_price = DecimalField(decimal_places=2)
    
    class Meta:
        table_name = 'price_calculations'

# Price calculation function
def calculate_service_price(params):
    """
    Calculate service price based on input parameters
    params: dictionary of input parameters
    returns: calculated price
    """
    base_price = 100  # Base price
    
    # Example calculation logic 
    multiplier = 1.0
    
    if 'service_type' in params:
        if params['service_type'] == 'premium':
            multiplier *= 1.5
        elif params['service_type'] == 'basic':
            multiplier *= 1.0
    
    if 'quantity' in params:
        multiplier *= float(params['quantity'])
    
    if 'urgency' in params:
        if params['urgency'] == 'high':
            multiplier *= 1.3
    
    return base_price * multiplier

# Create tables
def create_tables():
    with db:
        db.create_tables([PriceCalculation])

# Routes
@app.route('/calculate-price', methods=['POST'])
def calculate_price():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Calculate price
        calculated_price = calculate_service_price(data)
        
        # Store calculation in database
        with db.atomic():
            calculation = PriceCalculation.create(
                input_params=json.dumps(data),
                calculated_price=calculated_price
            )
        
        return jsonify({
            'calculation_id': calculation.id,
            'price': calculated_price,
            'timestamp': calculation.timestamp.isoformat(),
            'input_parameters': data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculations', methods=['GET'])
def get_calculations():
    try:
        calculations = []
        query = PriceCalculation.select().order_by(PriceCalculation.timestamp.desc())
        
        for calc in query:
            calculations.append({
                'id': calc.id,
                'price': float(calc.calculated_price),
                'timestamp': calc.timestamp.isoformat(),
                'input_parameters': json.loads(calc.input_params)
            })
        
        return jsonify(calculations)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculation/<int:calc_id>', methods=['GET'])
def get_calculation(calc_id):
    try:
        calc = PriceCalculation.get_by_id(calc_id)
        return jsonify({
            'id': calc.id,
            'price': float(calc.calculated_price),
            'timestamp': calc.timestamp.isoformat(),
            'input_parameters': json.loads(calc.input_params)
        })
    except DoesNotExist:
        return jsonify({'error': 'Calculation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
