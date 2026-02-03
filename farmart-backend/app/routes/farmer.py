from flask import Blueprint, request, jsonify
from app import db
from app.models import Livestock
from app.utils.decorators import farmer_required
from flask_jwt_extended import get_jwt_identity

farmer_bp = Blueprint("farmer", __name__, url_prefix="/api/v1/farmer")

@farmer_bp.route("/livestock", methods=["POST"])
@farmer_required
def add_livestock():
    farmer_id = get_jwt_identity()
    data = request.get_json()

    animal = Livestock(
        farmer_id=farmer_id,
        animal_type=data["animal_type"],
        breed=data.get("breed"),
        weight=data["weight"],
        age_months=data.get("age_months"),
        price=data["price"],
        location=data["location"]
    )

    db.session.add(animal)
    db.session.commit()

    return jsonify(animal.to_dict()), 201


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
