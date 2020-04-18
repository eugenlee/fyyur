#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))

    shows_venue = db.relationship('Show', backref='venue', lazy=True)

    # implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))
    shows_artists = db.relationship('Show', backref='artist', lazy=True)

    # implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.

    cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    data = []

    for city in cities:
        venues_by_city = db.session.query(Venue.id, Venue.name).filter(Venue.city==city[0])
        v = []
        for venue in venues_by_city:
            v.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).count()
            })

        data.append({
            "city": city[0],
            "state": city[1],
            "venues": v
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on venues with partial string search. Ensure it's case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%'))
    data = []

    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).count()
        })

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    try:
        venue = Venue.query.get(venue_id)
        past_shows = db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time < datetime.now())
        upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now())

        old_shows = []
        for show in past_shows:
            old_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })

        new_shows = []
        for show in upcoming_shows:
            new_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": old_shows,
            "past_shows_count": past_shows.count(),
            "upcoming_shows": new_shows,
            "upcoming_shows_count": upcoming_shows.count()
        }

        return render_template('pages/show_venue.html', venue=data)
    except:
        flash("Venue ID does not exist")
        return render_template('pages/home.html')


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    error = False

    try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            genres=request.form.getlist('genres'),
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            website=request.form['website'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_talent=True if 'seeking_talent' in request.form else False,
            seeking_description=request.form['seeking_description']
        )

        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
        ven_del = Venue.query.get(venue_id)
        db.session.delete(ven_del)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # replace with real data returned from querying the database

    data = db.session.query(Artist)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%'))
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).count()
        })

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id

    try:
        artist = Artist.query.get(artist_id)
        past_shows = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time < datetime.now())
        upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now())

        old_shows = []
        for show in past_shows:
            old_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            })

        new_shows = []
        for show in upcoming_shows:
            new_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            })

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": old_shows,
            "past_shows_count": past_shows.count(),
            "upcoming_shows": new_shows,
            "upcoming_shows_count": upcoming_shows.count()
        }

        return render_template('pages/show_artist.html', artist=data)
    except:
        flash("Artist ID does not exist")
        return render_template('pages/home.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist is not None:
        form.name.data = artist.name,
        form.genres.data = artist.genres,
        form.city.data = artist.city,
        form.state.data = artist.state,
        form.phone.data = artist.phone,
        form.website.data = artist.website,
        form.facebook_link.data = artist.facebook_link,
        form.seeking_venue.data = artist.seeking_venue,
        form.seeking_description.data = artist.seeking_description,
        form.image_link = artist.image_link
    else:
        flash('Artist ID does not exist')
        return render_template('pages/home.html')
    # populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False

    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=True if 'seeking_venue' in request.form else False,
            seeking_description=request.form['seeking_description']
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue is not None:
        form.name.data = venue.name,
        form.genres.data = venue.genres,
        form.address.data = venue.address,
        form.city.data = venue.city,
        form.state.data = venue.state,
        form.phone.data = venue.phone,
        form.website.data = venue.website,
        form.facebook_link.data = venue.facebook_link,
        form.seeking_talent.data = venue.seeking_talent,
        form.seeking_description.data = venue.seeking_description,
        form.image_link = venue.image_link
    else:
        flash('Venue ID does not exist')
        return render_template('pages/home.html')
    # populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False

    try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            genres=request.form.getlist('genres'),
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            website=request.form['website'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_talent=True if 'seeking_talent' in request.form else False,
            seeking_description=request.form['seeking_description']
        )

        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # insert form data as a new Artist record in the db, instead
    # modify data to be the data object returned from db insertion
    error = False

    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=True if 'seeking_venue' in request.form else False,
            seeking_description=request.form['seeking_description']
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        # on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    showers = db.session.query(Show).join(Artist).join(Venue)
    data = []

    for show in showers:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead
    error = False

    try:
        show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    else:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
