# sentinelone_data_lake_search

Use this python script to search for events in SentinelOne Data Lake.


# Installation

1. Clone this git repo locally

```
git clone https://github.com/mdmdfrontify/sentinelone_data_lake_search.git
cd sentinelone_data_lake_search
```


# Configuration

1. Modify the `config.ini` file:

- `API_TOKEN` - Your API token generated from the User menu "My profile".
- `BASE_URL` - Link to your SentinelOne console. It must look like `https://xxx-yyy.sentinelone.net/sdl/v2/api`
- `POLL_INTERVAL` - seconds between checking if data is available. S1 suggests 1-2 seconds
- `MAX_POLL_ATTEMPTS` - how many times the script checks if data is available, to avoid infinite loop

2. Modify the `sentinelone_data_lake_search.py` file:

- `s1_search_query` Your SDL search string
- `s1_search_since` Search time range (since). Format: `3d` - three days, `12h` - twelve hours etc
- `s1_result_count_limit` Limit on returned results. S1 limit is 1000 results

Optionally you can disable messages by changing `logging.basicConfig(level=logging.INFO)` to `logging.basicConfig(level=logging.ERROR)`. 

# Run

```
./sentinelone_data_lake_search.py
```
