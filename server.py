#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://slc2206:5957@104.196.18.7/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



#Some sample queries











@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)
  #return render_template("home.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')









"""
-----------Our added stuff-------
"""










@app.route('/show_all')
def show_all():

  return render_template("show_all.html", movies = movies)#movies = Movie.query.all())#, movies = Movie.query.all() )


@app.route('/movie_data')
def show_movie():
  movies = [m for m in engine.execute("SELECT * FROM Movie")]

  # movies = [m for m in engine.execute("SELECT * FROM Movie")]
  return render_template("movie_page.html", movies = movies)#movies = Movie.query.all())#, movies = Movie.query.all() )


@app.route('/movie_data_specific', methods = ["POST"])
def show_movie_specific():
  print "in show"
  movieID = int(request.form['movie_id'])
  print movieID
  movie = [m for m in engine.execute("SELECT * FROM Movie M WHERE M.movie_id = %d" % (movieID))]
  movies = [m for m in engine.execute("SELECT * FROM Movie")]

  actors = [a for a in engine.execute("SELECT * FROM Contributor C\
   WHERE C.contributor_id IN \
   (SELECT C.contributor_id FROM Contributor C, Acts A, Movie M\
    WHERE M.movie_id = %d AND M.movie_id = A.movie_id AND A.contributor_id = C.contributor_id)" % (movieID))]
  
  producers = [p for p in engine.execute("SELECT * FROM Contributor C\
   WHERE C.contributor_id IN \
   (SELECT C.contributor_id FROM Contributor C, Produces P, Movie M\
    WHERE M.movie_id = %d AND M.movie_id = P.movie_id AND P.contributor_id = C.contributor_id)" % (movieID))]

  studios = [s for s in engine.execute("SELECT * FROM Studio S\
    WHERE S.studio_id IN\
    (SELECT D.studio_id FROM Studio S, Develops D WHERE S.studio_id = D.studio_id AND D.movie_id = %d)" %(movieID))]

  awards = [a for a in engine.execute("SELECT * FROM Award A\
    WHERE A.movie_id = %d" % (movieID))]

  distributors = [d for d in engine.execute("SELECT * FROM Distributor D\
    WHERE D.dist_id IN\
    (SELECT D.dist_id FROM Distributor D, Distributes Dis WHERE Dis.dist_id = D.dist_id AND Dis.movie_id = %d)" %(movieID))]

  movieCritics = [c for c in engine.execute("SELECT * FROM MovieCritic C, Rates R\
    WHERE C.critic_id = R.critic_id AND R.movie_id = %d" % (movieID))]


  print("WE'RE IN")
  print(distributors)
  print(movieCritics)


  return render_template("movie_page_specific.html", movies = movies, specificMovie= movie, movieActors = actors, movieProducers = producers, studios = studios, awards = awards, distributors = distributors, MovieCriticsRates = movieCritics)#movies = Movie.query.all())#, movies = Movie.query.all() )


#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#contributor shit

@app.route('/contributor_data')
def show_contributor():
  contributors = [c for c in engine.execute("SELECT * FROM Contributor")]

  return render_template("contributor.html", contributors = contributors)


@app.route('/contributor_data_specific', methods = ["POST"])
def show_contributor_specific():
  print "in show"
  contributorID = int(request.form['contributor_id'])

  contributor = [c for c in engine.execute("SELECT * FROM Contributor C WHERE C.contributor_id = %d" % (contributorID))]
  contributors = [c for c in engine.execute("SELECT * FROM Contributor")]


  actor_movie = [a for a in engine.execute("SELECT * FROM Movie M\
   WHERE M.movie_id IN \
   (SELECT M.movie_id FROM Contributor C, Acts A, Movie M\
    WHERE C.contributor_id = A.contributor_id AND M.movie_id = A.movie_id AND A.contributor_id = %d)" % (contributorID))]

  producer_movie = [p for p in engine.execute("SELECT * FROM Movie M\
   WHERE M.movie_id IN \
   (SELECT M.movie_id FROM Contributor C, Produces P, Movie M\
    WHERE C.contributor_id = P.contributor_id AND M.movie_id = P.movie_id AND P.contributor_id = %d)" % (contributorID))]

  return render_template("contributor_data_specific.html", contributors = contributors, specificContributor= contributor, actor_movie = actor_movie, producer_movie = producer_movie)

#--------------------------------------------
@app.route('/quick_qs')
def quick_qs():
  
  entities = ["distributor", "studio", "award", "contributor"]

  return render_template("quick_qs.html", entities = entities)


@app.route('/quick_qs_details', methods = ["POST"])
def show_quick_qs():

  entityType = str(request.form['entity_type'])


  if entityType == "distributor":
    #query for data on each subexample
    distributors = [d for d in engine.execute("SELECT * FROM Distributor")]
    attributes = ["name", "medium"]
    return render_template("display_quick_qs.html", entityTable = distributors, type = entityType, attributes = attributes)

  elif entityType == "studio":
    studios = [s for s in engine.execute("SELECT * FROM Studio")]
    attributes = ["name", "number_movies","founding_year"]
    return render_template("display_quick_qs.html", entityTable = studios, type = entityType, attributes = attributes)
    
  elif entityType == "award":
    awards = [a for a in engine.execute("SELECT * FROM award")]
    attributes = ["type", "category", "year"]
    return render_template("display_quick_qs.html", entityTable = awards, type = entityType, attributes = attributes)
    
  elif entityType == "contributor":
    contributors = [a for a in engine.execute("SELECT * FROM contributor")]
    attributes = ["name", "number_movies", "gender", "birth_year"]
    return render_template("display_quick_qs.html", entityTable = contributors, type = entityType, attributes = attributes)



@app.route('/quick_qs_order', methods = ["POST"])
def show_quick_qs_order():
  """Note: The user has to use the 'back' button to change entity type
  We don't handle that here."""

  orderby_attribute = str(request.form['orderby_attribute'])

  orderBy_vs_type = [y for y in (x.strip() for x in orderby_attribute.split(',')) if y]
  orderBy = orderBy_vs_type[0]
  entityType = orderBy_vs_type[1]

  print orderBy_vs_type

  if entityType == "distributor":
    #query for data on each subexample
    distributors = [d for d in engine.execute("SELECT * FROM Distributor ORDER BY %s" % (orderBy))]
    print distributors
    attributes = ["name", "medium"]
    return render_template("display_quick_qs.html", entityTable = distributors , type = entityType, attributes = attributes)
  
  elif entityType == "studio":
    studios = [s for s in engine.execute("SELECT * FROM Studio ORDER BY %s" % (orderBy))]
    attributes = ["name", "number_movies","founding_year"]
    return render_template("display_quick_qs.html", entityTable = studios, type = entityType, attributes = attributes)
    
  elif entityType == "award":
    awards = [a for a in engine.execute("SELECT * FROM award ORDER BY %s" % (orderBy))]
    attributes = ["type", "category", "year"]
    return render_template("display_quick_qs.html", entityTable = awards, type = entityType, attributes = attributes)
    
  elif entityType == "contributor":
    contributors = [a for a in engine.execute("SELECT * FROM contributor ORDER BY %s" % (orderBy))]
    attributes = ["name", "number_movies", "gender", "birth_year"]
    return render_template("display_quick_qs.html", entityTable = contributors, type = entityType, attributes = attributes)




@app.route('/quick_studio')
def show_studio():
    s_attributes = [studio_id, founding_year, number_movies, name]
    return render_template("contributor.html", contributors = contributors)

@app.route('/quick_award')
def show_award():
    a_attributes = [award_id, movie_id, "type", category, year]
    return render_template("contributor.html", contributors = contributors)

@app.route('/quick_contributor')
def show_contributors():
    c_attributes = [contributor_id, name, number_movies, gender, birth_year]
    return render_template("contributor.html", contributors = contributors)

#--------------------------------------------
@app.route('/usercritic')#, methods=['POST'])
def parse_request():

  movies = [m for m in engine.execute("SELECT * FROM Movie")]

  userReviews = [u for u in engine.execute("SELECT * FROM Usercritic U, Reviews R, Movie M WHERE U.username = R.username AND R.movie_id = M.movie_id ORDER BY R.rating DESC")] 
  print userReviews
  #name = request.form.get('name')
  return render_template("usercritic.html", userReviews = userReviews, movies = movies)


@app.route('/submit_review', methods = ["POST"])
def push_to_database():

  #print "HELELELELELELELELLELELELELELELELELELELLE"
  movies = [m for m in engine.execute("SELECT * FROM Movie")]

  username = request.form['username_value']
  username_formatted = "'"+request.form['username_value']+"'"

  age =  int(request.form['age'])
  gender = "'" + request.form['gender'] + "'"

  #May have to change movie to movie_id because movie names are not unique
  movieID = int(request.form['movie_id_to_review'])
  review = int(request.form['user_review'])

  print username, " ", movieID, " ",review


  db_users = [un[0] for un in engine.execute("SELECT username FROM Usercritic U")]
  print "-------------------------------------"
  #print db_users


  attemptUser = "(u"+username+",)"
  print "attemptUssr: " + attemptUser

  for a in db_users:
    print str(a) == attemptUser
    print a == attemptUser



  if username not in db_users:
    print "Adding a new user--------------------------------------------------"
    engine.execute("INSERT INTO Usercritic Values(%s, %s, %d)" % (username_formatted, gender, age))


  print [mv[0] for mv in engine.execute("SELECT movie_id FROM Usercritic U, Reviews R WHERE U.username = R.username AND U.username = %s" % (username_formatted))]  
  print "movie id: " + str(movieID)

  if movieID in [mv[0] for mv in engine.execute("SELECT movie_id FROM Usercritic U, Reviews R WHERE U.username = R.username AND U.username = %s" % (username_formatted))]:
    print "You cannot rate the same movie--------------------------------------------------."
    userReviews = [u for u in engine.execute("SELECT * FROM Usercritic U, Reviews R, Movie M WHERE U.username = R.username AND R.movie_id = M.movie_id ORDER BY R.rating DESC")] 
    return render_template("usercritic.html", userReviews = userReviews, movies = movies)


  engine.execute("INSERT INTO Reviews Values(%d, %d, %s)" % (movieID, review, username))

  userReviews = [u for u in engine.execute("SELECT * FROM Usercritic U, Reviews R, Movie M WHERE U.username = R.username AND R.movie_id = M.movie_id ORDER BY R.rating DESC")] 
  return render_template("usercritic.html", userReviews = userReviews, movies = movies)










"""
-----------------------------------
"""








@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
