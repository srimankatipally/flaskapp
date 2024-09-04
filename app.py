from flask import Flask, jsonify, request, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orders Management</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        form {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>Orders Management</h1>
    
    <form id="orderForm">
        <h2>Add New Order</h2>
        <label for="customer_id">Customer ID:</label>
        <input type="number" id="customer_id" name="customer_id" required><br><br>
        <label for="order_date">Order Date (YYYY-MM-DD):</label>
        <input type="date" id="order_date" name="order_date" required><br><br>
        <label for="amount">Amount:</label>
        <input type="number" step="0.01" id="amount" name="amount" required><br><br>
        <label for="status">Status:</label>
        <select id="status" name="status" required>
            <option value="Pending">Pending</option>
            <option value="Shipped">Shipped</option>
            <option value="Delivered">Delivered</option>
            <option value="Cancelled">Cancelled</option>
            <option value="Returned">Returned</option>
        </select><br><br>
        <button type="submit">Add Order</button>
    </form>

    <h2>Existing Orders</h2>
    <table id="ordersTable">
        <thead>
            <tr>
                <th>Order ID</th>
                <th>Customer ID</th>
                <th>Order Date</th>
                <th>Amount</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <!-- Orders will be populated here -->
        </tbody>
    </table>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            fetchOrders();

            document.getElementById('orderForm').addEventListener('submit', function(event) {
                event.preventDefault();
                addOrder();
            });
        });

        function fetchOrders() {
            fetch('/orders')
                .then(response => response.json())
                .then(data => {
                    const ordersTableBody = document.getElementById('ordersTable').getElementsByTagName('tbody')[0];
                    ordersTableBody.innerHTML = '';  // Clear existing rows
                    data.forEach(order => {
                        const row = ordersTableBody.insertRow();
                        row.insertCell(0).textContent = order.order_id;
                        row.insertCell(1).textContent = order.customer_id;
                        row.insertCell(2).textContent = order.order_date;
                        row.insertCell(3).textContent = order.amount;
                        row.insertCell(4).textContent = order.status;
                    });
                })
                .catch(error => console.error('Error fetching orders:', error));
        }

        function addOrder() {
            const customer_id = document.getElementById('customer_id').value;
            const order_date = document.getElementById('order_date').value;
            const amount = document.getElementById('amount').value;
            const status = document.getElementById('status').value;

            fetch('/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ customer_id, order_date, amount, status })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error adding order: ' + data.error);
                } else {
                    alert('Order added successfully!');
                    fetchOrders();  // Refresh the orders table
                    document.getElementById('orderForm').reset();  // Reset form
                }
            })
            .catch(error => console.error('Error adding order:', error));
        }
    </script>
</body>
</html>
"""

DB_CONFIG = {
    'dbname': 'sales',
    'user': 'postgres',
    'password': 'root',
    'host': 'localhost', 
    'port': '5433'  
}

def get_db_connection():
    """Creates a connection to the PostgreSQL database."""
    connection = psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    return connection

@app.route('/')
def home():
    """Serve the HTML page."""
    return render_template_string(HTML_PAGE)

@app.route('/orders', methods=['GET'])
def fetch_orders():
    """Fetch all orders from the database and return as JSON."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM orders;")
        orders = cursor.fetchall()
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/orders', methods=['POST'])
def add_order():
    """Add a new order to the database."""
    try:
        data = request.json  

        customer_id = data.get('customer_id')
        order_date = data.get('order_date')
        amount = data.get('amount')
        status = data.get('status')

        if not all([customer_id, order_date, amount, status]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO orders (customer_id, order_date, amount, status)
        VALUES (%s, %s, %s, %s) RETURNING order_id;
        """
        cursor.execute(insert_query, (customer_id, order_date, amount, status))
        connection.commit()

        new_order_id = cursor.fetchone()[0]
        return jsonify({'message': 'Order added successfully', 'order_id': new_order_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
