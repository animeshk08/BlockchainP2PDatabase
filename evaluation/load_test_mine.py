from __future__ import absolute_import, print_function

import sys
sys.path.append('../')
import time

import environ
from core.blockchain import Blockchain
from locust import User, between, events, task
from sqlalchemy import create_engine

"""
Fetch environment variables from .env in parent directory
"""
env = environ.Env()
env.read_env('../.env')

# Instantiate the Blockchain
blockchain = Blockchain()


def create_conn():
    # create_engine will require the database connection configurations
    return create_engine(env("LOAD_TEST_DBENGINE")).connect()


def execute_query_mine(query):
    _conn = create_conn()
    rs = _conn.execute(query)
    block = blockchain.mine("query", query)
    return rs


"""
  The MySQL client that wraps the actual query
"""
class MySqlClient:

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                res = execute_query(*args, **kwargs)
                events.request_success.fire(request_type="mysql",
                                            name=name,
                                            response_time=int(
                                                (time.time() - start_time) * 1000),
                                            response_length=res.rowcount)
            except Exception as e:
                events.request_failure.fire(request_type="mysql",
                                            name=name,
                                            response_time=int(
                                                (time.time() - start_time) * 1000),
                                            exception=e)

                print('error {}'.format(e))

        return wrapper


# This class will be executed when you fire up locust
class MySqlLocust(User):

    def __init__(self, *args, **kwargs):
        super(MySqlLocust, self).__init__(*args, **kwargs)
        self.client = MySqlClient()

    @task
    def execute_query(self):
        # pass the query to be executed
        self.client.execute_query_mine(env("LOAD_TEST_QUERY"))
