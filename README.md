# Pricing4API
A module to deal with pricing plans of RESTful APIs 


## Module use cases

- *Rate Limiter*

    ```
    PlanDBLP = Plan('Pro', (9.99, 1, None), (2,1), [(20,60)])

    DBLPSubscription = Subscription(PlanDBLP, 'https://dblp.org/search/publ/api?q=deep+learning&format=json')

    for _ in range(n):  # Try n requests
        response= DBLPSubscription.make_request()
    data = response.json() # Interpret JSON response

    DBLPSubscription.close() #Commit changes and close the connection
    ```
