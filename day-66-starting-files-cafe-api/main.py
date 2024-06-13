from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import choice

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

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
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

with app.app_context():
    db.create_all()


# HTTP GET - Read Record
@app.route("/")
def home():
    return render_template("index.html")


@app.get("/random")
def random():
    all_cafes = Cafe.query.order_by(Cafe.name).all()
    cafe = choice(all_cafes)
    return jsonify(cafe = cafe.to_dict())

@app.get("/all")
def all():
    all_cafes = Cafe.query.order_by(Cafe.name).all()
    all_cafes_list =[]
    for cafe in all_cafes:
        cafe = cafe.to_dict()
        all_cafes_list.append(cafe)
    return jsonify(all_cafes_list)

@app.get("/search")
def search():
    location = request.args.get("location")
    condition = Cafe.location.like("%" + location + "%")
    all_cafes = Cafe.query.where(condition).all()
    if len(all_cafes) == 0:
        return jsonify({"error": "No results"})
    else:
        all_cafes_list = [cafe.to_dict() for cafe in all_cafes]
        return jsonify(all_cafes_list)



# HTTP POST - Create Record
def str_to_bool(val):
    if val == 'true':
        return 1
    return 0

@app.post('/add')
def add_new_cafe():
    new_cafe = Cafe(
        name= request.form.get("name"),
        map_url= request.form.get("map_url"),
        img_url= request.form.get("img_url"),
        location= request.form.get("location"),
        seats= request.form.get("seats"),
        has_toilet= str_to_bool(request.form.get("has_toilet")),
        has_wifi= str_to_bool(request.form.get("has_wifi")),
        has_sockets= str_to_bool(request.form.get("has_sockets")),
        can_take_calls=str_to_bool(request.form.get("can_take_calls")),
        coffee_price= request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(new_cafe.to_dict())

# HTTP PUT/PATCH - Update Record

@app.patch('/update-coffee-price/<int:cafe_id>')
def update_coffee_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe is None:
        return jsonify({"error": "Cafe not found"}, 404)
    cafe.coffee_price= request.form.get("new_coffee_price")
    db.session.commit()
    return jsonify({"success": 'Successfully updated coffee price'}, 200)

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
