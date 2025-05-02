from flask import Flask, render_template, redirect
import os

app = Flask(__name__, 
            template_folder='templates')

@app.route('/')
def direct_admin():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Direct Admin Access</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
            .btn-portal { width: 100%; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="text-center">Admin Dashboard Direct Access</h1>
                    <p class="text-center">Access the admin features directly without authentication</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 offset-md-3">
                    <div class="card">
                        <div class="card-header">
                            <h3>Main Access Points</h3>
                        </div>
                        <div class="card-body">
                            <a href="/dashboard" class="btn btn-primary btn-portal">Admin Dashboard</a>
                            <a href="/products" class="btn btn-success btn-portal">Product Management</a>
                            <a href="/reviews" class="btn btn-info btn-portal">Review Management</a>
                            <a href="/users" class="btn btn-warning btn-portal">User Management</a>
                            <a href="/reports" class="btn btn-danger btn-portal">Sentiment Reports</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
            .stat-card { padding: 20px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1>Admin Dashboard</h1>
                    <a href="/" class="btn btn-outline-secondary mb-3">Back to Admin Portal</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body stat-card bg-primary text-white">
                            <h3>Products</h3>
                            <h2>25</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body stat-card bg-success text-white">
                            <h3>Reviews</h3>
                            <h2>142</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body stat-card bg-info text-white">
                            <h3>Users</h3>
                            <h2>18</h2>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>Sentiment Overview</h3>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label>Positive Sentiment</label>
                                <div class="progress">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: 65%">65%</div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label>Neutral Sentiment</label>
                                <div class="progress">
                                    <div class="progress-bar bg-warning" role="progressbar" style="width: 20%">20%</div>
                                </div>
                            </div>
                            <div>
                                <label>Negative Sentiment</label>
                                <div class="progress">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: 15%">15%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/products')
def products():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Product Management</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
            table { color: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1>Product Management</h1>
                    <a href="/" class="btn btn-outline-secondary mb-3">Back to Admin Portal</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h3>Product List</h3>
                            <button class="btn btn-primary">Add New Product</button>
                        </div>
                        <div class="card-body">
                            <table class="table table-dark">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Category</th>
                                        <th>Price</th>
                                        <th>Reviews</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>680e0a9c...</td>
                                        <td>Amazon Kindle E-Reader</td>
                                        <td>Electronics</td>
                                        <td>$159.79</td>
                                        <td>9</td>
                                        <td>
                                            <button class="btn btn-sm btn-info">View</button>
                                            <button class="btn btn-sm btn-warning">Edit</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>680e1ec0...</td>
                                        <td>Echo Dot (4th Gen)</td>
                                        <td>Electronics</td>
                                        <td>$49.99</td>
                                        <td>3</td>
                                        <td>
                                            <button class="btn btn-sm btn-info">View</button>
                                            <button class="btn btn-sm btn-warning">Edit</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>680e1ec2...</td>
                                        <td>Amazon Fire HD 10</td>
                                        <td>Electronics</td>
                                        <td>$149.99</td>
                                        <td>3</td>
                                        <td>
                                            <button class="btn btn-sm btn-info">View</button>
                                            <button class="btn btn-sm btn-warning">Edit</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/reviews')
def reviews():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Review Management</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
            table { color: #f8f9fa; }
            .sentiment-positive { color: #28a745; }
            .sentiment-neutral { color: #ffc107; }
            .sentiment-negative { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1>Review Management</h1>
                    <a href="/" class="btn btn-outline-secondary mb-3">Back to Admin Portal</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>Review List</h3>
                        </div>
                        <div class="card-body">
                            <table class="table table-dark">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Product</th>
                                        <th>Author</th>
                                        <th>Rating</th>
                                        <th>Sentiment</th>
                                        <th>Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>680e230...</td>
                                        <td>Amazon Kindle E-Reader</td>
                                        <td>John D.</td>
                                        <td>5.0</td>
                                        <td><span class="sentiment-positive">Positive (0.92)</span></td>
                                        <td>2025-03-15</td>
                                        <td>
                                            <button class="btn btn-sm btn-info">View</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>680e235...</td>
                                        <td>Echo Dot (4th Gen)</td>
                                        <td>Sarah M.</td>
                                        <td>4.0</td>
                                        <td><span class="sentiment-positive">Positive (0.78)</span></td>
                                        <td>2025-03-18</td>
                                        <td>
                                            <button class="btn btn-sm btn-info">View</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>680e240...</td>
                                        <td>Amazon Fire HD 10</td>
                                        <td>Robert J.</td>
                                        <td>2.0</td>
                                        <td><span class="sentiment-negative">Negative (0.65)</span></td>
                                        <td>2025-03-20</td>
                                        <td>
                                            <button class="btn btn-sm btn-info">View</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/users')
def users():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Management</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
            table { color: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1>User Management</h1>
                    <a href="/" class="btn btn-outline-secondary mb-3">Back to Admin Portal</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h3>User List</h3>
                            <button class="btn btn-primary">Add New User</button>
                        </div>
                        <div class="card-body">
                            <table class="table table-dark">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Username</th>
                                        <th>Email</th>
                                        <th>Created</th>
                                        <th>Admin</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>680e514...</td>
                                        <td>admin</td>
                                        <td>admin@example.com</td>
                                        <td>2025-04-27</td>
                                        <td>Yes</td>
                                        <td>
                                            <button class="btn btn-sm btn-warning">Edit</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>680e520...</td>
                                        <td>user1</td>
                                        <td>user1@example.com</td>
                                        <td>2025-04-28</td>
                                        <td>No</td>
                                        <td>
                                            <button class="btn btn-sm btn-warning">Edit</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>680e525...</td>
                                        <td>user2</td>
                                        <td>user2@example.com</td>
                                        <td>2025-04-29</td>
                                        <td>No</td>
                                        <td>
                                            <button class="btn btn-sm btn-warning">Edit</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/reports')
def reports():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentiment Reports</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1>Sentiment Reports</h1>
                    <a href="/" class="btn btn-outline-secondary mb-3">Back to Admin Portal</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>Overall Sentiment</h3>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label>Positive Sentiment</label>
                                <div class="progress">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: 65%">65%</div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label>Neutral Sentiment</label>
                                <div class="progress">
                                    <div class="progress-bar bg-warning" role="progressbar" style="width: 20%">20%</div>
                                </div>
                            </div>
                            <div>
                                <label>Negative Sentiment</label>
                                <div class="progress">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: 15%">15%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>Top Products by Sentiment</h3>
                        </div>
                        <div class="card-body">
                            <table class="table table-dark">
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Positive Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Echo Dot (4th Gen)</td>
                                        <td>1.00</td>
                                    </tr>
                                    <tr>
                                        <td>Amazon Fire HD 10</td>
                                        <td>1.00</td>
                                    </tr>
                                    <tr>
                                        <td>Amazon Kindle E-Reader</td>
                                        <td>0.89</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>Hype vs Reality</h3>
                        </div>
                        <div class="card-body">
                            <p>Compare marketing claims against real customer sentiment</p>
                            <a href="/hype-reality" class="btn btn-primary">View Hype vs Reality Analysis</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/hype-reality')
def hype_reality():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hype vs Reality</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { padding: 20px; background-color: #212529; color: #f8f9fa; }
            .card { margin-bottom: 20px; background-color: #2c3034; color: #f8f9fa; border-color: #495057; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row mb-4">
                <div class="col-12">
                    <h1>Hype vs Reality Analysis</h1>
                    <a href="/reports" class="btn btn-outline-secondary mb-3">Back to Reports</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h3>Amazon Echo Dot (4th Gen)</h3>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h4>Marketing Claims</h4>
                                    <ul class="list-group mb-3">
                                        <li class="list-group-item bg-dark text-white">"Crisp, rich sound quality"</li>
                                        <li class="list-group-item bg-dark text-white">"Voice control your smart home"</li>
                                        <li class="list-group-item bg-dark text-white">"Designed to protect your privacy"</li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h4>Customer Sentiment</h4>
                                    <div class="mb-3">
                                        <label>Sound Quality</label>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" role="progressbar" style="width: 85%">85%</div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label>Smart Home Control</label>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" role="progressbar" style="width: 90%">90%</div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label>Privacy</label>
                                        <div class="progress">
                                            <div class="progress-bar bg-warning" role="progressbar" style="width: 60%">60%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3>Amazon Fire HD 10 Tablet</h3>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h4>Marketing Claims</h4>
                                    <ul class="list-group mb-3">
                                        <li class="list-group-item bg-dark text-white">"Vibrant HD display"</li>
                                        <li class="list-group-item bg-dark text-white">"All-day battery life"</li>
                                        <li class="list-group-item bg-dark text-white">"Fast and responsive performance"</li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h4>Customer Sentiment</h4>
                                    <div class="mb-3">
                                        <label>Display Quality</label>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" role="progressbar" style="width: 80%">80%</div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label>Battery Life</label>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" role="progressbar" style="width: 75%">75%</div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label>Performance</label>
                                        <div class="progress">
                                            <div class="progress-bar bg-danger" role="progressbar" style="width: 45%">45%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("DIRECT_ADMIN_PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)