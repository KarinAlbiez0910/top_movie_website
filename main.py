from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///blog.db")
Bootstrap(app)
db = SQLAlchemy(app)

class MyEditForm(FlaskForm):
    rating = StringField('Your Rating (out of 10, e. g. 7.5)', validators=[DataRequired()])
    review = StringField('Your Review',validators=[DataRequired()])
    submit = SubmitField("Done")


class MyAddForm(FlaskForm):
    added_movie_title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField("Add Movie")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Integer)
    ranking = db.Column(db.Integer, unique=True)
    review = db.Column(db.String)
    img_url = db.Column(db.String)

#db.create_all()

#new_movie = Movie(
#    title="Phone Booth",
#    year=2002,
#    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#    rating=7.3,
#    ranking=10,
#    review="My favourite character was the caller.",
#    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")

#new_movie_2 = Movie(
#    title="La La Land",
#    year=2016,
#    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#    ranking=9,
#    review="My favourite character was the caller.",
#    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")

#db.session.add(new_movie_2)
#db.session.commit()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating.desc()).all()
    for movie in all_movies:
        movie.ranking = all_movies.index(movie) + 1
        db.session.commit()
    return render_template("index.html", all_movies=all_movies)

@app.route("/edit/<string:movie_title>", methods=['POST', 'GET'])
def edit(movie_title):
    form = MyEditForm()
    current_movie = db.session.query(Movie).filter_by(title=movie_title).first()
    if form.validate_on_submit():
        current_movie.rating = form.rating.data
        current_movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie_title=movie_title)

@app.route("/add", methods=['POST', 'GET'])
def add():
    form = MyAddForm()
    if form.validate_on_submit():
        added_movie = form.added_movie_title.data.lower()
        api_key = "f8af01cad255748858e08c309f186b18"
        params = {
            'api_key': api_key,
            'query': added_movie
        }
        root_url = "https://api.themoviedb.org/3/search/movie"
        response = requests.get(root_url, params=params)
        data_response = response.json()
        return render_template('select.html', added_movie=added_movie, data_response=data_response)
    return render_template('add.html', form=form)

@app.route("/find/<int:id>")
def find(id):
    api_key = "f8af01cad255748858e08c309f186b18"
    params = {
        'api_key': api_key,
    }
    root_url = f"https://api.themoviedb.org/3/movie/{id}"
    response = requests.get(root_url, params=params)
    data_response = response.json()
    api_title = data_response['original_title']
    api_year = data_response['release_date'].split('-')[0]
    api_description = data_response['overview']
    image_base_url = "https://image.tmdb.org/t/p/w500"
    api_img_url = image_base_url + data_response['poster_path']
    selected_movie = Movie(
        title=api_title,
        year=api_year,
        description=api_description,
        img_url=api_img_url)
    db.session.add(selected_movie)
    db.session.commit()
    return redirect(url_for('edit', movie_title=api_title))


@app.route("/delete/<string:movie_title>")
def delete(movie_title):
    current_movie = db.session.query(Movie).filter_by(title=movie_title).first()
    db.session.delete(current_movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
   app.run(debug=True)


