This directory contatins scripts to test the proposed architecture.

> A single MySQL(8.0.26) relational database was used to test the performance of the added architecture.


> The experiments were performed on a 2 core Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz system with 2 Gb RAM.

[Locust](https://locust.io/) is an open source tool used to load test the architecture.

Intalling Locust:
```
pip install locust
```

The files defined are as follows:
  * [load_test.py](./load_test.py): To evaluate native MySQL database.
  * [load_test_min.py](./load_test_mine.py): To evaluate MySQL with added blockchain and peer-to-peer network.