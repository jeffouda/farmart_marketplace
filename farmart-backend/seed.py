"""
Database Seed Script for Farmart
Populates the database with sample livestock and users for testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, UserProfile, Livestock

# VERIFIED SAFE Unsplash image URLs
# These IDs have been checked to be actual animals
ANIMAL_IMAGES = {
    "Goat": [
        "https://images.unsplash.com/photo-1524024973431-2ad916746881?w=800&q=80", # White goat profile
        "https://images.unsplash.com/photo-1533318087102-b3ad366ed041?w=800&q=80", # Funny brown goat
        "https://images.unsplash.com/photo-1560731126-25b2dc04c6d2?w=800&q=80", # Goat eating grass
    ],
    "Cattle": [
        "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?w=800&q=80", # Highland cow
        "https://images.unsplash.com/photo-1546445317-29f4545e9d53?w=800&q=80", # Brown milk cow
        "https://images.unsplash.com/photo-1500595046743-cd271d694e30?w=800&q=80", # Herd in field
        "https://images.unsplash.com/photo-1596733430284-f7437764b1a9?w=800&q=80", # Black and white cow header
    ],
    "Sheep": [
        "https://images.unsplash.com/photo-1484557985045-edf25e08da73?w=800&q=80", # Sheep face closeup
        "https://images.unsplash.com/photo-1533415648777-407b626eb0fa?w=800&q=80", # Flock of sheep
        "https://images.unsplash.com/photo-1516631885956-6a2c26db467b?w=800&q=80", # White lamb
    ],
    "Pig": [
        "https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=800&q=80", # Piglet on grass
        "https://images.unsplash.com/photo-1592754862816-1a21a4ea2281?w=800&q=80", # Pigs eating
    ],
    "Chicken": [
        "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=800&q=80", # White chicken
        "https://images.unsplash.com/photo-1569428034239-f9565e32e224?w=800&q=80", # Brown hen
        "https://images.unsplash.com/photo-1612170153139-6f881ff067e0?w=800&q=80", # Colorful rooster
    ],
    "Rabbit": [
        "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=800&q=80", # White rabbit
        "https://images.unsplash.com/photo-1535241749838-299277b6305f?w=800&q=80", # Brown bunny on grass
    ],
    "Donkey": [
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80", # Grey donkey head
        "https://images.unsplash.com/photo-1518386377785-3e284a1d4085?w=800&q=80", # Two donkeys in field
    ],
}


# User-provided specific breed images
BREED_IMAGES = {
    "Somali Donkey": "https://i.ytimg.com/vi/pX7JjknR2ts/maxresdefault.jpg",
    "Kenyan Donkey": "https://bioengineer.org/wp-content/uploads/2025/09/Evaluating-Impact-of-Environment-on-Kenyan-Donkey-Welfare.jpg",
    "Sasso": "https://zootecnica.it/wp-content/uploads/2025/07/Rainbow-X_Europe.jpg",
    "Kuroiler": "https://i.ytimg.com/vi/AdrO11-MXYk/maxresdefault.jpg?sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgXShKMA8=&rs=AOn4CLBCxEpX3sMCK2DqSsgJY4V435SBTA",
    "Merino": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Poll_Merino.jpg/960px-Poll_Merino.jpg",
    "Zebu": "https://breeds.okstate.edu/cattle/site-files/images/miniature-zebu-800x600.jpg",
    "Saanen": "https://media.licdn.com/dms/image/v2/D4D12AQH7TLHWy8IsxQ/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1713698689827?e=2147483647&v=beta&t=N45UXimNgc_n5RlarUSAc0GWib5gOYi_7-YeMc97nww",
    "Toggenburg": "https://avatars.dzeninfra.ru/get-zen_doc/1686199/pub_5d5cdf4e97b5d400ad6ab8ec_5d5ce017e6cb9b00ade0428f/scale_1200",
    "Jersey": "https://i.pinimg.com/originals/0a/1c/c8/0a1cc8f3046019c04415c433225fc001.jpg",
}

def get_image_for_animal(animal_type, breed=None, index=0):
    """Get an image URL for the given animal type or specific breed."""
    # Check for specific breed image first
    if breed and breed in BREED_IMAGES:
        return BREED_IMAGES[breed]
        
    # Fallback to generic animal type images
    images = ANIMAL_IMAGES.get(animal_type, [])
    if images:
        return images[index % len(images)]
    return None


def seed_database():
    """Seed the database with sample data."""
    app = create_app()
    
    with app.app_context():
        print("Starting database seed...")
        
        # Check if data already exists
        if User.query.filter_by(role="farmer").count() > 0:
            print("Database already has farmer data. Skipping seed to avoid duplicates.")
            print("To re-seed, clear the database first.")
            return
        
        # Create sample farmers
        farmers_data = [
            {
                "email": "john.mwangi@farmart.co.ke",
                "phone_number": "254712345001",
                "first_name": "John",
                "last_name": "Mwangi",
                "password": "FarmerPass123!",
                "location": "Kiambu County"
            },
            {
                "email": "mary.wanjiku@farmart.co.ke",
                "phone_number": "254712345002",
                "first_name": "Mary",
                "last_name": "Wanjiku",
                "password": "FarmerPass123!",
                "location": "Nakuru County"
            },
            {
                "email": "peter.ochieng@farmart.co.ke",
                "phone_number": "254712345003",
                "first_name": "Peter",
                "last_name": "Ochieng",
                "password": "FarmerPass123!",
                "location": "Kisumu County"
            },
            {
                "email": "grace.njeri@farmart.co.ke",
                "phone_number": "254712345004",
                "first_name": "Grace",
                "last_name": "Njeri",
                "password": "FarmerPass123!",
                "location": "Nyeri County"
            },
            {
                "email": "james.kipchoge@farmart.co.ke",
                "phone_number": "254712345005",
                "first_name": "James",
                "last_name": "Kipchoge",
                "password": "FarmerPass123!",
                "location": "Uasin Gishu County"
            },
        ]
        
        farmers = []
        for data in farmers_data:
            farmer = User(
                email=data["email"],
                phone_number=data["phone_number"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role="farmer",
                is_active=True,
                is_verified=True
            )
            farmer.set_password(data["password"])
            db.session.add(farmer)
            db.session.flush()
            
            # Create profile
            profile = UserProfile(
                user_id=farmer.id,
                location=data["location"],
                rating=4.0 + (hash(data["email"]) % 10) / 10,
                total_sales=hash(data["email"]) % 50
            )
            db.session.add(profile)
            farmers.append(farmer)
        
        print(f"Created {len(farmers)} farmers")
        
        # Create sample buyer
        buyer = User(
            email="buyer@test.com",
            phone_number="254712345100",
            first_name="Test",
            last_name="Buyer",
            role="buyer",
            is_active=True,
            is_verified=True
        )
        buyer.set_password("BuyerPass123!")
        db.session.add(buyer)
        print("Created 1 test buyer")
        
        # Sample livestock data - diverse Kenyan livestock with image indices
        livestock_data = [
            # Goats - including Kiambu
            {"animal_type": "Goat", "breed": "Galla", "weight": 35, "age_months": 18, "price": 12000, "location": "Kiambu", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Goat", "breed": "Alpine", "weight": 40, "age_months": 24, "price": 15000, "location": "Kiambu", "farmer_idx": 0, "img_idx": 1},
            {"animal_type": "Goat", "breed": "Toggenburg", "weight": 38, "age_months": 20, "price": 18000, "location": "Nyeri", "farmer_idx": 3, "img_idx": 2},
            {"animal_type": "Goat", "breed": "Boer", "weight": 45, "age_months": 30, "price": 25000, "location": "Nakuru", "farmer_idx": 1, "img_idx": 0},
            {"animal_type": "Goat", "breed": "Small East African", "weight": 25, "age_months": 12, "price": 8000, "location": "Kisumu", "farmer_idx": 2, "img_idx": 1},
            {"animal_type": "Goat", "breed": "Saanen", "weight": 42, "age_months": 24, "price": 22000, "location": "Kiambu", "farmer_idx": 0, "img_idx": 2},
            
            # Cattle
            {"animal_type": "Cattle", "breed": "Friesian", "weight": 450, "age_months": 36, "price": 120000, "location": "Kiambu", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Cattle", "breed": "Ayrshire", "weight": 420, "age_months": 30, "price": 95000, "location": "Nakuru", "farmer_idx": 1, "img_idx": 1},
            {"animal_type": "Cattle", "breed": "Jersey", "weight": 380, "age_months": 28, "price": 85000, "location": "Nyeri", "farmer_idx": 3, "img_idx": 2},
            {"animal_type": "Cattle", "breed": "Guernsey", "weight": 400, "age_months": 32, "price": 90000, "location": "Eldoret", "farmer_idx": 4, "img_idx": 3},
            {"animal_type": "Cattle", "breed": "Sahiwal", "weight": 350, "age_months": 24, "price": 75000, "location": "Machakos", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Cattle", "breed": "Boran", "weight": 380, "age_months": 30, "price": 80000, "location": "Laikipia", "farmer_idx": 1, "img_idx": 1},
            {"animal_type": "Cattle", "breed": "Zebu", "weight": 300, "age_months": 24, "price": 55000, "location": "Kajiado", "farmer_idx": 2, "img_idx": 2},
            
            # Sheep
            {"animal_type": "Sheep", "breed": "Dorper", "weight": 55, "age_months": 18, "price": 18000, "location": "Narok", "farmer_idx": 1, "img_idx": 0},
            {"animal_type": "Sheep", "breed": "Red Maasai", "weight": 45, "age_months": 15, "price": 12000, "location": "Kajiado", "farmer_idx": 2, "img_idx": 1},
            {"animal_type": "Sheep", "breed": "Merino", "weight": 50, "age_months": 20, "price": 22000, "location": "Nakuru", "farmer_idx": 1, "img_idx": 2},
            {"animal_type": "Sheep", "breed": "Hampshire", "weight": 60, "age_months": 24, "price": 25000, "location": "Kiambu", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Sheep", "breed": "Corriedale", "weight": 52, "age_months": 18, "price": 20000, "location": "Nyandarua", "farmer_idx": 3, "img_idx": 1},
            
            # Pigs
            {"animal_type": "Pig", "breed": "Large White", "weight": 90, "age_months": 8, "price": 25000, "location": "Kiambu", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Pig", "breed": "Landrace", "weight": 85, "age_months": 7, "price": 22000, "location": "Nakuru", "farmer_idx": 1, "img_idx": 1},
            {"animal_type": "Pig", "breed": "Duroc", "weight": 95, "age_months": 9, "price": 28000, "location": "Kisumu", "farmer_idx": 2, "img_idx": 0},
            {"animal_type": "Pig", "breed": "Hampshire", "weight": 88, "age_months": 8, "price": 24000, "location": "Nyeri", "farmer_idx": 3, "img_idx": 1},
            
            # Chickens
            {"animal_type": "Chicken", "breed": "Kienyeji", "weight": 2, "age_months": 6, "price": 800, "location": "Murang'a", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Chicken", "breed": "Kuroiler", "weight": 3, "age_months": 4, "price": 1200, "location": "Kiambu", "farmer_idx": 0, "img_idx": 1},
            {"animal_type": "Chicken", "breed": "Rainbow Rooster", "weight": 3, "age_months": 5, "price": 1500, "location": "Nakuru", "farmer_idx": 1, "img_idx": 2},
            {"animal_type": "Chicken", "breed": "KARI Improved", "weight": 2, "age_months": 5, "price": 1000, "location": "Kisumu", "farmer_idx": 2, "img_idx": 0},
            {"animal_type": "Chicken", "breed": "Sasso", "weight": 4, "age_months": 4, "price": 1800, "location": "Eldoret", "farmer_idx": 4, "img_idx": 1},
            
            # Rabbits (Other)
            {"animal_type": "Rabbit", "breed": "New Zealand White", "weight": 4, "age_months": 6, "price": 2500, "location": "Kiambu", "farmer_idx": 0, "img_idx": 0},
            {"animal_type": "Rabbit", "breed": "California White", "weight": 4, "age_months": 5, "price": 2200, "location": "Nyeri", "farmer_idx": 3, "img_idx": 1},
            {"animal_type": "Rabbit", "breed": "Chinchilla", "weight": 3, "age_months": 4, "price": 3000, "location": "Nakuru", "farmer_idx": 1, "img_idx": 0},
            
            # Donkeys
            {"animal_type": "Donkey", "breed": "Kenyan Donkey", "weight": 180, "age_months": 48, "price": 35000, "location": "Machakos", "farmer_idx": 2, "img_idx": 0},
            {"animal_type": "Donkey", "breed": "Somali Donkey", "weight": 200, "age_months": 60, "price": 40000, "location": "Garissa", "farmer_idx": 2, "img_idx": 0},
        ]
        
        for data in livestock_data:
            image_url = get_image_for_animal(data["animal_type"], data.get("breed"), data["img_idx"])
            
            livestock = Livestock(
                farmer_id=farmers[data["farmer_idx"]].id,
                animal_type=data["animal_type"],
                breed=data["breed"],
                weight=data["weight"],
                age_months=data["age_months"],
                price=data["price"],
                location=data["location"],
                is_available=True,
                images=[image_url] if image_url else [],
                description=f"Quality {data['breed']} {data['animal_type']} from {data['location']}. Well-fed and healthy.",
                health_notes="Vaccinated against common diseases. Regular deworming done."
            )
            db.session.add(livestock)
        
        print(f"Created {len(livestock_data)} livestock listings with images")
        
        # Commit all changes
        db.session.commit()
        print("\nDatabase seeded successfully!")
        print("\nTest accounts:")
        print("  Farmers: john.mwangi@farmart.co.ke (and 4 others)")
        print("  Buyer: buyer@test.com")
        print("  Password for all: See above in script")
        print(f"\nLocations included: Kiambu, Nakuru, Nyeri, Kisumu, Eldoret, Machakos, Kajiado, Narok, Laikipia, Nyandarua, Murang'a, Garissa")
        print(f"Animal types: Goat, Cattle, Sheep, Pig, Chicken, Rabbit, Donkey")


if __name__ == "__main__":
    seed_database()
