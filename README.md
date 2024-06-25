Backend for messenger (https://github.com/YAJATapps/Messenger)

Uses FastAPI framework.

1. Remove mangum to run locally.  
  
OR  
  
2. Deploy to AWS:

# Setup virtualenv
virtualenv -p python3.9 env

source ./env/bin/activate

# Install dependencies
pip install fastapi

pip install mangum

pip install mysql-connector-python

# Zip the dependencies and python file
cd env/lib/python3.9/site-packages

zip -r9 ../../../../function.zip

cd ../../../..

zip -g ./function.zip -r api.py


Deploy the function.zip to AWS.
