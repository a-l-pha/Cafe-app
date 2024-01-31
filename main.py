from flask import * 
from flask_wtf import *
from wtforms import StringField, URLField, SubmitField, SelectField, BooleanField, FloatField
import wtforms.fields.list as list_
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms.validators import DataRequired
import re
import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cafes.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


class MyForm(FlaskForm):
    name = StringField('name:', validators=[DataRequired()])
    map_url = URLField('map_url:', validators=[DataRequired()])  # convert to string
    img_url = URLField('img_url:', validators=[DataRequired()])  # convert to string
    location = StringField('location', validators=[DataRequired()])

    seats = SelectField('num_seats',
                        choices=[('0-10', '0-10'), ('10-20', '10-20'), ('20-30', '20-30'), ('30-40', '30-40'),
                                 ('40-50', '40-50'), ('50+', '50+')], validators=[DataRequired()])
    coffee_price = FloatField('coffee price', validators=[DataRequired()])  # Convert to string
    has_toilet = BooleanField('has_toilets', )
    has_wifi = BooleanField('has_wifi', )
    has_sockets = BooleanField('has_sockets', )
    can_take_calls = BooleanField('can_take_calls', )

    submit = SubmitField('Submit')


cafes = []


@app.route('/')
def home():
    global cafes
    if type(db.session.query(Cafe).all()) == list_:
        cafes = db.session.query(Cafe).all()
        cafes = cafes[0]
    else:
        cafes = db.session.query(Cafe).all()

    return render_template('listing.html', cafes=cafes, current_cafe=None, can_go_back=False)


@app.route('/<int:cur_id>')
def show_cafe_info(cur_id):
    global cafes
    cafe = Cafe.query.filter_by(id=cur_id).first()
    return render_template('listing.html', cafes=cafes, current_cafe=cafe, can_go_back=False)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    global cafes

    form = MyForm(meta={'csrf': False})
    if form.validate_on_submit():
        new_cafe = Cafe(name=form.name.data, map_url=form.map_url.data, img_url=form.img_url.data,
                        location=form.location.data, seats=form.seats.data, coffee_price=form.coffee_price.data,
                        has_toilet=form.has_toilet.data, has_wifi=form.has_wifi.data, has_sockets=form.has_sockets.data,
                        can_take_calls=form.can_take_calls.data)
        db.session.add(new_cafe)
        db.session.commit()
        if type(db.session.query(Cafe).all()) == list_:
            cafes = db.session.query(Cafe).all()
            cafes = cafes[0]
        else:
            cafes = db.session.query(Cafe).all()

        cafe_id = cafes.pop().id

        if type(db.session.query(Cafe).all()) == list_:
            cafes = db.session.query(Cafe).all()
            cafes = cafes[0]
        else:
            cafes = db.session.query(Cafe).all()
        return redirect(f"/{cafe_id}")

    return render_template('add_cafe.html', cafes=cafes, form=form, can_go_back=True)


@app.route('/delete/<int:cur_id>')
def delete_cafe(cur_id):
    cafe_id = cur_id
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()

    return redirect(f"{url_for('home')}")


@app.route('/search/', methods=['GET', 'POST'])
def search_cafe():
    global cafes
    query = request.form.get("search_box")

    if type(db.session.query(Cafe).all()) == list_:
        cafes = db.session.query(Cafe).all()
        cafes = cafes[0]
    else:
        cafes = db.session.query(Cafe).all()
    new_cafes = []

    for cafe in cafes:
        if query.lower() in cafe.location.lower():
            new_cafes.append(cafe)

    return render_template('listing.html', cafes=new_cafes, current_cafe=None, can_go_back=True)


@app.route('/sort/<sort_by>', methods=['GET', 'POST'])
def sort_cafes(sort_by):
    global cafes

    if sort_by == 'None':
        return redirect(f"{url_for('home')}")
    elif sort_by == 'Coffee_price':
        cafes.sort(key=lambda x: x.coffee_price)
    elif sort_by == 'Capacity':
        cafes.sort(key=lambda x: re.findall(r'^\D*(\d+)', x.seats))
    elif sort_by == 'A-Z':
        cafes.sort(key=lambda x: x.name)
    elif sort_by == 'All-atr':
        cafes = list(filter(lambda x: x.has_toilet and x.has_wifi and x.has_sockets and x.can_take_calls,
                            cafes))

    return render_template('listing.html', cafes=cafes, current_cafe=None, can_go_back=False)


if __name__ == '__main__':
    app.run(debug=True)
