# Reputation Game V2

### Install dependencies

Navigate terminal to the root of the project folder.

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the codebase

Navigate terminal to the root of the project folder.

```
python -m main.py -r -o -p -pr
```

Args can be passed individually or combined.

- r = run
- o = overwrite existing simulation
- p = launch plotter
- pr = benchmarking the postprocessor

### Create documentation

Navigate terminal to the root of the project folder.

```
cd docs
make html
open _build/html/index.html
```

To create a Call Graph for some package:

```
cd docs
python call_graph_maker.py PATHNAME
open _build/html/index.html
```

Make sure that PATHNAME is written starting from the root folder. Examples:

```
python call_graph_maker.py simulate
python call_graph_maker.py simulate/agent
python call_graph_maker.py evaluate
```

The resulting call graph is stored as a PNG in docs/call_graphs.
