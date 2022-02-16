
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Time, cast
from flask_migrate import Migrate
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user, login_required
from flask_wtf import FlaskForm
#from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
from datetime import datetime, timezone, timedelta

from dash import dash
import dash_core_components as dcc
import dash_html_components as html



from BlueAlliance import GetSimpleTeamListAtEvent,GetEventMatches
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True
#Bootstrap(app)





#setup db connection
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="DiverJim",
    password="M3chT3ch3959!",
    hostname="DiverJim.mysql.pythonanywhere-services.com",
    databasename="DiverJim$Comments",
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#setup login stuff
app.config["SECRET_KEY"] = "MechT3ch!!QAZxsw2#EDCvfr4M3chT3ch!!"
login_manager = LoginManager()
login_manager.init_app(app)

#user Class
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    approvedUser = db.Column(db.Boolean, default=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

#comment data model
class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    posted = db.Column(db.DateTime, default=datetime.now)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    commenter = db.relationship('User', foreign_keys=commenter_id)


#Scouting app data
class Team2019(db.Model):
    __tablename__ = "Teams2019"

    id = db.Column(db.Integer, primary_key=True)
    teamNumber = db.Column(db.Integer)
    name = db.Column(db.String(128))
    key =  db.Column(db.String(128))
    country = db.Column(db.String(128))
    state = db.Column(db.String(128))
    city = db.Column(db.String(128))

    def __init__(self,teamNumber= None,name= None,key= None,country= None,state= None,city= None ):
        self.data = (teamNumber,name,key,country,state,city)

    def __repr__(self):
        if self.name != None:
            return "Team "+str(self.teamNumber) + " : " + self.name
        return self.key


class Event2019(db.Model):
    __tablename__ = "Events2019"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    key =  db.Column(db.String(128))
    start_date = db.Column(db.Date, nullable=True)
    week = db.Column(db.Integer)

    def __init__(self,name= None,key= None,start_date= None,week= None):
        self.data = (name,key,start_date,week)

    def __repr__(self):
        if self.name != None:
            return self.name
        return self.key


class EventTeamMap(db.Model):
    __tablename__ = "EventTeamMap"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('Events2019.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('Teams2019.id'))
    event = db.relationship('Event2019', foreign_keys=event_id)
    team = db.relationship('Team2019', foreign_keys=team_id)

class Match2019(db.Model):
    __tablename__ = "Match2019"

    id = db.Column(db.Integer, primary_key=True)
    Event_id = db.Column(db.Integer, db.ForeignKey('Events2019.id'))
    name = db.Column(db.String(128))
    key =  db.Column(db.String(128))
    predictedStartTime = db.Column(db.DateTime, nullable=True)
    matchNumber = db.Column(db.Integer)
    event = db.relationship('Event2019', foreign_keys=Event_id)

    def __init__(self,Event_id= None,name= None,key= None,predictedStartTime= None,matchNumber= None):
        self.data = (Event_id,name,key,predictedStartTime,matchNumber)

    def __repr__(self):
        if self.name != None:
            return self.event.name + " " + self.name
        return self.key


class MatchTeamMap(db.Model):
    __tablename__ = "MatchTeamMap"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Match2019.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('Teams2019.id'))
    position = db.Column(db.Integer, default=1)
    isBlue = db.Column(db.Boolean, default=True)
    match = db.relationship('Match2019', foreign_keys=match_id)
    team = db.relationship('Team2019', foreign_keys=team_id)


class StandScouting2019(db.Model):

    __tablename__ = "StandScouting2019"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    posted = db.Column(db.DateTime, default=datetime.now)
    Event_id = db.Column(db.Integer, db.ForeignKey('Events2019.id'))
    Match_id = db.Column(db.Integer, db.ForeignKey('Match2019.id'))
    Team_id = db.Column(db.Integer, db.ForeignKey('Teams2019.id'))
    SS_HatchesPlaced = db.Column(db.Integer, default=0)
    SS_CargoPlaced =  db.Column(db.Integer, default=0)
    SS_StartLevel =   db.Column(db.Integer, default=1)
    SS_LeftPlatform = db.Column(db.Boolean, default=False)
    TO_LeftPlatform = db.Column(db.Boolean, default=False)
    TO_HatchesPlaced = db.Column(db.Integer, default=0)
    TO_CargoPlaced =  db.Column(db.Integer, default=0)
    EG_ClimbLevel = db.Column(db.Integer, default=0)
    Penalties = db.Column(db.Integer, default=0)
    HighestPlacement = db.Column(db.Integer, default=0)
    DroppedHatches = db.Column(db.Integer, default=0)
    DroppedBalls = db.Column(db.Integer, default=0)
    PanelFloorPickup = db.Column(db.Integer, default=0)
    Notes = db.Column(db.String(4096))
    user = db.relationship('User', foreign_keys=user_id)
    event = db.relationship('Event2019', foreign_keys=Event_id)
    match = db.relationship('Match2019', foreign_keys=Match_id)
    team =  db.relationship('Team2019', foreign_keys=Team_id)

    def toDict(self):
        PointContribution = ( self.SS_HatchesPlaced+ self.TO_HatchesPlaced)*2+( self.SS_CargoPlaced+ self.TO_CargoPlaced)*3
        if  self.SS_LeftPlatform:
            PointContribution = PointContribution +  self.SS_StartLevel*3
        if  self.EG_ClimbLevel == 1:
            PointContribution = PointContribution + 3
        if  self.EG_ClimbLevel == 2:
            PointContribution = PointContribution + 6
        if  self.EG_ClimbLevel == 3:
            PointContribution = PointContribution + 12
        data = {
            "reportId": self.id,
            "User": self.user.username,
            "posted": self.posted,
            "Event_id": self.Event_id,
            "Event": self.event.name,
            "Match_id": self.Match_id,
            "Match": self.match.name,
            "Team_id": self.Team_id,
            "SS_HatchesPlaced": self.SS_HatchesPlaced,
            "SS_CargoPlaced": self.SS_CargoPlaced,
            "SS_StartLevel": self.SS_StartLevel,
            "SS_LeftPlatform": self.SS_LeftPlatform,
            "TO_HatchesPlaced": self.TO_HatchesPlaced,
            "TO_CargoPlaced": self.TO_CargoPlaced,
            "EG_ClimbLevel": self.EG_ClimbLevel,
            "Penalties": self.Penalties,
            "HighestPlacement": self.HighestPlacement,
            "DroppedHatches": self.DroppedHatches,
            "DroppedBalls": self.DroppedBalls,
            "PanelFloorPickup": self.PanelFloorPickup,
            "PointContribution": PointContribution,
            "Notes": self.Notes
            }
        return data
'''
    def __init__(self,user_id= None,
                        posted= None,
                        Event_id= None,
                        Match_id= None,
                        Team_id= None,
                        SS_HatchesPlaced= None,
                        SS_CargoPlaced= None,
                        SS_StartLevel= None,
                        SS_LeftPlatform= None,
                        TO_LeftPlatform= None,
                        TO_HatchesPlaced= None,
                        TO_CargoPlaced= None,
                        EG_ClimbLevel= None,
                        Penalties= None,
                        HighestPlacement= None,
                        DroppedHatches= None,
                        DroppedBalls= None,
                        PanelFloorPickup= None,
                        Notes= None):
        self.data = (name,key,predictedStartTime,matchNumber)
'''

#Form Classes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ScoutAdminForm(FlaskForm):
    task = SelectField('Task', choices=[('1','Insert Events')])

class defineEventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    key = StringField('Event Key', validators=[DataRequired()])
    start_date = DateField('Event Start Date')
    week = StringField('Event Week')

def eventsQuery():
    return Event2019.query.order_by(Event2019.start_date.desc())

class addTeamsForm(FlaskForm):
    event = QuerySelectField("Event",query_factory=eventsQuery, allow_blank=False)

class EventMatchTeamForm(FlaskForm):
    event = QuerySelectField("Event",query_factory=eventsQuery, allow_blank=False)
    match = SelectField('Match',coerce=int, choices=[])
    team  =  SelectField('Team',coerce=int, choices=[])

class StandScouting2019Form(FlaskForm):
    event = QuerySelectField("Event",query_factory=eventsQuery, allow_blank=False)
    matchTimeFilter = BooleanField('Filter Match Times', default=False)
    match = SelectField('Match',coerce=int, choices=[])
    team  =  SelectField('Team',coerce=int, choices=[])
    SS_HatchesPlaced = IntegerField('Sandstorm Hatches',validators=[NumberRange(min=0, max=5)])
    SS_CargoPlaced =  IntegerField('Sandstorm Cargo',validators=[NumberRange(min=0, max=12)])
    SS_StartLevel =   SelectField('Start Level',choices=[('1','Bottom (lvl 1)'),('2','Second (lvl 2)')])
    SS_LeftPlatform = BooleanField('Exited Hab in Sandstorm')
    TO_LeftPlatform = BooleanField('Exited Hab at all')
    TO_HatchesPlaced = IntegerField('Teleop Hatches',validators=[NumberRange(min=0, max=5)])
    TO_CargoPlaced =  IntegerField('Teleop Cargo',validators=[NumberRange(min=0, max=30)])
    EG_ClimbLevel = SelectField('Climb Level',choices=[('0','No Climb'),('1','Bottom (lvl 1)'),('2','Second (lvl 2)'),('3','Third (lvl 3)')])
    Penalties = IntegerField('Penalties',validators=[NumberRange(min=0, max=200)])
    HighestPlacement = SelectField('Highest Rocket Level',choices=[('1','Bottom (lvl 1)'),('2','Second (lvl 2)'),('3','Third (lvl 3)')])
    DroppedHatches = IntegerField('Hatches Dropped',validators=[NumberRange(min=0, max=200)])
    DroppedBalls = IntegerField('Cargo Dropped',validators=[NumberRange(min=0, max=200)])
    PanelFloorPickup = IntegerField('Hatches Picked from floor',validators=[NumberRange(min=0, max=200)])
    Notes = StringField('Notes')

def GetScoutReportDicts(event_id = None, match_id=None, team_id = None):
    q = StandScouting2019.query
    if event_id != None:
        q = q.filter(StandScouting2019.Event_id == event_id)
    if match_id != None:
        q = q.filter(StandScouting2019.Match_id == match_id)
    if team_id != None:
        q = q.filter(StandScouting2019.Team_id == team_id)

    reports = [ i.toDict() for i in q.all()]

    return reports

#Start Dash Config
external_stylesheets = []
meta_viewport = {}

scoutingDash = dash.Dash(__name__, server=app,
                         url_base_pathname='/ScoutDashboard/',
                         title='Scouting Dashboard - MechTech',
                         )

scoutingDash.index_string = '''
 <!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        {%metas%}
        <link rel="stylesheet"
              href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
              integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
              crossorigin="anonymous">

        <link rel="stylesheet"
              href="https://use.fontawesome.com/releases/v5.7.2/css/all.css"
              integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr"
              crossorigin="anonymous">

        <title>{%title%}</title>

        <style>
            /* Remove the navbar's default margin-bottom and rounded borders */
            .navbar {
                margin-bottom: 0;
                border-radius: 0;
            }

            /* Set height of the grid so .sidenav can be 100% (adjust as needed) */
            .row.content {height: 450px}

            /* Set gray background color and 100% height */
            .sidenav {
                padding-top: 20px;
                background-color: #f1f1f1;
                height: 100%;
            }

            /* Set black background color, white text and some padding */
            footer {
                background-color: #555;
                color: white;
                padding: 15px;
            }

            /* On small screens, set height to 'auto' for sidenav and grid */
            @media screen and (max-width: 767px) {
            .sidenav {
                height: auto;
                padding: 15px;
            }
                .row.content {height:auto;}
            }

            {%favicon%}
            {%css%}

        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-md navbar-dark bg-dark">
            <a class="navbar-brand" href="/">MechTech</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home <span class="sr-only">(current)</span></a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/StandScoutReport">Reports</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle"
                            href="#" id="navbarDropdown"
                            role="button" data-toggle="dropdown"
                            aria-haspopup="true"
                            aria-expanded="false">Scouting
                        </a>
                        <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                            <a class="dropdown-item" href="/StandScout">Stand Scouting</a>
                            <a class="dropdown-item" href="#">Pit Scouting</a>
                            <div class="dropdown-divider"></div>
                            <a class="dropdown-item" href="/ScoutAdmin">Scouting Admin</a>
                        </div>
                    </li>
                    <!--<li class="nav-item">
                        <a class="nav-link disabled" href="#" tabindex="-1" aria-disabled="true">Management</a>
                    </li> -->
                </ul>
            </div>
        </nav>
        <hr>
        {%app_entry%}
        <footer>
            <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>

    </body>
</html>
'''


Events = Event2019.query.filter_by(id=3).all()
Matchs = Match2019.query.filter_by(Event_id = 3).order_by(Match2019.predictedStartTime).all()
Teams = Team2019.query.order_by(Team2019.teamNumber.desc()).all()
EventList = [{'label': i.name, 'value': i.id} for i in Events]
MatchList = [{'label': i.key, 'value': i.id} for i in Matchs]
TeamList = [{'label': str(i), 'value': i.id} for i in Teams]

Reports = GetScoutReportDicts()

scoutingDash.layout = html.Div(
            html.Div(children = [
                                dcc.Dropdown(
                                                id='Event',
                                                options=EventList,
                                                value='3',
                                                style={"width":"250px", "margin-right":'3px'},
                                                className = 'form-inline'
                                            ),
                                dcc.Dropdown(
                                                id='Match',
                                                options=MatchList,
                                                value='Match',
                                                style={"width":"200px", "margin-right":'3px'},
                                                clearable = True,
                                                placeholder = 'match',
                                                className = 'form-inline'
                                            ),
                                dcc.Dropdown(
                                                id='Team',
                                                options=TeamList,
                                                value='Team',
                                                style={"width":"200px", "margin-right":'3px'},
                                                clearable = True,
                                                placeholder = 'team',
                                                className = 'form-inline'
                                            ),
                                ],
                        className= 'form-group row',
                        style = {'margin':'5px'}
                )
            )

'''
class customDash(dash):
    def index(self, *args, **kwargs):
'''
#End of Dash Stuff

#Home page
@app.route('/index', methods=["GET", "POST"])
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #return render_template("main_page.html", comments=Comment.query.all())
        return render_template("index.html",title='Home', comments=Comment.query.all())
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    comment = Comment(content=request.form["contents"], commenter=current_user)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))


#login page
@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/StandScout', methods=['GET', 'POST'])
def standScout():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = StandScouting2019Form()

    form.match.choices = [(match.id, str(match)) for match in Match2019.query.all()]
    form.team.choices = [(team.id, str(team)) for team in Team2019.query.all()]
    if request.method == "GET":
        return render_template('StandScout.html', title='Stand Scout', form=form)

    #return '<html><h3>Event = {}, Match = {}, team = {}</h3></html>'.format(form.event.data.id, form.match.data, form.team.data)

    if form.validate_on_submit():
        report = StandScouting2019()
        report.user_id = current_user.id
        report.Event_id = form.event.data.id
        report.Match_id = int(form.match.data)
        report.Team_id = int(form.team.data)
        report.SS_HatchesPlaced = form.SS_HatchesPlaced.data
        report.SS_CargoPlaced = form.SS_CargoPlaced.data
        report.SS_StartLevel = form.SS_StartLevel.data
        report.SS_LeftPlatform = form.SS_LeftPlatform.data
        report.TO_LeftPlatform = form.TO_LeftPlatform.data
        report.TO_HatchesPlaced = form.TO_HatchesPlaced.data
        report.TO_CargoPlaced = form.TO_CargoPlaced.data
        report.EG_ClimbLevel = form.EG_ClimbLevel.data
        report.Penalties = form.Penalties.data
        report.HighestPlacement = form.HighestPlacement.data
        report.DroppedHatches = form.DroppedHatches.data
        report.DroppedBalls = form.DroppedBalls.data
        report.PanelFloorPickup = form.PanelFloorPickup.data
        report.Notes = form.Notes.data

        db.session.add(report)
        db.session.commit()
        return redirect(url_for('standScout'))
    #return '<html><h2>team data = {}</h2><h3>{}</h3></html>'.format( form.team.data, form.team.choices)
    return render_template('StandScout.html', title='Stand Scout', form=form)


@app.route('/StandScout/matches')
def standScoutMatches():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    e_id = request.args.get('event_id')
    timeFilter = request.args.get('timeFilter') == 'true'

    if e_id != None:
        if e_id.isdigit():
            e_id = int(e_id)
    else:
        e_id = -1
    #matches = []
    if timeFilter:
        minTime = datetime.now() - timedelta(hours=3)
        maxTime = datetime.now() + timedelta(hours=3)
        matches = Match2019.query.filter(Match2019.Event_id == e_id,
                                         cast(Match2019.predictedStartTime, Time) >= minTime,
                                         cast(Match2019.predictedStartTime, Time) <= maxTime).order_by(Match2019.predictedStartTime).all()
        #matches = Match2019.query.filter(_and(Event_id = e_id, predictedStartTime.between(minTime, maxTime))).order_by(Match2019.predictedStartTime).all()
    else:
        matches = Match2019.query.filter_by(Event_id = e_id).order_by(Match2019.predictedStartTime).all()

    matchAry = []
    for m in matches:
        match = {}
        match['id'] = m.id
        match['name'] = str(m)
        matchAry.append(match)
    return jsonify({ 'matches':matchAry})

@app.route('/StandScout/teams')
def standScoutTeams():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    m_id = request.args.get('match_id')

    if m_id != None:
        if m_id.isdigit():
            m_id = int(m_id)
    else:
        m_id = -1


    teams = MatchTeamMap.query.filter_by(match_id = m_id).all()

    teamAry = []
    for t in teams:
        team = {}
        team['id'] = t.team.id
        team['name'] = str(t.team)
        teamAry.append(team)
    return jsonify({'teams':teamAry})



@app.route('/StandScoutReport', methods=['GET'])
def standScoutReport():
    form = EventMatchTeamForm()
    q = StandScouting2019.query
    cols = q.column_descriptions
    reports = GetScoutReportDicts(event_id=3)
    return jsonify(reports)
    '''
    df = pd.read_sql(sql = db.session.query(StandScouting2019) \
                                     .join(StandScouting2019.event)\
                                     .join(StandScouting2019.match)\
                                     .join(StandScouting2019.team)\
                                     .join(StandScouting2019.user)
                                     .with_entities(Event2019.name,
                                                     Match2019.name,
                                                     Team2019.teamNumber,
                                                     User.username,
                                                     StandScouting2019.posted,
                                                     StandScouting2019.SS_StartLevel,
                                                     StandScouting2019.SS_LeftPlatform,
                                                     StandScouting2019.SS_HatchesPlaced,
                                                     StandScouting2019.SS_CargoPlaced,
                                                     StandScouting2019.TO_LeftPlatform,
                                                     StandScouting2019.TO_HatchesPlaced,
                                                     StandScouting2019.TO_CargoPlaced,
                                                     StandScouting2019.EG_ClimbLevel,
                                                     StandScouting2019.Penalties,
                                                     StandScouting2019.HighestPlacement,
                                                     StandScouting2019.PanelFloorPickup,
                                                     StandScouting2019.DroppedHatches,
                                                     StandScouting2019.DroppedBalls,
                                                     StandScouting2019.Notes).statement,
                    con = db.session.bind)
    '''

    '''
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    posted = db.Column(db.DateTime, default=datetime.now)
    Event_id = db.Column(db.Integer, db.ForeignKey('Events2019.id'))
    Match_id = db.Column(db.Integer, db.ForeignKey('Match2019.id'))
    Team_id = db.Column(db.Integer, db.ForeignKey('Teams2019.id'))
    SS_HatchesPlaced = db.Column(db.Integer, default=0)
    SS_CargoPlaced =  db.Column(db.Integer, default=0)
    SS_StartLevel =   db.Column(db.Integer, default=1)
    SS_LeftPlatform = db.Column(db.Boolean, default=False)
    TO_LeftPlatform = db.Column(db.Boolean, default=False)
    TO_HatchesPlaced = db.Column(db.Integer, default=0)
    TO_CargoPlaced =  db.Column(db.Integer, default=0)
    EG_ClimbLevel = db.Column(db.Integer, default=0)
    Penalties = db.Column(db.Integer, default=0)
    HighestPlacement = db.Column(db.Integer, default=0)
    DroppedHatches = db.Column(db.Integer, default=0)
    DroppedBalls = db.Column(db.Integer, default=0)
    PanelFloorPickup = db.Column(db.Integer, default=0)
    Notes = db.Column(db.String(4096))
    user = db.relationship('User', foreign_keys=user_id)
    event = db.relationship('Event2019', foreign_keys=Event_id)
    match = db.relationship('Match2019', foreign_keys=Match_id)
    team =  db.relationship('Team2019', foreign_keys=Team_id)
    '''

    #return render_template('scoutingDashboard.html', title='Scout Report', form=form, tblCols=cols)



@app.route('/ScoutAdmin', methods=['GET', 'POST'])
def scoutAdmin():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form=ScoutAdminForm()
    return render_template('ScoutAdmin.html', title='Scout Admin', form=form)

@app.route('/defineEvent', methods=['GET', 'POST'])
def defineEvent():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = defineEventForm()
    if request.method == "GET":
        return render_template('defineEvent.html', title='Define Event', form=form)

    if form.validate_on_submit():
        e = Event2019(name=form.name.data, key=form.key.data, start_date=form.start_date.data, week=form.week.data)
        db.session.add(e)
        db.session.commit()
        return redirect(url_for('scoutAdmin'))
    return render_template('defineEvent.html', title='Define Event', form=form)


@app.route('/insertAllTeams', methods=['GET','POST'])
def insertAllTeams():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = addTeamsForm()
    if request.method == "GET":
        return render_template('addTeamsAtEvent.html', title='Add Teams', form=form)
    tl = GetSimpleTeamListAtEvent(form.event.data.key)
    dbTeamList = Team2019.query.with_entities(Team2019.teamNumber).all()
    #return '<html><h1>{}</h1></html>'.format(dbTeamList)

    for t in tl:
        nt = Team2019()
        if t['team_number'] not in dbTeamList:
            nt.teamNumber=t['team_number']
            nt.name=t['nickname']
            nt.country=t['country']
            nt.state=t['state_prov']
            nt.city=t['city']
            nt.key=t['key']
            #return '<html><h1>{},{},{},{},{}</h1></html>'.format(str(nt.teamNumber), nt.name, nt.country, nt.state, nt.city)
            db.session.add(nt)
            db.session.commit()
        else:
            nt = Team2019.query.filter_by(teamNumber=t.teamNumber).first()
        if EventTeamMap.query.filter_by(team=nt, event=form.event.data).count() ==0:
            etm = EventTeamMap()
            etm.event = form.event.data
            etm.team = nt
            db.session.add(etm)
            db.session.commit()

    return redirect(url_for('scoutAdmin'))

@app.route('/insertAllMatches', methods=['GET','POST'])
def insertAllMatches():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = addTeamsForm()
    if request.method == "GET":
        return render_template('addMatchesAtEvent.html', title='Add Matches', form=form)
    ml = GetEventMatches(form.event.data.key)
    if not ml:
        return redirect(url_for('scoutAdmin'))

    dbMatchList = Match2019.query.filter_by(Event_id=form.event.data.id).with_entities(Match2019.key).all()
    #return '<html><h1>{}</h1></html>'.format(ml)

    for m in ml:
        if "key" not in m:
            continue
        nm = Match2019()
        if m['key'] not in dbMatchList:
            nm.Event_id=form.event.data.id
            nm.key=m['key']
            if m['comp_level'] != "qm":
                nm.name = m['comp_level']+str(m['set_number'])+'m'+str(m['match_number'])
            else:
                nm.name = m['comp_level']+str(m['match_number'])
            nm.predictedStartTime=datetime.fromtimestamp(m['predicted_time'], timezone.utc)
            nm.matchNumber=m['match_number']
            db.session.add(nm)
        else:
            nm = Match2019.query.filter_by(key=m['key']).first()
            nm.Event_id=form.event.data.id
            nm.key=m['key']
            if m['comp_level'] != "qm":
                nm.name = m['comp_level']+str(m['set_number'])+'m'+str(m['match_number'])
            else:
                nm.name = m['comp_level']+str(m['match_number'])
            nm.predictedStartTime=datetime.fromtimestamp(m['predicted_time'], timezone.utc)
            nm.matchNumber=m['match_number']
        db.session.commit()

        tl = MatchTeamMap.query.filter_by(match_id=nm.id)
        tl.delete(synchronize_session=False)
        i = 1
        for t in m['alliances']['red']['team_keys']:
            tm = MatchTeamMap()
            tm.team = Team2019.query.filter_by(key=t).first()
            tm.match_id = nm.id
            tm.isBlue = False
            tm.position = i
            i += 1
            db.session.add(tm)
            db.session.commit()
        i = 1
        for t in m['alliances']['blue']['team_keys']:
            tm = MatchTeamMap()
            tm.team = Team2019.query.filter_by(key=t).first()
            tm.match_id = nm.id
            tm.isBlue = True
            tm.position = i
            i += 1
            db.session.add(tm)
            db.session.commit()
    return redirect(url_for('scoutAdmin'))
'''
match_id = db.Column(db.Integer, db.ForeignKey('Match2019.id'))
team_id = db.Column(db.Integer, db.ForeignKey('Teams2019.id'))
position = db.Column(db.Integer, default=1)
isBlue = db.Column(db.Boolean, default=True)
match = db.relationship('Match2019', foreign_keys=match_id)
team = db.relationship('Team2019', foreign_keys=team_id)
'''

