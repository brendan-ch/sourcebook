# Sourcebook (working title)

A lightweight, self-contained CMS for class websites.

## Developer Setup

Prerequisites:

- Python 3.12
- MySQL 9.0.1
- MySQL shell
- Docker (for tests)

The first step is to create and load the database schema, located under
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


