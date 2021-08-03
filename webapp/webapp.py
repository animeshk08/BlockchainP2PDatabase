import re
import sys
sys.path.append('../')
from uuid import uuid4

import environ
import MySQLdb.cursors
from core.backup import db_backup, db_recovery
from core.blockchain import Blockchain
from core.ipfsclient import IpfsClient
from flask import Flask, jsonify, render_template, request
from flask_mysqldb import MySQL
from ipfshttpclient.client import block
from werkzeug.wrappers import response



"""
Fetch environment variables from .env in parent directory
"""
env = environ.Env()
env.read_env('../.env')

"""
Initialize the Flask App
"""
app = Flask(__name__)
app.secret_key = 'your secret key'

"""
Set Flask App configs for the MySQL database connection
"""
app.config['MYSQL_HOST'] = env("WEBAPP_MYSQL_HOST")
app.config['MYSQL_USER'] = env("WEBAPP_MYSQL_USER")
app.config['MYSQL_PASSWORD'] = env("WEBAPP_MYSQL_PASS")
app.config['MYSQL_DB'] = env("WEBAPP_MYSQL_DBNAME")
mysql = MySQL(app)

"""
Generate a globally unique address for this node
"""
node_identifier = str(uuid4()).replace('-', '')

"""
Instantiate the Blockchain
"""
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine(type, command):
    """
    Manually mine a new block into the blockchain
    """

    block = blockchain.mine(type, command)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'command': block['command'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    # Return response as a json
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Return the blockchain
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/users', methods=['GET'])
def users():
    """
    Fetch all the users in the database
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users')
    user_list = cursor.fetchall()

    return render_template('users.html', user_list=user_list)


@app.route('/backup', methods=['GET'])
def backup():
    """
    Generate a database backup file and store it inside the IPFS network
    """
    file_path = db_backup()

    client = IpfsClient()
    client.connect()
    node = client.create_backup(file_path)
    client.close()

    blockchain.mine(type='backup', body=node['Hash'])

    return "Backup successful", 200


@app.route('/retrieve', methods=['GET'])
def retrieve():
    """
    Retrieve the database file from the IPFS network and load it into the database
    """
    backup_file = env("TEMP_BACKUP_STORE_PATH")
    response = blockchain.chain

    cid = None

    # Fetch latest backup block in blockchain
    for block in reversed(blockchain.chain):
        if block['type'] == 'backup':
            cid = block['body']
            break

    client = IpfsClient()
    client.connect()
    content = client.retrieve_backup(cid)
    client.close()
    response = cid

    # Write the backup into a temporary file TEMP_BACKUP_STORE
    with open(backup_file, "wb") as file:
        file.write(content)

    # Restore the backup into the Destination Database
    db_recovery(backup_file)

    blockchain.mine(type='recovery', body=cid)

    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Resolve the blockchain based on consensus algorthim when multiple nodes are conencted
    """
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user
    """
    msg = ''
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        organisation = request.form['organisation']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        postalcode = request.form['postalcode']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        elif not re.match(r'[0-9]+', postalcode):
            msg = 'Postal code should be a number'
        else:
            command = "INSERT INTO users VALUES('{}', '{}' , '{}' , '{}' , '{}' , '{}' , '{}' , {});".format(
                username, email, organisation, address, city, state, country, postalcode)
            cursor.execute(command)
            mysql.connection.commit()
            blockchain.mine(type='query', body=command)
            msg = 'You have successfully registered !'
    elif request.method == 'GET':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
