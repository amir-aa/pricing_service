from flask import Flask, request, jsonify
from peewee import *
from playhouse.pool import PooledMySQLDatabase
import datetime
import json,os
from decimal import Decimal
from enum import Enum
from config import get_db
from flask import Flask, request, jsonify
from peewee import *
import datetime
import json
from decimal import Decimal
from enum import Enum
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
database=get_db()
# Base Model Class
class BaseModel(Model):
    class Meta:
        database = database

# Parameter Types Enum
class ParameterType(Enum):
    MULTIPLIER = 'multiplier'
    FIXED = 'fixed'
    QUANTITY = 'quantity'

# Models
# Models
class Service(BaseModel):
    name = CharField(unique=True)
    description = TextField(null=True)
    base_price = DecimalField(decimal_places=2)
    
    class Meta:
        table_name = 'services'

class Parameter(BaseModel):
    service = ForeignKeyField(Service, backref='parameters')
    name = CharField()
    description = TextField(null=True)
    parameter_type = CharField()
    is_required = BooleanField(default=False)
    default_value = CharField(null=True)
    
    class Meta:
        table_name = 'parameters'

class ParameterOption(BaseModel):
    parameter = ForeignKeyField(Parameter, backref='options')
    value = CharField()
    modifier = DecimalField(decimal_places=4)
    
    class Meta:
        table_name = 'parameter_options'

class PriceCalculation(BaseModel):
    timestamp = DateTimeField(default=datetime.datetime.now)
    service = ForeignKeyField(Service, backref='calculations')
    input_params = TextField()
    calculated_price = DecimalField(decimal_places=2)
    base_price = DecimalField(decimal_places=2)
    
    class Meta:
        table_name = 'price_calculations'
# Rest of your application code remains the same...
# (Keep all the route handlers and calculation functions as they were)

@app.before_request
def before_request():
    database.connect(reuse_if_open = True)

@app.after_request
def after_request(response):
    database.close()
    return response

def init_db():
    MODELS = [Service, Parameter, ParameterOption, PriceCalculation]
    database.create_tables(MODELS)
init_db()

# Helper function to calculate service price
def calculate_service_price(service_id, params):
    """
    Calculate service price based on dynamic parameters and service base price
    """
    try:
        # Fetch the service and its base price
        service = Service.get_by_id(service_id)
        base_price = Decimal(str(service.base_price))
        total_price = base_price
        multiplier = Decimal('1.0')
        fixed_modifiers = Decimal('0.0')
        
        # Get all parameters associated with the service
        parameters = Parameter.select().where(Parameter.service == service)
        
        for parameter in parameters:
            param_value = params.get(parameter.name, parameter.default_value)
            
            # Check if the parameter is required and missing
            if parameter.is_required and param_value is None:
                raise ValueError(f"Required parameter '{parameter.name}' is missing")
            
            if param_value is not None:
                try:
                    # Find matching option for the parameter value
                    option = (ParameterOption
                            .select()
                            .where(
                                (ParameterOption.parameter == parameter) & 
                                (ParameterOption.value == str(param_value))
                            )
                            .get())
                    
                    if parameter.parameter_type == ParameterType.MULTIPLIER.value:
                        multiplier *= option.modifier
                    elif parameter.parameter_type == ParameterType.FIXED.value:
                        fixed_modifiers += option.modifier
                    elif parameter.parameter_type == ParameterType.QUANTITY.value:
                        multiplier *= (option.modifier * Decimal(str(param_value)))
                        
                except ParameterOption.DoesNotExist:
                    raise ValueError(f"Invalid value '{param_value}' for parameter '{parameter.name}'")
        
        # Calculate final price
        total_price = (total_price * multiplier) + fixed_modifiers
        return max(total_price, Decimal('0.0'))  # Ensure price is not negative
        
    except Exception as e:
        raise ValueError(f"Calculation error: {str(e)}")

# Routes

@app.route('/services', methods=['GET'])
def get_services():
    Services=[model_to_dict(item) for item in Service.select()]
    return jsonify(Services)
    


@app.route('/services', methods=['POST'])
def create_service():
    """
    Create a new service
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        service = Service.create(
            name=data['name'],
            description=data.get('description'),
            base_price=data['base_price']
        )
        
        return jsonify({
            'message': 'Service created successfully',
            'service_id': service.id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parameters', methods=['POST'])
def create_parameter():
    """
    Create a new parameter for a service
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Fetch the service
        service = Service.get_by_id(data['service_id'])
        
        # Create the parameter
        parameter = Parameter.create(
            service=service,
            name=data['name'],
            description=data.get('description'),
            parameter_type=data['parameter_type'],
            is_required=data.get('is_required', False),
            default_value=data.get('default_value')
        )
        
        # Create options for the parameter
        for option in data.get('options', []):
            ParameterOption.create(
                parameter=parameter,
                value=option['value'],
                modifier=option['modifier']
            )
        
        return jsonify({'message': 'Parameter created successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parameters', methods=['GET'])
def get_parameters():
    """
    Get all parameters
    """
    try:
        parameters = []
        for param in Parameter.select():
            options = [
                {
                    'value': opt.value,
                    'modifier': float(opt.modifier)
                } 
                for opt in param.options
            ]
            
            parameters.append({
                'id': param.id,
                'service_id': param.service.id,
                'name': param.name,
                'description': param.description,
                'type': param.parameter_type,
                'is_required': param.is_required,
                'default_value': param.default_value,
                'options': options
            })
        
        return jsonify(parameters)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate-price', methods=['POST'])
def calculate_price():
    """
    Calculate the price for a service based on parameters
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        service_id = data.get('service_id')
        if not service_id:
            return jsonify({'error': 'Service ID is required'}), 400
        
        params = data.get('parameters', {})


        # Fetch the service to get the base price
        service = Service.get_by_id(service_id)
        missing_params=[]
        for _parameter in service.parameters:
            if _parameter.is_required and str(_parameter.name) not in params:
                missing_params.append(_parameter.name)
        if len(missing_params)>0:
            return jsonify({'error': 'some parameters are required','missing_parameters':missing_params}), 500


        #dictparams=json.loads(params)
        # Calculate price
        calculated_price = calculate_service_price(service_id, params)
        

        # Store calculation in database
        with database.atomic():
            calculation = PriceCalculation.create(
                service=service,
                input_params=json.dumps({
                    'service_id': service_id,
                    'parameters': params
                }),
                calculated_price=calculated_price,
                base_price=service.base_price
            )
        
        return jsonify({
            'calculation_id': calculation.id,
            'service_id': service_id,
            'base_price': float(service.base_price),
            'calculated_price': float(calculated_price),
            'timestamp': calculation.timestamp.isoformat(),
            'input_parameters': params
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Create tables
init_db()

if __name__ == '__main__':
    app.run(debug=True)