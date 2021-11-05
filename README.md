# linkagg

Example implementation of link agreggation hashing algorithm. This is in response
to Christopher Hart's ([@_ChrisJHart](https://twitter.com/_ChrisJHart)) post [here](https://twitter.com/_ChrisJHart/status/1452343071484653578). This is by no means exhaustive or bug-free, it's just a fun
side-project to explore hashing algorithms and Ethernet link load-balancing.

## Installation

1. Make sure you have gcc installed (Ubuntu): `sudo apt update && sudo apt install build-essential`
2. Make sure you have Python 3.9.7 installed: [Pyenv](https://github.com/pyenv/pyenv#installation)
3. Clone the repo and cd into the directory: `git clone https://github.com/clay584/linkagg.git && cd linkagg`
4. Create a Python virtual environment: `python -m venv venv`
5. Activate the Python virtual environment: `source venv/bin/activate`
6. Install the Python dependencies: `pip install -r requirements-dev.txt`
7. Compile the cythonized code: `python setup.py build_ext --inplace`

## Usage

`./demo.py <number_of_active_links> <num_of_unique_flows_to_generate>`

OR

`python -m linkagg <number_of_active_links> <num_of_unique_flows_to_generate>`

## Example Output

Running 8,000 frames through with an eight interface bundle.

```shell
❯ ./demo.py 8 8000
One frame for every flow only. We should see a uniform distribution
==================================================
Egress Queue 1: 984 frames
Egress Queue 2: 978 frames
Egress Queue 3: 1025 frames
Egress Queue 4: 980 frames
Egress Queue 5: 1015 frames
Egress Queue 6: 1065 frames
Egress Queue 7: 988 frames
Egress Queue 8: 965 frames
==================================================

Now lets see it with two elephant flows. Sometimes those will hit the same interface
==================================================
Egress Queue 1: 984 frames
Egress Queue 2: 978 frames
Egress Queue 3: 11025 frames
Egress Queue 4: 980 frames
Egress Queue 5: 1015 frames
Egress Queue 6: 1065 frames
Egress Queue 7: 988 frames
Egress Queue 8: 10965 frames
==================================================
Total hashing time: 32.13191032409668 ms
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
