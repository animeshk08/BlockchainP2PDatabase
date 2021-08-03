from __future__ import absolute_import
from __future__ import print_function
from sqlalchemy import create_engine
from locust import between, TaskSet, task, events, User
import time
from locust.contrib.fasthttp import FastHttpUser

from core.blockchain import Blockchain
# Instantiate the Blockchain
blockchain = Blockchain()


def create_conn():
    # print("Connecting to MySQL")
    return create_engine('mysql://iris:f0rwarder12345@10.15.17.33/p2p').connect()

def execute_query(query):
    _conn = create_conn()
    rs = _conn.execute(query)
    block = blockchain.mine("query", query) 
    return rs

'''
  The MySQL client that wraps the actual query
'''
class MySqlClient:

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                res = execute_query(*args, **kwargs)
                #print('Result ----------->' + str(res.fetchone()))
                events.request_success.fire(request_type="mysql",
                                            name=name,
                                            response_time=int((time.time() - start_time) * 1000),
                                            response_length=res.rowcount)
            except Exception as e:
                events.request_failure.fire(request_type="mysql",
                                            name=name,
                                            response_time=int((time.time() - start_time) * 1000),
                                            exception=e)

                print('error {}'.format(e))

        return wrapper

# class MySqlTaskSet(TaskSet):
#     #conn_string = 'employee-metrics:employee-metrics@emp1-metrics-db-1/emp'

#     @task(1)
#     def execute_query(self):
#         self.client.execute_query("select * from users")

# This class will be executed when you fire up locust
class MySqlLocust(FastHttpUser):
    # min_wait = 0.1
    # max_wait = 1
    # tasks = [MySqlTaskSet]
    # wait_time = between(min_wait, max_wait)

    def __init__(self, *args, **kwargs):
        super(MySqlLocust, self).__init__(*args, **kwargs) 
        self.client = MySqlClient()
    
    @task
    def execute_query(self):
        self.client.execute_query("select * from users")