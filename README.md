# Alexa Skill Dungeon Beasts
Code for my Alexa Skill Dungeon Beasts

**Usage**

The Alexa Skill calls lambda.py

**Testing locally**

I haven't figured out how to do CI testing with Alexa Skills and Python code. `emulambda` has worked just fine for local manual testing.


Install emulambda. `pip install -e emulambda`
See https://github.com/fugue/emulambda for more information

Run emulambda

`emulambda lambda.lambda_handler testjson/test.json`

Add `-v` for more information.

`emulambda lambda.lambda_handler testjson/test.json -v`


**Monster Manual Data**

Run `populate_bestiary_dynamo.rb` to insert the beasts in `beastiary.db` into your DynamoDB. The default is to a local instance of DynamoDB.


**Requirements**

- Python 2.7
- emulambda
- AWS account with credentials on your development machine
- Alexa Developer account
- DynamoDB configured and loaded with the D&D 5e Monster Manual.
