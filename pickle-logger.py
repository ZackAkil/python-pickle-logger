import os
import datetime
import pickle

from functools import wraps

SAVE_FOLDER = 'pickle_capture'

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

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
        pickle_file_name = f'{SAVE_FOLDER}/{function_execution_id}.pickle'

        # save all of the function input data to pickle file
        with open(pickle_file_name, "wb") as f:
          pickle.dump({'args':args, 
                       'kwargs':kwargs, 
                       'function_name':func.__name__}, f)

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

