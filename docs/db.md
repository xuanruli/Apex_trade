## database initialize
1. the delay in process_all_stocks is set up to 0.1 second, if in your end some print message said "store xxx failed, it means you need to increase delay, after test 0.3 second is a general safe delay time to guarantee all successful store"
2. nasdaq-100 stock list is in fetch_nasdaq_100() function
3. alpha vantage key is in env
4. pip install necessary package from import section
5. there are hourly, monthly, and daily data now
6. use adjusted close price when making chart
7. structure of db in shcema.py

## db package usage
1. for action involved with database change (portfolio added, user added), please see __init__.py for helper function