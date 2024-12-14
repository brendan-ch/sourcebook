# Sourcebook (working title)

A lightweight, self-contained CMS for class websites.

## Demo Video

Demo video is located at `/docs/demo.mp4`.

## Developer Setup

Prerequisites:

- Python 3.12
- MySQL 9.0.1
- MySQL shell
- Docker (not required unless you want to run the tests)

### MySQL

Database schema definitions are located in
`sql/setup_schema.sql`. With the MySQL shell installed, you can run
something like this to create your schema:

```shell
# Start the shell
# Default host: localhost
# Default port: 3306
$ mysql -u <username> -p --host=<hostname> --port=<port>

# Create a new schema
mysql> CREATE SCHEMA sourcebook;
```

Then, exit the MySQL shell with Ctrl+D and load the schema definition:

```shell
$ mysql -u <username> -p --host=<hostname> --port=<port> sourcebook < sql/setup_schema.sql
```

I also recommend loading the sample data
located in `sql/setup_playground_data.sql`.

```shell
$ mysql -u <username> -p --host=<hostname> --port=<port> sourcebook < sql/setup_playground_data.sql
```

### Environment variables

Duplicate the `.env.example` file, name it `.env`, and set the variables
to point to your MySQL database instance.

See [the Flask documentation](https://flask.palletsprojects.com/en/stable/config/#SECRET_KEY)
for how to quickly generate the `FLASK_APP_SECRET_KEY` value.

### Main app

Set up your Python virtual environment:

```shell
# Create and activate the virtual environment
$ python -m venv .venv
$ source .venv/bin/activate

# Install packages
$ pip install -r requirements.txt
```

You're now ready to start the application.

```shell
$ python app.py
```

The application will run at http://localhost:5000 by default.

### Admin app

Some functionality (e.g. exports) is located in a separate interface which is
started separately from the main app. To start this app, run `app.py`
with the `--admin` flag:

```shell
$ python app.py --admin
```

Go to http://localhost:5000 to access the interface.
