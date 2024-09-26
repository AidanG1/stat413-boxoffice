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
source venv/bin/activate # for mac or linux
venv/Scripts/activate # for windows

# install the requirements
pip install -r requirements.txt

# install this package itself, this makes all the cool sibling imports work nicely
pip install -e .

# give permissions to get the data
chmod +x scripts/get_data

# run the script to get the data
scripts/get_data

# create the kernel so that the jupyter notebooks can use the venv
# only need to do this on mac or linux
python -m ipykernel install --user --name=boxoffice_kernel
# within each ipynb in vscode, type "ctrl+shift+p" and select "Notebook: Select Notebook Kernel" and select "boxoffice_kernel" from the "Jupyter Kernel..." dropdown
```

# Running the code
```bash
python boxoffice/analysis/deadpool_graph.py
```

# Exploring the database
Go to this website: https://sqliteviewer.app or download this VS Code extension: VSCode extension: https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer . Follow the instructions within the website to upload the database file. This file can be found in the stat413-boxoffice/boxoffice/db/data directory.

### Data Folder
This box folder in the cloud has the data -> https://rice.app.box.com/folder/284200986903

# Committing
This repository is using pre-commit. This means that sometimes your commits will fail due to formatting issues. Do not worry, the code automatically formats itself. Just re-add the files and commit again.

# Advanced
To update the data_link in the data_link.txt file, use these instructions: https://joelgrayson.com/software/box-download-link-generator
