This is a simple implementation of the blockchain and peer-to-peer network based database. A single page form is available to register a new user.

### Pre-running instructions

* Add your know database configuration by modifying the below lines in [webapp.py](./webapp.py)

```
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
```

* Create a database with a single user table.

```
mysql> create database db;
mysql> use db;
CREATE TABLE users1 (username varchar2(20), email varchar(20), organisation varchar(50), address varchar(255), city varchar(50), state varchar(50), country varchar(50), postalcode int(10), PRIMARY KEY(username));
```

### Running instructions

```
python3 webapp.py
```
Go to the URL http://192.168.0.5:5000/register

### Paths

* /register : Register a new entry
* /chain : Display the current status of the blockchain
* /backup : Create a database backup
* /retrieve : Retrieve the latest database backup
* /users : Get all the users inside the database