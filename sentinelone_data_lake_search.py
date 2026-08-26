#!/usr/bin/python3

__version__ = "1.0.0"

import json
import time
import requests
import logging
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


# === Connection configuration
API_TOKEN = config["main"]["API_TOKEN"]
BASE_URL = config["main"]["BASE_URL"]
POLL_INTERVAL = 5  # Seconds between status checks
MAX_POLL_ATTEMPTS = 20  # Safety timeout limit (60 seconds max)

# === search query configuration
# SDL search string
s1_search_query = "event.id='12511DD3-774E-496C-B7AD-32F0783AE7CB_999'"
# SDL search time range; 1d is one day, 1h is one hour
s1_search_since = "3h"
# SDL maximum limit on count of results
s1_result_count_limit = 10

# for debugging set level=logging.DEBUG
logging.basicConfig(level=logging.INFO)


logging.debug('SentinelOne SDL script started.')

## Stage 1 - send search query to sentinelone SDL

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

payload = {
    "queryType": "LOG",
    "queryPriority": "LOW",
    "startTime": s1_search_since,
    "log": {
        "filter": s1_search_query,
        "limit": s1_result_count_limit
    },
}
logging.info('Stage 1 - Sending search query "%s" to %s', s1_search_query,BASE_URL)

try:
    response = requests.post(f"{BASE_URL}/queries", json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    response_json = response.json()

    # get query id
    query_id = response_json.get("id") or response_json.get("data", {}).get("id")
    # get forward tag
    forward_tag = response.headers.get("x-dataset-query-forward-tag", "")

    logging.info('Stage 1 - Sending search query - success. query_id: %s, time range: %s', query_id,s1_search_since)

except:
    logging.error('Stage 1 failed: %s, %s', response.status_code, response.text)
    raise

## Stage 2 - fetch search results

logging.debug('forward tag %s', forward_tag)


poll_headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}",
    "X-Dataset-Query-Forward-Tag": forward_tag
}

attempts = 0
stage2_start = time.time()

while attempts < MAX_POLL_ATTEMPTS:

    get_response = requests.get(f"{BASE_URL}/queries/{query_id}", headers=poll_headers, timeout=30)
    get_response.raise_for_status()
    res_data = get_response.json()

    steps_completed = res_data.get("stepsCompleted", 0)
    steps_total = res_data.get("stepsTotal", 1)

    logging.info('Stage 2 - Pulling data. attempt: %d/%s, step: %d/%d, http code: %s',attempts,MAX_POLL_ATTEMPTS,steps_completed,steps_total,get_response.status_code)

    if steps_completed >= steps_total and steps_total > 0:
        stage2_end = time.time()
        stage2_runtime = round((stage2_end - stage2_start),0)

        s1_dl_outcome_body = (
            res_data if isinstance(res_data, dict) else {"data": res_data}
        )
        s1_dl_outcome_count_results = s1_dl_outcome_body["data"]["estimatedMatchCount"]
        s1_dl_outcome_body = s1_dl_outcome_body["data"]["matches"]

        logging.info('Stage 2 - Pulling data - success. Results: %d, runtime: %d seconds', s1_dl_outcome_count_results, stage2_runtime)

        print(s1_dl_outcome_body)

        break

    attempts += 1

    if attempts == MAX_POLL_ATTEMPTS:
        logging.error('Stage 2 - Pulling data - fail. Not enough time. Increase MAX_POLL_ATTEMPTS and POLL_INTERVAL, or decrease s1_search_since.')
        break

    time.sleep(POLL_INTERVAL)
