Make sure to create and activate a venv and then install the requirements.txt file.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# install this package itself, this makes all the cool sibling imports work nicely
pip install -e .
```
