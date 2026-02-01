from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import html 

router = APIRouter()

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def render_app(query: str = ""):
    
    safe_query = html.escape(query)
    
    
    search_result_html = ""
    if query:
        search_result_html = f'<div class="safe-zone">Result for: <b>{safe_query}</b> <br><i>No product found (but the script did not execute!).</i></div>'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ShopSecure</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ background-color: #e8f5e9; padding-top: 20px; padding-bottom: 50px; }}
            .hidden {{ display: none !important; }}
            .safe-zone {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin-top: 20px; border-radius: 5px; color: #155724; }}
            .card {{ transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
            .nav-btn {{ margin-left: 10px; }}
        </style>
    </head>
    <body>

        <div class="container">
            
            <div class="d-flex justify-content-between align-items-center mb-5 p-3 bg-white rounded shadow-sm">
                <h1 class="text-success m-0"><i class="fas fa-shield-alt"></i> Shop<span class="text-success fw-bold">Secure</span></h1>
                
                <div>
                    <div id="auth-buttons">
                        <div class="input-group">
                            <input type="text" id="username" placeholder="user1" class="form-control" value="user1">
                            <input type="password" id="password" placeholder="password123" class="form-control" value="password123">
                            <button class="btn btn-success" onclick="login()">Login</button>
                        </div>
                    </div>

                    <div id="user-info" class="hidden d-flex align-items-center">
                        <span class="fw-bold me-3 text-secondary">
                            <i class="fas fa-user-check"></i> Logged In (Secure)
                        </span>
                        
                        <button class="btn btn-outline-success nav-btn" onclick="loadProducts()">
                            <i class="fas fa-box"></i> Catalog
                        </button>
                        
                        <button class="btn btn-success nav-btn" onclick="triggerLoadOrders()">
                            <i class="fas fa-shopping-cart"></i> My Orders
                        </button>
                        
                        <button class="btn btn-danger nav-btn" onclick="logout()">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm p-4 mb-5 border-success">
                <h4 class="text-success"><i class="fas fa-search"></i> Product Search (XSS Protected)</h4>
                <p class="text-muted small">
                    Even if you try to inject code here, it will be escaped.<br>
                    <em>Test with: <code>&lt;script&gt;alert('Hacked')&lt;/script&gt;</code></em>
                </p>
                
                <form action="/" method="GET">
                    <div class="input-group">
                        <input type="text" class="form-control" name="query" value="{safe_query}" placeholder="Search...">
                        <button class="btn btn-success" type="submit">Search</button>
                    </div>
                </form>

                {search_result_html}
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 id="section-title" class="fw-bold text-secondary">Product Catalog</h3>
            </div>
            
            <div id="content-list" class="row"></div>

        </div>

        <script src="/static/app.js"></script> 
    </body>
    </html>
    """
    return html_content