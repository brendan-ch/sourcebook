# Sourcebook (working title)

A lightweight, self-contained CMS for class websites.

## Developer Setup

Prerequisites:

- Python 3.12
- MySQL 9.0.1
- MySQL shell
- Docker (for tests)

### MySQL

Database schema definitions are located under
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

At this stage, you can also load the database with some sample data
located under `sql/setup_playground_data.sql`.

```bash
$ mysql -u <username> -p --host=<hostname> --port=<port> sourcebook < sql/setup_playground_data.sql
```

### Environment variables

Duplicate the `.env.example` file, name it `.env`, and set the variables.

See [the Flask documentation](https://flask.palletsprojects.com/en/stable/config/#SECRET_KEY)
for how to quickly generate the `FLASK_APP_SECRET_KEY` value.

### Python

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
