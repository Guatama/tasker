from multiprocessing import Process, Queue, queues
from multiprocessing import Lock as Lock_mp
from threading import Thread, Lock

from pprint import pprint
import json
import argparse

import jsonschema

from uuid import uuid4

# Register for task-units
TASK_LINE = {}
TASK_QUEUE = {}


class Task_IO():
    """Class wrapper for IO info about
    tasks
    """
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.id = uuid4().hex
        self.status = "Init"
        self.result = None


class BaseTask(Process):
    """Base class for creating process-class for tasks
    """
    name = None
    json_schema = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Registration of child class in TASK_LINE
        """
        super().__init_subclass__(**kwargs)

        if hasattr(cls, 'run_task'):
            raise NotImplementedError
        if cls.name is not None:
            TASK_LINE[cls.name] = cls

    def __init__(self, task: Task_IO, our_connection: Queue):
        super().__init__()
        self.task = task
        self.connection = our_connection
        self.mp_lock = Lock_mp()

    def run_task(self, *args, **kwargs):
        """Override me"""
        pass

    def run(self):
        """Run function which override Process.run - and automaticaly
        execute when we starting the process (BaseTask_obj.start())
        """
        try:
            self.task.result = self.run_task(**self.task.params)
            self._return_result()

        except KeyError as e:
            error_text = f"KeyError: {e.args[0]}"
            self._return_result(err_msg=error_text)
            return
# BUG Serialize exception
# TODO Check for None
        except Exception as e:
            self._return_result(err_msg=e.args[0])
            return

    def _return_result(self, err_msg=None):
        """Put result of task into inter-process
        queue

        Keyword Arguments:
            err_msg {[str]} -- error message for result (default: {None})
        """
        if err_msg is None:
            self.task.status = "Done"
        else:
            self.task.status = "Failed"
            self.task.result = err_msg
# BUG If object is not-serializable
        self.connection.put(self.task)


class TaskObserver(Thread):
    """Universal task-observer, which run in anather thread
    When thread.start() -> TaskObesrver.run() start the event-loop
    """
    def __init__(self):
        super().__init__()
        self.task_proc = {}
        self.thread_lock = Lock()
        self.mp_lock = Lock_mp()
        self.task_updates = Queue()
        self.task_id = 0

    def run(self):
        """Execute when Thread.start(). Event-loop for checking status of tasks and
        fetching result of task and join end-processes
        """
        self.check_init_task()
        while True:
            self.check_init_task()
            try:
                task = self.task_updates.get(True, 5)
                print(task.__dict__)
            except queues.Empty:
                self.check_init_task()
                continue

            if task.status == "Done":
                self._result_out(task)
                self.task_proc[task.id].join()
                del self.task_proc[task.id]
                self.check_init_task()

            elif task.status == "Failed":
                self._result_out(task)
                self.task_proc[task.id].join()
                del self.task_proc[task.id]
                self.check_init_task()

            else:
                self._result_out(task)
                self.check_init_task()
                continue

            self.check_init_task()

    @staticmethod
    def validate_params(schema, params: dict):
                """Validate parameters using json_schema
                If schema is None -> Ok
                If schema is valid -> Ok
                If schema is not valid -> raise json_schema.ValidationError

                Arguments:
                    params {[dict, Any]} -- parameters for task-function
                """
                if schema:
                    jsonschema.validate(instance=params, schema=schema)

    def start_task(self, task: Task_IO):
        """
        Arguments:
            name {[type]} -- [description]
        """
        schema = TASK_LINE[task.name].json_schema
        try:
            self.validate_params(schema, task.params)
        except jsonschema.ValidationError as e:
            TASK_QUEUE[task.id].status = "Failed"
            TASK_QUEUE[task.id].result = "ValidationError: " + str(e.args[0])
            return

        task.status = "In process"

        process = TASK_LINE[task.name](task, self.task_updates)

        self.task_proc[process.task.id] = process
        process.start()

        TASK_QUEUE[task.id].status = task.status

    def _result_out(self, task_message):
        self.thread_lock.acquire()
        TASK_QUEUE[task_message.id] = task_message
        self.thread_lock.release()

    def check_init_task(self):
        self.thread_lock.acquire()
        try:
            init_tasks = [task[1] for task in TASK_QUEUE.items() if task[1].status == "Init"]
            for task in init_tasks:
                if task.id not in self.task_proc:
                    self.start_task(task)
        # TODO change this exception
        except Exception as e:
            pass

        finally:
            self.thread_lock.release()


# Decorator-function - interface for task-building
def task(in_name: str, in_json_schema: dict = None):
    """Decorator-interface for regestration function in TASK_LINE
    like Task() - object

    Arguments:
        name {[str]} -- key for TASK_LINE, and name-id for running Task

    Keyword Arguments:
        json_schema {[dict, Any]} -- schema for validation json parameters
                    (default: {None})
                                     json parameters == arguments for func_obj
    """
    def decorator(func):
        class New_Task(BaseTask):
            name = in_name
            json_schema = in_json_schema

            def run_task(self, *args, **kwargs):
                # args_len = func.__code__.co_argcount
                # args = func.__code__.co_varnames[:args_len]
                return func(*args, **kwargs)

        cls = New_Task

        return cls
    return decorator


def run_cli():
    """Parsing and running task from CLI
    """
    # Parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, nargs='?',
                        action='store', help='Name of registered task')
    parser.add_argument('-p', '--params', default='{}', type=str,
                        help='JSON with arguments for task')

    # Parsing arguments from CLI
    args = parser.parse_args()
    name = args.name
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print({"status": "JSONDecodeError",
               "msg": str(e.args[0])})
        return

    if name == 'runserver':
        # print(current_thread())
        observer = TaskObserver()
        from tasks.api import run_webserver

    # BUG Экспешен из дочернего треда в главном не перехватить
        try:
            proc = Thread(target=run_webserver)

            proc.start()
            observer.start()
            return
        except Exception as e:
            print(e)
            # observer.join()
            return
        finally:
            # observer.join()
            return

    elif name == 'ls':
        pprint({k: {'schema': v.json_schema} for (k, v) in TASK_LINE.items()})
        return


    # If task registered - run with arguments from params
    try:
        task = Task_IO(name, params)
        our_connection = Queue()

        schema = TASK_LINE[task.name].json_schema
        try:
            TaskObserver.validate_params(schema, task.params)
        except jsonschema.ValidationError as e:
            task.status = "Failed"
            task.result = "Schema ValidationError"
            print(task.__dict__)
            return

        proc = TASK_LINE[task.name](task, our_connection)
        proc.start()

        result = our_connection.get()
        print('RESULT:', result.result)
        return
    except KeyError as e:
        result = {"status": "KeyError",
                  "msg": str(e.args[0]) + " not registered in TASK_LINE"}
        print(result)
        return
