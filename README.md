# linkagg

Example implementation of link agreggation hashing algorithm. This is in response
to Christopher Hart's ([@_ChrisJHart](https://twitter.com/_ChrisJHart)) post [here](https://twitter.com/_ChrisJHart/status/1452343071484653578). This is by no means exhaustive or bug-free, it's just a fun
side-project to explore hashing algorithms and Ethernet link load-balancing.

## Installation

Clone the repo and cd into the directory: `git clone https://github.com/clay584/linkagg-hash.git && cd linkagg`

## Usage

`./demo.py <number_of_active_links> <num_of_unique_flows_to_generate>`

OR

`python -m linkagg <number_of_active_links> <num_of_unique_flows_to_generate>`

## Example Output

Running 10,000 frames through with an eight interface bundle.

```shell
> python linkagg_hash/linkagg_hash.py 8 10000

One frame for every flow only. We should see a uniform distribution
==================================================
Interface 1: 1263 frames
Interface 2: 1217 frames
Interface 3: 1277 frames
Interface 4: 1219 frames
Interface 5: 1216 frames
Interface 6: 1283 frames
Interface 7: 1235 frames
Interface 8: 1290 frames
==================================================

Now lets see it with two elephant flows. Sometimes those will hit the same interface
==================================================
Interface 1: 1263 frames
Interface 2: 11217 frames
Interface 3: 11277 frames
Interface 4: 1219 frames
Interface 5: 1216 frames
Interface 6: 1283 frames
Interface 7: 1235 frames
Interface 8: 1290 frames
==================================================
```

## Tests

How can we ensure we get it right? With tests of course! (I'm not saying there are
no bugs. I'm sure there are bugs.)

First, install the dev requirements: `pip install -r requirements-dev.txt`

Run `pytest -v`

```shell
❯ pytest -v
=========================== test session starts ===========================
platform linux -- Python 3.9.7, pytest-6.2.5, py-1.10.0,
pluggy-1.0.0 -- /home/jccurtis/code/personal/linkagg-hash/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/jccurtis/code/personal/linkagg-hash
collected 5 items

tests/test_linkagg.py::test_version PASSED                    [ 20%]
tests/test_linkagg.py::test_frames PASSED                     [ 40%]
tests/test_linkagg.py::test_one_intf PASSED                   [ 60%]
tests/test_linkagg.py::test_link_distribution PASSED          [ 80%]
tests/test_linkagg.py::test_hashes_are_deterministic PASSED   [100%]

============================ 5 passed in 0.37s ============================
```
