#emulambda -v lambda.lambda_handler testJson/test.json


python-lambda-local -f lambda_handler -t 5 lambda.py testJson/test.json
