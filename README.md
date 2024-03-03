# Pricing4API
A module to deal with pricing plans of RESTful APIs 


## Module use cases

- *Rate Limiter*

    ```
    PlanDBLP = Plan('DBLP', (9.99, 1, None), (1, 2), [(20, 60)])
    DBLPSubscription = Subscription(PlanDBLP,  'https://dblp.org/search/publ/api')

    end = time.time() + 36
    logging.info(f"Consuming in a regulated manner, there should be no 429 errors until {end}.")

    response = DBLPSubscription.make_request()
    while(time.time() < end and response.status_code != 429):
        response = DBLPSubscription.make_request()

    DBLPSubscription.regulated(False)
    end = time.time() + 10
    logging.info("Consuming in an unregulated manner, 429 errors should appear in approximately 10 seconds.")

    while(time.time() < end and response.status_code != 429):
        response = DBLPSubscription.make_request()
    if response.status_code == 429:
        if 'Retry-After' in response.headers:
            logging.info(f"Actively waiting until {time.time() + int(response.headers['Retry-After'])}")
            time.sleep(int(response.headers['Retry-After']))
        else:
            logging.info(f"Actively waiting 5 minutes, that is, until {time.time() + 5*60}.")
            time.sleep(5*60)

    logging.info(f"Consuming again in a regulated manner, there should be no 429 errors.")
    DBLPSubscription.regulated(True)
    end = time.time() + 2 * PlanDBLP.quote_frequency[-1]
    while(time.time() < end):
        DBLPSubscription.make_request()
    ```
