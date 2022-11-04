from json import JSONDecodeError
import requests

# connect to the API

# local host
URL = f"http://localhost:8000"

# post multiple request to the API
def postMultiRequest(uploaded_file):

    files = {'csv_file':uploaded_file.getvalue()} # get the file from the user
    r = requests.post(url = URL + '/multi-predictions', files=files) # post the file to the API
    if(r.status_code == 200): # check if the request is successful
        return r.json()['results'] # only return the results
    else:
        print('Error During Query: postMultiRequest()')
        print(r)
        return r.status_code

# post single request to the API
def postJsonRequest(user_input):

    addr = URL + f'/single-prediction' # get the address of the API in fast.py
    r = requests.post (addr, json=user_input) # post the user input to the API
    if (r.status_code == 200): # check if the request is successful
        return r.json()['results'] # only return the results
    else:
        print('Error During Query: postJsonRequest()')
        print(r)
        return r.status_code


# get the past predictions from the API
def getHistory():
    r = requests.get(url = URL + '/past-predictions') # get the past predictions from the API
    if (r.status_code == 200):
        return r.json()['results']
    else:
        print('Error During Query: getHistory()')
        return r.status_code # return the status code if the request is not successful