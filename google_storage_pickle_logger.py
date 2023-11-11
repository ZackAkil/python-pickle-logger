# %%writefile pickle_logs_config.json
# {"google_storage_bucket":"your-bucket-name", "google_storage_folder":"test"}


import os
import datetime
import pickle

from functools import wraps

import json

with open("pickle_logs_config.json", "r") as f:
    json_data = json.load(f)
    google_storage_bucket = json_data.get('google_storage_bucket')
    google_storage_folder = json_data.get('google_storage_folder')



def pickle_log(func):

    """Pickle logs a function call.

    This decorator pickles the function's arguments and keyword arguments to a file.
    This can be useful for debugging and generating tests.

    Args:
      func: The function to decorate.

    Returns:
      A decorated function that pickles its arguments and keyword arguments to a file before calling the original function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        start_time = datetime.datetime.now()
        # create the id of pickle log

        function_execution_id = f'{func.__name__} {start_time.strftime("%d-%m-%Y %H:%M:%S.%f")}'
        pickle_file_name = f'{function_execution_id}.pickle'

        # save all of the function input data to pickle file

        with tempfile.NamedTemporaryFile(delete=False) as f:
          pickle.dump({'args':args,
                       'kwargs':kwargs,
                       'function_name':func.__name__}, f)
          
        # upload to cloud bucket
        gs_location = f'{google_storage_bucket}/{google_storage_folder}/{pickle_file_name}'
        upload_to_gcs(local_filename=f.name, gs_location=gs_location)

        # remove local pickle
        os.remove(f.name)

        # calculate how long the pickling took (just in case it's too much overhead)
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        print(f"🥒 Pickle logged {pickle_file_name} in {elapsed_time} seconds 🪵")

        # run function as normal
        output = func(*args, **kwargs)
        return output

    return wrapper


def reheat_pickle_log(pickle_capture_file_name, function):
  """Reheats a pickled function log.

  Args:
    pickle_capture_file_name: The name of the pickled function log file.
    function: The function whose log should be reheated.

  Returns:
    None.
  """

  print('🔥 Reheating pickle log 🥒 ')

  # get data from pickled log
  with open(pickle_capture_file_name, "rb") as f:
    pickle_data = pickle.load(f)

  args = pickle_data.get('args')
  kwargs = pickle_data.get('kwargs')

  # run function without Pickle Logging it again
  function_without_decorator = function.__wrapped__
  return function_without_decorator(*args, **kwargs)


import json

def generate_test(pickle_capture_file_name, function):
  """Generates a test code for a pickled function log.
  Only good when the outputs are simple, otherwise good for template test.

  Args:
    pickle_capture_file_name: The name of the pickled function log file.
    function: The function whose log should be used to generate the test code.
  Returns:
    None.
  """

  print('🧪 Generating test code 🥒 ')

  # get data from pickled log
  with open(pickle_capture_file_name, "rb") as f:
    pickle_data = pickle.load(f)

  function_name = pickle_data.get('function_name')
  function_output = reheat_pickle_log(pickle_capture_file_name, function)
  # print out the code template
  print('----generated test below----\n')
  print(f'def test_{function_name}_{random_id(5)}():')
  print(f'  pickle_capture_file_name = "{pickle_capture_file_name}"')
  print(f'  function_output = reheat_pickle_log(pickle_capture_file_name, {function_name})')
  print(f'  assert function_output == {json.dumps(function_output)}')


import random
import string

def random_id(n):
  """Generates a random ID of length `n`.

  Args:
    n: The length of the random ID.

  Returns:
    A random ID of length `n`.
  """
  chars = string.ascii_uppercase + string.digits
  return ''.join(random.SystemRandom().choice(chars) for _ in range(n))



# pip install google-cloud-storage

import tempfile
from google.cloud import storage

def upload_to_gcs(local_filename:str, gs_location:str) -> None:
    """Uploads a file to a Google Storage bucket.
    """
    bucket_name, blob_name = gs_location.replace('gs://', '').split('/', 1)
    
    print(f'⬆️ Uploadting {local_filename} to bucket 🪣:{bucket_name}, blob {blob_name} ...')

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_filename)
    print(f'✅ Uploaded {local_filename} to bucket:{bucket_name}, blob {blob_name}')


def download_from_gcs(gs_location:str) -> str:
    """Loads a file from Google Storage.
    """
    print(f'⬇️ Downloading file :{gs_location}...')
    
    bucket_name, blob_name = gs_location.replace('gs://', '').split('/', 1)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        blob.download_to_file(temp)
    print(f'✅ Downloaded file :{gs_location}')
    return temp.name

