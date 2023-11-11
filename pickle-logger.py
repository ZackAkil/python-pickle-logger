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
          pickle.dump({'args':args, 'kwargs':kwargs}, f)

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
    function_input_data = pickle.load(f)

  args = function_input_data.get('args')
  kwargs = function_input_data.get('kwargs')
  
  # run function without Pickle Logging it again
  function_without_decorator = function.__wrapped__
  function_without_decorator(*args, **kwargs)
