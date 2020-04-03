from concurrent.futures import ThreadPoolExecutor
import requests


def multithreading(func, args):
    # pool = multiprocessing.Semaphore(multiprocessing.cpu_count())
    with ThreadPoolExecutor() as executor:
        result = executor.map(func, args)
    return list(result)


def post_api(url, json_data):
    try:
        resp = requests.post(url, json=json_data)
        return resp.text[:-1]
    except Exception as e:
        print ('ERROR: %s' % e)
        return None


def get_api(url):
    try:
        resp = requests.get(url)
        return resp.text[:-1]
    except Exception as e:
        print ('ERROR: %s' % e)
        return None


def main():
    HOST = 'http://127.0.0.1:5000/api'
    json_data = {'method': 'start', 'task_name': 'mult', 'params':{'operands': [3, 2, 8]}}
    # json_data = {"method": "start", "task_name": "delay", "params": {}}
    args = ((HOST, json_data) for _ in range(100))
    r = multithreading(lambda p: post_api(*p), args)
    print(r)


if __name__ == "__main__":
    main()
