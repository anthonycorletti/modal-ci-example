import json
from concurrent.futures import ThreadPoolExecutor

from watchfiles import watch

from hudson.config import config


def go() -> None:
    for changes in watch(config.client_watch_dir):
        print(changes)


pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="hudson-client-watcher")
running = True

print("writing data")
with pool as executor:
    while running:
        for i in range(2):
            # write some data to the watch dir
            with open(f"{config.client_watch_dir}/data.jsonl", "w") as f:
                f.write(json.dumps({"text": "hello world"}))


print("stopping watch")
pool.shutdown(wait=False)
