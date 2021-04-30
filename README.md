Backend for messenger (https://github.com/YAJATapps/Messenger)

Uses FastAPI framework.

To deploy to AWS:

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


Deploy the function.zip to AWS

Deployment method from (https://deadbearcode.com/simple-serverless-fastapi-with-aws-lambda/)
