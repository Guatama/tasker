from flask import Flask, request
from threading import Lock
import tasks.tasks as tasks


TASK_LINE = tasks.TASK_LINE
TASK_QUEUE = tasks.TASK_QUEUE
thread_lock = Lock()

# TODO In future - use Blueprints for error-handling before creating app
app = Flask(__name__)


@app.route("/", methods=['GET'])
def get_tasks():
    """GET method returns json with TASK_LINE
    """
    return {"TASK_LINE":
            {k: {'schema': v.json_schema} for (k, v) in TASK_LINE.items()}}


@app.route("/tq", methods=['GET'])
def get_queue():
    """GET method returns json with TASK_LINE
    """
    return {"TASK_QUEUE":
            {k: {'status': v.status, "result": v.result} for (k, v) in TASK_QUEUE.items()}}


@app.route("/api", methods=['POST'])
def task_api():
    """POST method for running task by name

    Arguments:
        name {[str]} -- name of task in tasks.TASK_LINE
        params {[dict]} -- json data from request -> kwargs for task
    """

    try:
        json_input = request.get_json()
        method = json_input['method']

        if method == 'start':
            name = json_input['task_name']
            params = json_input['params']
            task = tasks.Task_IO(name=name, params=params)
            thread_lock.acquire()
            TASK_QUEUE[task.id] = task
            thread_lock.release()
            print("START:", task.__dict__)
            return task.__dict__

        elif method == 'status':
            thread_lock.acquire()
            task = TASK_QUEUE[json_input['task_id']]
            thread_lock.release()
            print("STATUS:", task.id, task.status)
            return {"task_id": task.id,
                    "task_type": task.name,
                    "status": task.status}

        elif method == 'get_result':
            thread_lock.acquire()
            task = TASK_QUEUE[json_input['task_id']]
            thread_lock.release()

            if task.status == 'Done' and task.result:
                print("RESULT:", task.result)
                result = {"task_id": task.id,
                          "task_type": task.name,
                          "result": task.result}
                return result
        else:
            return {"status": "API Method not exist"}

    except KeyError as e:
        result = {"status": "KeyError",
                  "msg": str(e.args[0]) + " not registered in TASK_LINE"}
        print(result)
        return result

    except Exception as e:
        return {"status": str(e.code), "msg": str(e.get_description())}


def run_webserver():
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
