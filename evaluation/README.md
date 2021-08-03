### This directory contatins scripts to test the proposed architecture.

> A single MySQL(8.0.26) relational database was used to test the performance of the added architecture.

> The experiments were performed on a 2 core Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz system with 2 GB RAM.

[Locust](https://locust.io/) is an open source tool which was used to load test the architecture.

### Intalling Locust:
```
pip3 install locust
```

### The files defined are as follows:
  * [load_test.py](./load_test.py): To evaluate native MySQL database.
  * [load_test_min.py](./load_test_mine.py): To evaluate MySQL with added blockchain and peer-to-peer network.

### Running the load tests:
 - After installing locust, run locust web UI by passing the file as:
 ```
# here file passed will be the configuration to be evaluated (native or with blockchain + p2p network)
locust -f "load_test.py"
 ```
  - Specify parameters for the load test
  ![Locust web UI](../images/locust-web.png)
 - Start the load test and below shows the example metrics observed:

   ![Locust Sample Test Report](../images/locust-test-report.png)

> More details on configuring locust can be found [here](https://docs.locust.io/en/stable/configuration.html)