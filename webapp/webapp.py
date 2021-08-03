from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from ipfshttpclient.client import block
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.wrappers import response
from core.backup import db_backup, db_recovery
from core.blockchain import Blockchain
from core.ipfsclient import IpfsClient
import re

# Instantiate the Node
app = Flask(__name__)

app.secret_key = 'your secret key'
  
  
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'animesh987'
app.config['MYSQL_DB'] = 'test1'
  
  
mysql = MySQL(app)
  
# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
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
    Get all the users inside the database
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

    response = node

    return jsonify(response), 200

@app.route('/retrieve', methods=['GET'])
def retrieve():
    """
    Retrieve the database file from the IPFS network and load it into the database
    """
    backup_file = "./test2.txt"
    response = blockchain.chain
    print(blockchain.chain)

    cid = None

    for block in reversed(blockchain.chain):
        if block['type'] == 'backup':
            cid = block['body']
            break

    client = IpfsClient()
    client.connect()

    print(cid)

    content = client.retrieve_backup(cid)

    print(content)

    client.close()

    response = cid

    with open(backup_file, "wb") as file:
        file.write(content)

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


@app.route('/register', methods =['GET', 'POST'])
def register():
    """
    REgister a new user
    """

    msg = ''
    print(request.method)
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
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
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
            command = "INSERT INTO users VALUES('{}', '{}' , '{}' , '{}' , '{}' , '{}' , '{}' , {});".format(username, email, organisation, address, city, state, country, postalcode )
            print(command)
            cursor.execute(command)
            mysql.connection.commit()
            print("comm",command)
            blockchain.mine(type='query',body=command)
            msg = 'You have successfully registered !'
    elif request.method == 'GET':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
