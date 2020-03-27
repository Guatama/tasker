import pytest
import copy
import json

from tasks import tasks

from tests.test_cases import Case, CHARCOUNT_CASES, MANYARG_CASES,\
                       MULT_CASES, MULTIPRINT_CASES


FUNC_MOCK = object.__call__
assert len(tasks.TASK_LINE) == 0


# Preparations
@pytest.fixture(scope='function', name='TASK_LINE')
def create_four_test_func():
    import tests.cli_example


@pytest.fixture(scope='function', name='TASK_LINE_empty')
def create_none_test_func():
    tasks.TASK_LINE = dict()


@pytest.fixture(scope='function', name='API_test')
def create_test_app():
    from api import app
    testing_client = app.test_client()
    return testing_client


# Testing registration API
def test_registration_decorator(TASK_LINE_empty: pytest.fixture):
    assert len(tasks.TASK_LINE) == 0

    for i in range(10):
        i_name = 'task_' + str(i)
        tasks.task(i_name)(FUNC_MOCK)
        assert len(tasks.TASK_LINE) == i + 1
        assert tasks.TASK_LINE[i_name].name == i_name
        assert tasks.TASK_LINE[i_name].schema == None


def test_registration_derived_class(TASK_LINE_empty: pytest.fixture):
    assert len(tasks.TASK_LINE) == 0

    test_TASK_LINE = dict()

    for i in range(10):
        i_name = 'task_' + str(i)

        test_TASK_LINE[i_name]= type(i_name + "_cls",
                                     (tasks.BaseTask,),
                                      {"name": i_name, "run": FUNC_MOCK})

        assert len(tasks.TASK_LINE) == i + 1
        assert tasks.TASK_LINE[i_name].name == i_name
        assert tasks.TASK_LINE[i_name].schema == None

    assert len(test_TASK_LINE) == len(tasks.TASK_LINE)


# Test of constructing class Task()
def test_construct_Task_1(TASK_LINE_empty: pytest.fixture):
    assert len(tasks.TASK_LINE) == 0

    with pytest.raises(KeyError):
        tasks.Task('task_without_functinon', 50)


def test_construct_Task_2(TASK_LINE_empty: pytest.fixture):
    assert len(tasks.TASK_LINE) == 0

    with pytest.raises(KeyError):
        tasks.Task('task_with_wrong_schema', FUNC_MOCK, list)


def test_construct_Task_3(TASK_LINE_empty: pytest.fixture):
    new_task = tasks.Task('task_1', FUNC_MOCK)

    assert len(tasks.TASK_LINE) == 0
    assert isinstance(new_task, tasks.Task)
    assert new_task.schema == None


# Test for Task.run() method
CASES = [*CHARCOUNT_CASES, *MANYARG_CASES, *MULT_CASES, *MULTIPRINT_CASES]

@pytest.mark.parametrize('t', CASES, ids=str)
def test_run_func(t: Case, TASK_LINE: pytest.fixture) -> None:
    """
        Testing of function from cli_test.py
        ['charcount', 'manyarg', 'mult', 'multiprint']
        by method Task.run()
    """
    params_copy = copy.deepcopy(t.params)
    answer = tasks.TASK_LINE[t.name].run(t.params)

    assert len(tasks.TASK_LINE) == 6
    assert t.params == params_copy, "You shouldn't change inputs"
    assert t.json_schema == tasks.TASK_LINE[t.name].schema
    assert answer == t.result


# Flask API tests
def test_get_home(API_test: pytest.fixture) -> None:
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check that {"TASK_LINE": {...}} in response
    """
    response = API_test.get('/')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert "TASK_LINE" in data
    assert data['TASK_LINE'].keys() == tasks.TASK_LINE.keys()


@pytest.mark.parametrize('t', CASES, ids=str)
def test_run_api(t: Case, TASK_LINE: pytest.fixture, API_test: pytest.fixture) -> None:
    """
        Testing of function from cli_test.py
        ['charcount', 'manyarg', 'mult', 'multiprint']
        by API POST http-request
    """
    params_copy = copy.deepcopy(t.params)
    response = API_test.post('/'+t.name, json=t.params)
    answer = json.loads(response.data)

    assert len(tasks.TASK_LINE) == 6
    assert t.params == params_copy, "You shouldn't change inputs"
    assert answer == t.result


def test_for_wrong_func(TASK_LINE: pytest.fixture):
    wrong_name = 'blablabla'
    with pytest.raises(KeyError):
        tasks.TASK_LINE[wrong_name]


def test_for_wrong_func_api(TASK_LINE: pytest.fixture, API_test: pytest.fixture) -> None:
    wrong_name = 'blablabla'
    response = API_test.post('/'+wrong_name, json={})
    answer = json.loads(response.data)

    assert len(tasks.TASK_LINE) == 6
    assert answer == {"msg": "blablabla not registered in TASK_LINE",
                      "status": "KeyError"}
