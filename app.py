from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import os

movie_search = "https://api.themoviedb.org/3/search/movie/"
API_KEY = str(os.environ['API_KEY'])
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w342"
app = Flask(__name__)

app.config['SECRET_KEY'] = str(os.environ['SECRET_KEY'])
Bootstrap(app)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://ixxtwtjfrpqpgi:3b73700c0df24a74f6988b82c978aefbfb4b2d47dc2d6e1bd96acaf890fbfd5f@ec2-34-195-143-54.compute-1.amazonaws.com:5432/d6j7mlc3s47btc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Movie Database
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(2000), nullable=True)
    img_url = db.Column(db.String(500), nullable=False)


db.create_all()


# form class
class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()],
                         render_kw={'class': 'myfield', 'style': 'border-radius:10px'})
    review = StringField("Your Review", validators=[DataRequired()],
                         render_kw={'class': 'myfield', 'style': 'border-radius:10px;'})
    submit = SubmitField("Done", render_kw={'class': 'button',
                                            'style': 'border-radius:10px;width:30%;height:80%; background: linear-gradient(135deg, #1a9be6, #1a57e6);color:white;font-weight:600;'})


class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()],
                        render_kw={'class': 'myfield', 'style': 'border-radius:10px;'})
    submit = SubmitField("Add Movie", render_kw={'class': 'button',
                                                 'style': 'border-radius:10px; width:30%;height:80%; background: linear-gradient(135deg, #1a9be6, #1a57e6);color:white;font-weight:600;'})


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"

        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["original_title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie", id=new_movie.id))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(movie_search, params={"api_key": API_KEY, "query": movie_title})
        data = response.json()['results']
        print(data)

        return render_template("select.html", options=data)
    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
