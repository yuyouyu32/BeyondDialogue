import time

MaxRetries = 5
Delay = 10

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    print(f"Attempt {retries}/{max_retries} failed: {e}")
                    time.sleep(delay)
            raise Exception(f"Failed after {max_retries} attempts")
        return wrapper
    return decorator