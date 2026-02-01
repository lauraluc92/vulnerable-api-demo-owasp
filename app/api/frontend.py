from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def render_app(query: str = ""):
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ShopVulnerable</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ background-color: #f8f9fa; padding-top: 20px; padding-bottom: 50px; }}
            .hidden {{ display: none !important; }}
            .xss-zone {{ background: #ffe6e6; border: 1px solid red; padding: 15px; margin-top: 20px; border-radius: 5px; color: #721c24; }}
            .card {{ transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
            .nav-btn {{ margin-left: 10px; }}
        </style>
    </head>
    <body>

        <div class="container">
            
            <div class="d-flex justify-content-between align-items-center mb-5 p-3 bg-white rounded shadow-sm">
                <h1 class="text-primary m-0"><i class="fas fa-bug"></i> Shop<span class="text-danger fw-bold">Vulnerable</span></h1>
                
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
                            <i class="fas fa-user-circle"></i> Logged In
                        </span>
                        
                        <button class="btn btn-outline-primary nav-btn" onclick="loadProducts()">
                            <i class="fas fa-box"></i> Catalog
                        </button>
                        
                        <button class="btn btn-primary nav-btn" onclick="triggerLoadOrders()">
                            <i class="fas fa-shopping-cart"></i> My Orders
                        </button>
                        
                        <button class="btn btn-danger nav-btn" onclick="logout()">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm p-4 mb-5 border-danger">
                <h4 class="text-danger"><i class="fas fa-search"></i> Product Search</h4>
                <p class="text-muted small">
                    Type a product name... or a malicious script.<br>
                    <em>XSS Payload: <code>&lt;script&gt;alert(localStorage.getItem('access_token'))&lt;/script&gt;</code></em>
                </p>
                
                <form action="/" method="GET">
                    <div class="input-group">
                        <input type="text" class="form-control" name="query" value="{query}" placeholder="Search...">
                        <button class="btn btn-danger" type="submit">Search</button>
                    </div>
                </form>

                {'<div class="xss-zone">Result for: <b>' + query + '</b> <br><i>No product found.</i></div>' if query else ''}
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 id="section-title" class="fw-bold text-secondary">Product Catalog</h3>
            </div>
            
            <div id="content-list" class="row"></div>

        </div>

        <script>
            window.onload = () => {{
                checkLogin();
                loadProducts();
            }};

            function checkLogin() {{
                const token = localStorage.getItem("access_token");

                if (token) {{
                    document.getElementById("auth-buttons").classList.add("hidden");
                    document.getElementById("user-info").classList.remove("hidden");
                }} else {{
                    document.getElementById("auth-buttons").classList.remove("hidden");
                    document.getElementById("user-info").classList.add("hidden");
                }}
            }}

            async function login() {{
                const u = document.getElementById("username").value;
                const p = document.getElementById("password").value;
                const formData = new URLSearchParams();
                formData.append('username', u);
                formData.append('password', p);

                try {{
                    const res = await fetch('/auth/login', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                        body: formData
                    }});
                    
                    if (res.ok) {{
                        const data = await res.json();
                        localStorage.setItem("access_token", data.access_token);
                        localStorage.setItem("user_id", data.user_id); 
                        location.reload(); 
                    }} else {{ alert("Login error"); }}
                }} catch (e) {{ console.error(e); alert("Network error"); }}
            }}

            async function logout() {{
        
            const token = localStorage.getItem("access_token");

                try {{
                    await fetch('/auth/logout', {{
                        method: 'POST',
                        headers: {{ 
                            "Authorization": "Bearer " + token,
                            "Content-Type": "application/json"
                        }}
                    }});
                }} catch (e) {{
                    console.log("Server did not respond, but clearing token locally anyway.");
                }}
                localStorage.clear();
                location.reload();
            }}
            function triggerLoadOrders() {{
                const token = localStorage.getItem("access_token");
                if(!token) {{ alert("Please log in"); return; }}
                loadOrders(token);
            }}

            async function loadProducts() {{
                document.getElementById("section-title").innerText = "Product Catalog";
                const container = document.getElementById("content-list");
                container.innerHTML = '<div class="col-12 text-center text-muted">Loading products...</div>';
                
                try {{
                    const res = await fetch('/products');
                    
                    if (res.ok) {{
                        const products = await res.json();
                        container.innerHTML = "";
                        
                        products.forEach(p => {{
                            container.innerHTML += `
                                <div class="col-md-4 mb-4">
                                    <div class="card h-100 border-0 shadow-sm">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-start">
                                                <h5 class="card-title text-primary">${{p.name}}</h5>
                                                <span class="badge bg-success">${{p.price}} €</span>
                                            </div>
                                            
                                            ${{p.blocked ? '<div class="badge bg-danger mb-2 w-100">🚫 BLOCKED BY ADMIN</div>' : ''}}
                                            
                                            <p class="card-text small text-muted">${{p.description || 'No description'}}</p>
                                            <hr>
                                            <small class="text-muted d-block">
                                                <i class="fas fa-store"></i> Seller: <strong>${{p.seller.username}}</strong>
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }});
                    }}
                }} catch (e) {{ 
                    container.innerHTML = '<div class="alert alert-danger">Error loading products.</div>';
                }}
            }}

            async function loadOrders(token) {{
                document.getElementById("section-title").innerText = "🛒 My Orders";
                const container = document.getElementById("content-list");
                container.innerHTML = '<div class="col-12 text-center text-muted">Loading your orders...</div>';

                const userId = localStorage.getItem("user_id");

                if (!userId) {{
                    container.innerHTML = '<div class="alert alert-warning">Error: User ID not found.</div>';
                    return;
                }}

                try {{
                    const res = await fetch('/orders/user/' + userId, {{
                        headers: {{ "Authorization": "Bearer " + token }}
                    }});
                    
                    if (res.ok) {{
                        const orders = await res.json();
                        
                        if(orders.length === 0) {{
                            container.innerHTML = '<div class="col-12"><div class="alert alert-info">No orders found.</div></div>';
                            return;
                        }}
                        
                        container.innerHTML = "";
                        orders.forEach(o => {{
                            const prodName = o.product ? o.product.name : "Deleted product";
                            const prodPrice = o.product ? o.product.price : 0;
                            const total = (prodPrice * o.quantity).toFixed(2);
                            
                            container.innerHTML += `
                                <div class="col-md-6 mb-3">
                                    <div class="card border-primary h-100">
                                        <div class="card-header bg-transparent border-primary d-flex justify-content-between">
                                            <span>Order #<b>${{o.id}}</b></span>
                                            <small class="text-muted">${{o.created_at}}</small>
                                        </div>
                                        <div class="card-body">
                                            <h5 class="card-title text-dark">${{prodName}}</h5>
                                            <p class="card-text">
                                                Quantity: <b>${{o.quantity}}</b><br>
                                                Buyer ID: <span class="badge bg-warning text-dark">${{o.buyer_id}}</span>
                                            </p>
                                        </div>
                                        <div class="card-footer bg-light d-flex justify-content-between align-items-center">
                                            <small class="text-muted">Total</small>
                                            <span class="fw-bold text-success fs-5">${{total}} €</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }});
                    }} else {{
                        container.innerHTML = '<div class="alert alert-danger">Access denied or server error.</div>';
                    }}
                }} catch (e) {{ 
                    container.innerHTML = '<div class="alert alert-danger">Network error.</div>';
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_content