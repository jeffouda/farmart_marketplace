from flask import Blueprint, request, jsonify
from app import db
from app.models import Livestock, Vaccination
from app.utils.decorators import farmer_required
from flask_jwt_extended import get_jwt_identity
from datetime import datetime

farmer_bp = Blueprint("farmer", __name__, url_prefix="/api/v1/farmer")


@farmer_bp.route("/livestock", methods=["POST"])
@farmer_required
def add_livestock():
    farmer_id = get_jwt_identity()
    data = request.get_json()

    # Create livestock with all fields
    animal = Livestock(
        farmer_id=farmer_id,
        animal_type=data.get("animal_type"),
        breed=data.get("breed"),
        gender=data.get("gender"),
        weight=data.get("weight"),
        age_months=data.get("age_months"),
        price=data.get("price"),
        price_per_kg=data.get("price_per_kg"),
        original_price=data.get("original_price"),
        location=data.get("location"),
        image_url=data.get("image_url") or data.get("images", "").split(",")[0] if data.get("images") else None,
        images=data.get("images", ""),
        description=data.get("description"),
        reason_for_sale=data.get("reason_for_sale"),
        health_certified=data.get("health_certified", False),
    )

    db.session.add(animal)
    db.session.flush()  # Get the animal ID

    # Handle vaccinations if provided
    vaccinations = data.get("vaccinations", [])
    if vaccinations and isinstance(vaccinations, list):
        for vax_data in vaccinations:
            if isinstance(vax_data, dict):
                try:
                    date_administered = None
                    if vax_data.get("date_administered"):
                        date_administered = datetime.strptime(
                            vax_data["date_administered"], "%Y-%m-%d"
                        ).date()

                    next_due_date = None
                    if vax_data.get("next_due_date"):
                        next_due_date = datetime.strptime(
                            vax_data["next_due_date"], "%Y-%m-%d"
                        ).date()

                    vaccination = Vaccination(
                        livestock_id=animal.id,
                        name=vax_data.get("name"),
                        date_administered=date_administered,
                        next_due_date=next_due_date,
                        certificate_url=vax_data.get("certificate_url"),
                    )
                    db.session.add(vaccination)
                except (ValueError, TypeError) as e:
                    # Skip invalid vaccination data
                    print(f"Skipping invalid vaccination: {e}")
                    continue

    db.session.commit()

    return jsonify({
        "message": "Livestock added successfully",
        "livestock": animal.to_dict()
    }), 201


@farmer_bp.route("/livestock", methods=["GET"])
@farmer_required
def my_livestock():
    farmer_id = get_jwt_identity()
    animals = Livestock.query.filter_by(farmer_id=farmer_id).all()
    return jsonify([a.to_dict() for a in animals]), 200


@farmer_bp.route("/analytics", methods=["GET"])
@farmer_required
def farmer_analytics():
    farmer_id = get_jwt_identity()

    total_animals = Livestock.query.filter_by(farmer_id=farmer_id).count()
    total_value = db.session.query(
        db.func.sum(Livestock.price)
    ).filter_by(farmer_id=farmer_id).scalar() or 0

    return jsonify({
        "total_animals": total_animals,
        "total_value": total_value
    })
