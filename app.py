from flask import Flask, render_template, request, redirect, url_for ,flash
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import enum as Enum
from datetime import date
from sqlalchemy import or_ , and_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dancer1.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
app.secret_key = 'dancer1234*#'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

ROLE_CHOICES = (
    ('D', 'Director'),
    ('C', 'Coach'),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False)
    user_role = db.Column(db.String(120), nullable=False)

    # is_active = db.Column(db.Boolean(), default=True, nullable=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    mobile_no = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(120), nullable=True, default='M')
    about_us = db.Column(db.String(500), nullable=False)
    date_of_birth = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)

    def __repr__(self):
        return '<Artist %r>' % self.first_name + self.last_name


class Injury(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    injury_type = db.Column(db.String(80), nullable=False)
    injury_discription = db.Column(db.String(500), nullable=False)
    injury_date = db.Column(db.String(100), nullable=True)
    excepted_recovery_date = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    artist = db.Column(db.BigInteger, db.ForeignKey('artist.id'), nullable=False)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)

    def __str__(self):
        return self.injury_discription


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    artist_id = db.Column(db.BigInteger, db.ForeignKey('artist.id'), nullable=False)
    date = db.Column(db.String(100), default=date.today())
    status = db.Column(db.Boolean(), default=True, nullable=False)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)

    def __str__(self):
        return self.date


# db.create_all()

'''@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()'''


@login_manager.user_loader
def load_user(id):
    """Check if user is logged-in on every page load."""
    if id is not None:
        return User.query.get(int(id))
    return None


'''FLASK_ENV=development
 export FLASK_APP=main       

'''


@app.route('/')
@login_required
def index():
    artist_list = Artist.query.filter_by(user_id=current_user.id, is_active=True).all()
    artist__Injured_list = Artist.query.filter_by(user_id=current_user.id, is_active=False).all()
    injury_Details = Injury.query.filter_by(user_id=current_user.id).all()
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("pages/add-artist.html", artist_list=artist_list, user=user,
                           artist__Injured_list=artist__Injured_list,
                           injury_Details=injury_Details)


@app.route('/addArtist', methods=["POST", "GET"])
@login_required
def add_artist_view():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        address = request.form['address']
        about_us = request.form['abouts_us']
        date_of_birth = request.form['date_of_birth']
        age = request.form['age']
        is_active = request.form['is_active']
        if int(is_active) == 1:
            is_active = True
        else:
            is_active = False
        mobile_no = request.form['mobile_no']
        gender = request.form['gender']
        artist = Artist(first_name=first_name, last_name=last_name, email=email, address=address, about_us=about_us,
                        date_of_birth=date_of_birth, age=age, is_active=is_active, gender=gender, mobile_no=mobile_no,
                        user_id=current_user.id)
        db.session.add(artist)
        db.session.commit()
        return redirect('/')
    artist_list = Artist.query.filter_by(user_id=current_user.id, is_active=True).all()
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('pages/add-artist.html', artist_list=artist_list, user=user)


@app.route("/updateArtist/<id>")
@app.route("/updateArtist/<id>", methods=["GET", "POST"])
@login_required
def update_artist(id):
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        address = request.form['address']
        about_us = request.form['about_us']
        date_of_birth = request.form['date_of_birth']
        age = request.form['age']
        is_active = request.form['is_active']
        if int(is_active) == 1:
            is_active = True
        else:
            is_active = False
        mobile_no = request.form['mobile_no']
        user_id = request.form["user_id"]
        artist_id = request.form["artist_id"]
        artist_obj = Artist.query.filter_by(id=artist_id).first()
        artist_obj.first_name = first_name
        artist_obj.last_name = last_name
        artist_obj.email = email
        artist_obj.about_us = about_us
        artist_obj.date_of_birth = date_of_birth
        artist_obj.age = age
        artist_obj.is_active = is_active
        artist_obj.user_id = user_id
        artist_obj.id = artist_id
        artist_obj.mobile_no = mobile_no
        db.session.add(artist_obj)
        db.session.commit()
        return redirect("/")
    artist = Artist.query.get(id)
    print(artist.is_active, "@@@@@@@@@@@@@@@@@@")
    artist_list = Artist.query.filter_by(user_id=current_user.id).all()
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("pages/update-artist.html", artist_list=artist_list, artist=artist, user=user)


@app.route('/injuryArtist/<id>', methods=["POST", "GET"])
@login_required
def injuryArtist(id):
    if request.method == "POST":
        artist_id = request.form['artist_id']
        injury_type = request.form['injury_type']
        injury_date = request.form['injury_date']
        excepted_recovery_date = request.form['excepted_recovery_date']
        injury_discription = request.form['injury_discription']
        user_id = current_user.id
        injury = Injury(artist=int(artist_id), injury_date=injury_date, injury_type=injury_type,
                        excepted_recovery_date=excepted_recovery_date, injury_discription=injury_discription,
                        user_id=user_id, is_active=True)
        db.session.add(injury)
        artist = Artist.query.get(id)
        artist.is_active = False
        db.session.add(artist)
        db.session.commit()
        return redirect(url_for("index"))

    artist = Artist.query.get(id)
    artist_list = Artist.query.filter_by(user_id=current_user.id).all()
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("pages/add-injury.html", artist_list=artist_list, artist=artist, user=user)


@app.route("/Recorved/<id>")
@login_required
def recorved_artist(id):
    artist = Artist.query.get(id)
    artist.is_active = True
    injury = Injury.query.filter_by(artist=id).first()
    injury.is_active = False
    db.session.add(artist)
    db.session.commit()
    db.session.add(injury)
    db.session.commit()
    return redirect('/')


@app.route("/deleteArtist/<id>")
@login_required
def delete_artist(id):
    artist = Artist.query.get(id)
    db.session.delete(artist)
    db.session.commit()
    return redirect('/')


@app.route("/attendacePresent/<id>", methods=['GET', 'POST'])
@login_required
def attendace_present(id):
    attendace_status = Attendance.query.filter_by(user_id=current_user.id,  artist_id=id,
                                                  date=str(date.today())).first()
    if attendace_status is  None:
        attedance = Attendance(user_id=current_user.id, artist_id=id, date=date.today(), is_active=True)
        db.session.add(attedance)
        db.session.commit()
        return redirect('/')
    flash("Attendance already mark!")
    return redirect('/')


@app.route("/attendaceAbsent/<id>", methods=['GET', 'POST'])
@login_required
def attendace_absent(id):
    attendace_status = Attendance.query.filter_by(user_id=current_user.id, artist_id=id,
                                                  date=str(date.today())).first()
    if attendace_status is None:
        attedance = Attendance(status=False, user_id=current_user.id, artist_id=id, date=date.today(), is_active=True)
        db.session.add(attedance)
        db.session.commit()
        return redirect('/')
    flash("Attendance already mark!")
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            # email = request.form['email']
            password = request.form['password']

            if username is not None and password is not None:
                print(User.query.all())
                try:
                    user = User.query.filter_by(username=username, password=password).first()
                except User.DoesNotExist:
                    user = None
                if user is not None:
                    login_user(user)
                    return redirect(url_for('index'))
    return render_template("pages/login.html")


@app.route('/register', methods=["GET", "POST"])
def register_view():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_role = request.form['user_role']
        valid_username = User.query.filter_by(username=username).first()
        if valid_username is None:
            valid_email = User.query.filter_by(email=email).first()
            if valid_email is None:
                user = User(username=username, email=email, password=password, user_role=user_role, is_active=True)
                db.session.add(user)
                db.session.commit()
                return redirect("login")
            else:
                flash("Already exist this  email")
                return redirect(url_for('register_view'))
        else:
            flash("Already exist this  username")
            return redirect(url_for('register_view'))

    return render_template("pages/sign-up.html")


@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


if __name__ == "__main__":
    db.create_all()
    app.run(use_reloader=True, debug=True)
