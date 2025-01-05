# Service Price Calculator API

A Flask-based REST API for calculating service prices with MariaDB/MySQL storage using Peewee ORM. This application provides endpoints for calculating prices based on various parameters and stores both input and output data in a MySQL database with connection pooling.

در این رابط شما شما باید سه ورودی نوع سرویس، تعداد و اولویت را بعنوان ورودی ارائه کنید و در پاسخ قیمت محاسبه شده را دریافت نمایید. تمام پاسخ ها با یک شناسه در پاسخ برمیگردند و با همان شناسه هم مجددا در دسترس خواهند بود! 
<br/>
متغیر multiplier تعیین کننده ضریب در محاسبات است.
<br/>

![image](https://github.com/user-attachments/assets/3915e6c8-8a17-4cb6-885a-914033466507)

## Features

- RESTful API endpoints for price calculations
- MySQL database integration with connection pooling
- Flexible parameter handling for price calculations
- Historical data storage and retrieval
- Input parameter validation
- Error handling and logging

## Requirements

- Python 3.8+
- MySQL 8+ (Mariadb preferred)
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/price-calculator-api.git
cd price-calculator-api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install flask peewee mysqlclient
```

4. Set up the MySQL database:
```sql
CREATE DATABASE price_calculator;
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON price_calculator.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```

5. Update the database configuration in `app.py`:
```python
db = PooledMySQLDatabase(
    'price_calculator',
    max_connections=32,
    stale_timeout=300,
    user='your_username',
    password='your_password',
    host='localhost',
    port=3306
)
```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### 1. Calculate Price (POST `/calculate-price`)

Calculate and store a new price calculation.

**Request Body:**

```json
{
    "service_type": "premium",  // optional: "premium" or "basic", default: "basic"
    "quantity": 2,             // optional: positive number, default: 1
    "urgency": "high"          // optional: "high" or "normal", default: "normal"
}
```

**Mandatory Fields:** None (all fields are optional with defaults)

**Response:**
```json
{
    "calculation_id": 1,
    "price": 390.0,
    "timestamp": "2025-01-05T14:30:00",
    "input_parameters": {
        "service_type": "premium",
        "quantity": 2,
        "urgency": "high"
    }
}
```

#### 2. Get All Calculations (GET `/calculations`)

Retrieve all stored calculations.

**Parameters:** None

**Response:**
```json
[
    {
        "id": 1,
        "price": 390.0,
        "timestamp": "2025-01-05T14:30:00",
        "input_parameters": {
            "service_type": "premium",
            "quantity": 2,
            "urgency": "high"
        }
    },
    // ... more calculations
]
```

#### 3. Get Specific Calculation (GET `/calculation/<id>`)

Retrieve a specific calculation by ID.

**Parameters:** 
- `id`: The calculation ID (in URL)

**Response:**
```json
{
    "id": 1,
    "price": 390.0,
    "timestamp": "2025-01-05T14:30:00",
    "input_parameters": {
        "service_type": "premium",
        "quantity": 2,
        "urgency": "high"
    }
}
```

### Price Calculation Rules

The base price is 100 units, modified by the following factors:

1. Service Type:
   - Premium: 1.5x multiplier
   - Basic: 1.0x multiplier (default)

2. Quantity:
   - Multiplied directly by the quantity value
   - Default: 1

3. Urgency:
   - High: 1.3x multiplier
   - Normal: 1.0x multiplier (default)

### Example Requests

1. Basic calculation with all parameters:
```bash
curl -X POST http://localhost:5000/calculate-price \
-H "Content-Type: application/json" \
-d '{
    "service_type": "premium",
    "quantity": 2,
    "urgency": "high"
}'
```

2. Minimal calculation with defaults:
```bash
curl -X POST http://localhost:5000/calculate-price \
-H "Content-Type: application/json" \
-d '{}'
```

3. Get all calculations:
```bash
curl http://localhost:5000/calculations
```

4. Get specific calculation:
```bash
curl http://localhost:5000/calculation/1
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400: Bad Request (invalid input)
- 404: Not Found (calculation not found)
- 500: Internal Server Error

Example error response:
```json
{
    "error": "Invalid service type. Must be 'premium' or 'basic'"
}
```

## Database Schema

The application uses a single table with the following structure:

```sql
CREATE TABLE price_calculations (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME NOT NULL,
    input_params TEXT NOT NULL,
    calculated_price DECIMAL(10,2) NOT NULL
);
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Author
[Written by Amir Ahmadabadiha](https://linkedin.com/in/amir-ahmadabadiha-259113175)


