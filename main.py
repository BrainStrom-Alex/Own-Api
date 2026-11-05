from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)\

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()



@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafe = result.scalars().all()
    random_cafe = random.choice(all_cafe)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafe = result.scalars().all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafe])

@app.route("/search")
def search_cafe():
    loc = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == loc))
    all_cafe = result.scalars().all()
    if len(all_cafe) == 0:
        return jsonify(error={
           "Not Found": "Sorry, we don't have a cafe at that location."
       })
    else:
        return jsonify(cafe=[cafe.to_dict() for cafe in all_cafe])


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    price = request.args.get("price")
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == id)).scalar()
    try:
        cafe.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    except AttributeError:
        return jsonify(error={
            "Not Found": "Sorry, we don't have this cafe at that location."
        })

# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    api_key = (request.args.get("api_key"))
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe:
        if api_key == "777":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."})
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have this cafe at that location."
        })

if __name__ == '__main__':
    app.run(debug=True)
