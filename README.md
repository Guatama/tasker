Side package:
jsonschema
flask
pytest

Main:
* tasks -- main lib
* api -- api (flask) for tasks

Tests:
* cli_test -- main test file, ready for cli using and runserver (that how users should use it)
* test_main -- main pytest with 42 passed tests
* test_cases -- cases for pytests in test_main (Task.run() and API post methods)
* test_stress_api -- little stress test for multiprocess 


==========================================================
```
API:
# my_tasks.py
import tasks

# Define your task

# With decorator
@tasks.task("name_of_task_1", json_schema=None)
def function(params):
	some_arg_1, some_arg_2 = params["some_arg_1"], params["some_arg_2"]
	# do something
	result = some_arg_1 * some_arg_2
	return result

# With class-inheritance
class A(tasks.BaseTask):
	name = "name_of_task_2"
	json_schema = None # If not none -> validate params

	def run(params):
		some_arg_1, some_arg_2 = params["some_arg_1"], params["some_arg_2"]
		# do something
		result = some_arg_1 * some_arg_2
		return result

if __name__ == "__main__":
	tasks.cli_run()
```
==========================================================
In terminal:
```
> python my_tasks.py name_of_task_2 -p '{"some_arg_1": 5, "some_arg_2": 10}'
>- 50
```
==========================================================
# With API
```
> python my_tasks.py runserver

-> htt post http://0.0.0.0:5000/api
Body of request (JSON):
'{"method": "start", "task_name": "name_of_task_1", "params": {"some_arg_1": 5, "some_arg_2": 10}'
>- {"result": 50}
```