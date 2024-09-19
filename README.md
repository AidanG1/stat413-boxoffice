# Setup
```bash
# clone the repo
git clone https://github.com/AidanG1/stat413-boxoffice.git

# move into the repo
cd stat413-boxoffice

# create the venv
python3 -m venv venv

# activate the venv
source venv/bin/activate

# install the requirements
pip install -r requirements.txt

# install this package itself, this makes all the cool sibling imports work nicely
pip install -e .
```

https://rice.app.box.com/folder/284200986903

Find the most recent version of data and rename it as `data.sqlite` and place it in boxoffice/db/data

# Running the code
```bash
python boxoffice/analysis/deadpool_graph.py
```
