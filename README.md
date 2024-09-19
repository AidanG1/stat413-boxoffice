# Setup
```bash
# clone the repo
git clone https://github.com/AidanG1/stat413-boxoffice.git

# move into the repo
cd stat413-boxoffice

# upgrade pip
pip install --upgrade pip

# create the venv
python3 -m venv venv

# activate the venv
source venv/bin/activate

# install the requirements
pip install -r requirements.txt

# install this package itself, this makes all the cool sibling imports work nicely
pip install -e .

# give permissions to get the data
chmod +x scripts/get_data

# run the script to get the data
scripts/get_data
```

# Running the code
```bash
python boxoffice/analysis/deadpool_graph.py
```

# Committing
This repository is using pre-commit. This means that sometimes your commits will fail due to formatting issues. Do not worry, the code automatically formats itself. Just re-add the files and commit again.

### Data Folder
This folder has the data -> https://rice.app.box.com/folder/284200986903

# Advanced
To update the data_link in the data_link.txt file, use these instructions: https://joelgrayson.com/software/box-download-link-generator
