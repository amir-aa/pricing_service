# Dynamic Service Price Calculator API
# سیستم محاسبه پویای قیمت خدمات

A flexible REST API for calculating service prices with dynamic parameters and rules stored in MySQL database. This system allows administrators to define various parameters and their effects on price calculation, supporting multipliers, fixed amounts, and quantity-based modifications.

یک API انعطاف‌پذیر برای محاسبه قیمت خدمات با پارامترهای پویا و قوانین ذخیره شده در پایگاه داده MySQL. این سیستم به مدیران امکان می‌دهد پارامترهای مختلف و تأثیر آنها بر محاسبه قیمت را تعریف کنند و از ضرایب، مقادیر ثابت و تغییرات مبتنی بر تعداد پشتیبانی می‌کند.
![image](https://github.com/user-attachments/assets/3915e6c8-8a17-4cb6-885a-914033466507)
## Features | ویژگی‌ها

- Dynamic parameter definition | تعریف پویای پارامترها
- Three types of price modifiers | سه نوع تغییردهنده قیمت:
  - Percentage-based multipliers | ضرایب درصدی
  - Fixed amount additions/subtractions | افزودن/کاهش مقادیر ثابت
  - Quantity-based calculations | محاسبات مبتنی بر تعداد
- Parameter validation | اعتبارسنجی پارامترها
- Historical data storage | ذخیره‌سازی تاریخچه محاسبات
- MySQL connection pooling | استخر اتصالات MySQL

## Requirements | پیش‌نیازها

- Python 3.8+
- MySQL 5.7+
- pip (Python package manager | مدیر پکیج پایتون)


2. Create virtual environment | ایجاد محیط مجازی:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install requirements | نصب نیازمندی‌ها:
```bash
pip install flask peewee mysqlclient
```

4. Set up MySQL database | راه‌اندازی پایگاه داده:
```sql
CREATE DATABASE price_calculator;
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON price_calculator.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```
5. Set up MySQL configs | تنظیم پایگاه داده:
After writing your actual parameters on 'config_sample.py' change its name to 'config.py'

در فایل config_sample.py مقادیر مرتبط را جاگذاری کنید سپس نام آنرا به config.py تغییر دهید.
## API Endpoints | نقاط پایانی API

### 1. Parameter Management | مدیریت پارامترها

#### Create Parameter (POST `/parameters`)
Create a new calculation parameter | ایجاد پارامتر جدید محاسبه

```json
{
    "name": "service_level",
    "description": "Level of service",
    "parameter_type": "multiplier",
    "is_required": true,
    "default_value": "basic",
    "options": [
        {"value": "basic", "modifier": 1.0},
        {"value": "premium", "modifier": 1.5},
        {"value": "enterprise", "modifier": 2.0}
    ]
}
```

#### Get Parameters (GET `/parameters`)
Retrieve all defined parameters | دریافت تمام پارامترهای تعریف شده

### 2. Price Calculation | محاسبه قیمت

#### Calculate Price (POST `/calculate-price`)

**Request Body | بدنه درخواست:**
```json
{
    "base_price": 100,
    "parameters": {
        "service_level": "premium",
        "rush_fee": "next_day",
        "units": "2"
    }
}
```

**Response | پاسخ:**
```json
{
    "calculation_id": 1,
    "base_price": 100.0,
    "calculated_price": 350.0,
    "timestamp": "2025-01-11T14:30:00",
    "input_parameters": {
        "service_level": "premium",
        "rush_fee": "next_day",
        "units": "2"
    }
}
```

## Parameter Types | انواع پارامتر

### 1. Multiplier (percentage-based) | ضریب (درصدی)
- Affects price multiplicatively | تأثیر ضربی روی قیمت
- Example | مثال: Service level (1.0x, 1.5x, 2.0x)
```json
{
    "name": "service_level",
    "parameter_type": "multiplier",
    "options": [
        {"value": "basic", "modifier": 1.0},
        {"value": "premium", "modifier": 1.5}
    ]
}
```

### 2. Fixed Amount | مقدار ثابت
- Adds/subtracts fixed amount | افزودن/کاهش مقدار ثابت
- Example | مثال: Rush fee (+50, +100)
```json
{
    "name": "rush_fee",
    "parameter_type": "fixed",
    "options": [
        {"value": "none", "modifier": 0},
        {"value": "next_day", "modifier": 50}
    ]
}
```

### 3. Quantity-based | مبتنی بر تعداد
- Multiplies by quantity | ضرب در تعداد
- Example | مثال: Number of units
```json
{
    "name": "units",
    "parameter_type": "quantity",
    "options": [
        {"value": "1", "modifier": 1.0}
    ]
}
```

## Example Usage | مثال استفاده

## 1. Create a Service

**Endpoint:** `POST /services`

### Request Body:

```json
{
  "name": "Car Wash",
  "description": "Car washing service",
  "base_price": 50
}
```

### Description:
This endpoint allows you to create a new service. You must provide the service name, description, and the base price.

---

## 2. Create a Parameter

**Endpoint:** `POST /parameters`

### Request Body:

```json
{
  "service_id": 1,
  "name": "Car Size",
  "description": "Size of the car",
  "parameter_type": "multiplier",
  "is_required": true,
  "default_value": "Small",
  "options": [
    { "value": "Small", "modifier": 1.0 },
    { "value": "Large", "modifier": 1.5 }
  ]
}
```

### Description:
This endpoint allows you to create a parameter for an existing service. In this example, the parameter is `Car Size`, which allows users to select between "Small" or "Large" car sizes, each with a corresponding price modifier.

---

## 3. Calculate Price

**Endpoint:** `POST /calculate-price`

### Request Body:

```json
{
  "service_id": 1,
  "parameters": {
    "Car Size": "Large",
    "Waxing": "Yes"
  }
}
```

### Description:
This endpoint calculates the price for a service based on the provided parameters. You must pass the `service_id` and a set of parameters to get the final price.

--- 

```markdown
## Price Calculation Logic | منطق محاسبه قیمت

### Overview
The price calculation logic determines the final price of a service by applying various modifiers (multipliers, fixed values, or quantities) to the base price of the service. This logic is implemented within the `calculate_service_price` function.

### Steps

#### 1. Fetch the Service:
- Retrieve the service from the database using the `service_id`.
- Obtain the `base_price` of the service.

#### 2. Initialize Variables:
- `total_price`: Starts with the `base_price`.
- `multiplier`: Starts at `1.0` (used for multiplicative modifiers).
- `fixed_modifiers`: Starts at `0.0` (used for additive modifiers).

#### 3. Process Parameters:
For each parameter associated with the service:
- Retrieve the user-provided value, or use the default value if none is provided.
- If the parameter is required and no value is provided, raise an error.
- Find the corresponding `ParameterOption` for the provided value.
- Apply the modifier based on the parameter type:
  - **Multiplier**: Multiply the `multiplier` by the option's modifier.
  - **Fixed**: Add the option's modifier to `fixed_modifiers`.
  - **Quantity**: Multiply the `multiplier` by the option's modifier and the provided quantity.

#### 4. Calculate Final Price:
- Multiply the `base_price` by the `multiplier`.
- Add the `fixed_modifiers` to the result.
- Ensure the final price is not negative (set it to `0.0` if negative).

#### 5. Return the Final Price:
- Return the calculated price.

### Example Calculation

**Input:**
- **Service:** Car Wash (`base_price = $50`)
- **Parameters:**
  - Car Size: Large (`multiplier = 1.5`)
  - Waxing: Yes (`fixed_modifier = +$10`)

**Calculation:**
- `base_price = $50`
- `multiplier = 1.0 * 1.5 = 1.5` (from Car Size)
- `fixed_modifiers = $10` (from Waxing)
- `total_price = ($50 * 1.5) + $10 = $85`

**Output:**
- **Final Price:** $85

---

### منطق محاسبه قیمت (فارسی)

#### مرور کلی
منطق محاسبه قیمت، قیمت نهایی یک سرویس را با اعمال تعدیل‌کننده‌ها (ضریب، مقدار ثابت یا مقدار کمی) به قیمت پایه سرویس محاسبه می‌کند. این منطق در تابع `calculate_service_price` پیاده‌سازی شده است.

#### مراحل

##### 1. دریافت سرویس:
- سرویس را از پایگاه داده با استفاده از `service_id` دریافت کنید.
- `base_price` سرویس را دریافت کنید.

##### 2. مقداردهی اولیه متغیرها:
- `total_price`: با `base_price` شروع می‌شود.
- `multiplier`: با `1.0` شروع می‌شود (برای تعدیل‌کننده‌های ضریبی استفاده می‌شود).
- `fixed_modifiers`: با `0.0` شروع می‌شود (برای تعدیل‌کننده‌های ثابت استفاده می‌شود).

##### 3. پردازش پارامترها:
برای هر پارامتر مرتبط با سرویس:
- مقدار ارائه‌شده توسط کاربر را بازیابی کنید یا در صورت عدم ارائه، از مقدار پیش‌فرض استفاده کنید.
- اگر پارامتر اجباری است و مقداری ارائه نشده است، یک خطا ایجاد کنید.
- `ParameterOption` مربوط به مقدار ارائه‌شده را پیدا کنید.
- تعدیل‌کننده را بر اساس نوع پارامتر اعمال کنید:
  - **ضریب:** `multiplier` را در تعدیل‌کننده گزینه ضرب کنید.
  - **ثابت:** تعدیل‌کننده گزینه را به `fixed_modifiers` اضافه کنید.
  - **مقدار کمی:** `multiplier` را در تعدیل‌کننده گزینه و مقدار ارائه‌شده ضرب کنید.

##### 4. محاسبه قیمت نهایی:
- `base_price` را در `multiplier` ضرب کنید.
- `fixed_modifiers` را به نتیجه اضافه کنید.
- اطمینان از این که قیمت نهایی منفی نباشد (در صورت منفی بودن، آن را `0.0` تنظیم کنید).

##### 5. بازگشت قیمت نهایی:
- قیمت محاسبه‌شده را بازگردانید.

#### مثال محاسبه

**ورودی:**
- **سرویس:** کارواش (`base_price = 50 دلار`)
- **پارامترها:**
  - اندازه ماشین: بزرگ (`multiplier = 1.5`)
  - واکس: بله (`fixed_modifier = +10 دلار`)

**محاسبه:**
- `base_price = 50 دلار`
- `multiplier = 1.0 * 1.5 = 1.5` (از اندازه ماشین)
- `fixed_modifiers = 10 دلار` (از واکس)
- `total_price = (50 دلار * 1.5) + 10 دلار = 85 دلار`

**خروجی:**
- **قیمت نهایی:** 85 دلار
```


## Error Handling | مدیریت خطا

The API returns appropriate HTTP status codes and error messages | API کدهای وضعیت HTTP و پیام‌های خطای مناسب را برمی‌گرداند:

- 400: Bad Request (invalid parameters) | درخواست نامعتبر (پارامترهای نامعتبر)
- 404: Not Found | یافت نشد
- 500: Internal Server Error | خطای داخلی سرور

Example error response | مثال پاسخ خطا:
```json
{
    "error": "Required parameter 'service_level' is missing"
}
```

## Database Schema | ساختار پایگاه داده

```sql
CREATE TABLE services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE parameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parameter_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    default_value VARCHAR(255),
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

CREATE TABLE parameter_options (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parameter_id INT NOT NULL,
    value VARCHAR(255) NOT NULL,
    modifier DECIMAL(10, 4) NOT NULL,
    FOREIGN KEY (parameter_id) REFERENCES parameters(id) ON DELETE CASCADE
);

CREATE TABLE price_calculations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    input_params TEXT NOT NULL,
    calculated_price DECIMAL(10, 2) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);
```

##Testing
```pytest test.py -v ```

## Author
[Written by Amir Ahmadabadiha](https://linkedin.com/in/amir-ahmadabadiha-259113175)

with https://claude.ai & Copilot helps as my assistants

