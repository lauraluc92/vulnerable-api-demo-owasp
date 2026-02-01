import os
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker 
from sqlalchemy.orm import Session
from app_secure.database.base import Base 
from app_secure.models.user import User 
from app_secure.models.product import Product
from app_secure.models.order import Order 
from app_secure.models.report import Report
from app_secure.core.hashing import get_password_hash
from datetime import datetime

#Nom BDD sécurisée
SQLALCHEMY_DATABASE_URL = "sqlite:///./secure_api.db"
RESET = os.getenv("RESET") == "True"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def populate_db(db: Session): 
    fake = Faker('fr_FR')
    
    # 1. Création utilisateurs
    created_users = []

    admin_user = User(
        username="admin", 
        email="admin@shop.com", 
        hashed_password=get_password_hash("password123"),
        role="admin",
        phone=fake.phone_number(),
        address=fake.address(),
    )
    db.add(admin_user)
    created_users.append(admin_user)
    for i in range(1, 11):
        user = User(
            username=f"user{i}", 
            email=fake.email(), 
            hashed_password=get_password_hash("password123"),
            role="user",
            phone=fake.phone_number(),
            address=fake.address(),)
        db.add(user)
        created_users.append(user)
    
    bad_seller= User(
        id=666,
        username=f"badguy",
        email="badguy@free.fr",
        hashed_password=get_password_hash("thisismypwd!"),
        role="user",
        phone=fake.phone_number(),
        address=fake.address(),)
    db.add(bad_seller)
    created_users.append(bad_seller)
    db.commit() 

    # 2. Création produits
    print("Création des produits (Secure DB)...")
    created_products = [] 
    for i in range(1, 51):
        seller = created_users[i % len(created_users)] 
        product = Product(
            name=f"{fake.word(ext_word_list=['iFone 16', 'Air Fryer', 'Headphones', 'Computer', 'Barby Doll','Camera', 'T-Shirt', 'Disk', 'Vinyl', 'New Singer Album', 'Cute Pillow'])}",
            price=round(fake.random_int(min=5, max=200), 2),
            description=fake.sentence(nb_words=10),
            blocked=False,
            seller_id=seller.id,
            stock=100 
            )
        db.add(product)
        created_products.append(product)
    blocked_product = Product(
        id=666,
        name=f"Cheap used iFone",
        price=50,
        description="Great iFone, good quality, very affordable",
        blocked=True,
        seller_id=666,
        stock=50
    )
    db.add(blocked_product)
    created_products.append(blocked_product)
    star_product = Product(
        id=999,
        name="PlayStati 6 - Limited Edition",
        price=899.99,
        description="The console everyone wants. Ultra-limited stock!",
        seller_id=admin_user.id,
        blocked=False,
        stock=11)
    db.add(star_product)
    
    created_products.append(star_product)
    
    db.commit()

    # 3. Création signalement
    existing_report = db.query(Report).filter_by(product_id=666).first()
    if not existing_report:
        user1 = db.query(User).filter_by(username="user1").first()
        product_target = db.query(Product).filter_by(id=666).first()
        if user1 and product_target:
            fake_report = Report(
                id=1,
                product_id=666,
                reporter_id=user1.id,
                reason="WARNING: This product is a dangerous counterfeit. Do not purchase!",
                timestamp=datetime.now()
            )
            db.add(fake_report)
            db.commit()
            print("signalement initial de User1 créé en BDD.")

    # 4. Création commandes
    print(f"Ajout BDD SÉCURISÉE : {len(created_users)} users et {len(created_products)} produits")
    print("Génération de commandes aléatoires...")
    random_product = random.choice(created_products)
    qty = random.randint(1, 3)
    #ne pas commander un produit bloqué ou rupture stock
    if not (random_product.blocked or random_product.stock < qty):
        order = Order(
            buyer_id=5,
            product_id=random_product.id,
            quantity=qty
            )
        random_product.stock -= qty
        order2 = Order(
            buyer_id=1,
            product_id=random_product.id,
            quantity=qty
            )
        random_product.stock -= qty
        db.add(order)
        db.add(order2)
    for _ in range(20): 
        random_buyer = random.choice(created_users)
        random_product = random.choice(created_products)
        qty = random.randint(1, 3)
        #logique métier : pas de commande si bloqué ou stock vide
        if random_product.blocked or random_product.stock < qty:
            continue
        order = Order(
            buyer_id=random_buyer.id,
            product_id=random_product.id,
            quantity=qty
        )
        random_product.stock -= qty
        db.add(order)
    db.commit()
    print("Commandes ajoutées.")

def init_db():
    #pour initialiser la base sécurisée, on supprime si demandé et on recrée
    if RESET:
        print("RESET SECURE DATABASE")
        Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine) 
    db = SessionLocal()
    if db.query(User).count() == 0:
        populate_db(db)
    db.close()
    print("Secure Database initialized and populated.")