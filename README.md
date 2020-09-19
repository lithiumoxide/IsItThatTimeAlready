# Is It That Time Already, Is It?
Python code for the Twitter account @IsItDarkAlready.

This code is designed for AWS Lambda with a Python 3.8 runtime, but it should run at least as far back 3.6, and probably even older.

The code requires a few third party libraries: `requests`, `tweepy`, and `arrow` (`boto3` is already available to Lambda functions by default). If you run this code locally you can install these libraries by running `pip3 install LIBRARY-NAME-HERE`. If you run it on Lambda, you'll need to package up these libraries into zip files to be used by Lambda Layers. If you don't want to do that, I've included the layers in the `layers` directory: upload the `python.zip` files to Lambda Layers and you'll be good to go.

You'll need a Twitter API account and appropriate access and consumer keys and secrets, and if you want to run it on Lambda you'll need an AWS account.