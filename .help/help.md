# run the application

flask run

# initialize the db

flask init-db
flask --app flaskr init-db

# db upgrade

flask db init
flask db migrate
flask db upgrade

# install packages

pip install -r requirements.txt

# update requirements.txt and packages with latest version

pip install upgrade-requirements
upgrade-requirements

# changes to requirements.txt

pip freeze > requirements.txt
