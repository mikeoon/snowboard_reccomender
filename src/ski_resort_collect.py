import pandas as pd
import json
import requests

api_url = 'http://clientservice.onthesnow.com/externalservice/authorization/token/'

test_url = 'http://clientservice.onthesnow.com/externalservice/authorization/token/test%40mountainnews.com/test123!'
get_token = 'authorization/token/youngjungmyoon@gmail.com/YMY01191994!'

test_2url = 'https://www.espn.com'
# Parameters for the API request: We want the Unicorn page encoded as json.



r = requests.get(test_2url)

print(r)































