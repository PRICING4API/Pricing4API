import logging
import time

import pandas as pd
import requests
from Pricing4API.ancillary.limit import Limit
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.main.new_plan import Plan


class Subscription:
    
    def __init__(self, plan: Plan, url: str):
        self.__plan = plan
        self.__url = url
        self.__regulated = True
        self.__subscription_time = time.time()
        self.__accumulated_requests = 0
        self.__requests_log = []
        self.__429_requests = []
        
        
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', 
                            handlers=[
                                logging.FileHandler('api_requests.log'),
                                logging.StreamHandler()
                            ])
        
        logging.info(f"Subscription to {url} started at {self.__subscription_time}")
    
    
        
    @property
    def plan(self) -> Plan:
        return self.__plan
    
    @property
    def url(self) -> str:
        return self.__url
    
    @property
    def regulated(self) -> bool:
        return self.__regulated
    
    @property
    def subscription_time(self) -> float:
        return self.__subscription_time
    
    @property
    def accumulated_requests(self) -> int:
        return self.__accumulated_requests
    
    @property
    def requests_log(self) -> list:
        return self.__requests_log
    
    @property
    def requests_429(self) -> list:
        return self.__429_requests
        
        
    def regulated(self, regulated: bool) ->bool:
        '''Check if the subscription is regulated by the plan.'''
        self.__regulated = regulated
        
        
    def available_request(self, t) -> bool:
        pos = len(self.__plan.limits) - 1
        
        t_milliseconds = int(t) * 1000
        time_duration = TimeDuration(t_milliseconds, TimeUnit.MILLISECOND)
        
        available_capacity = self.__plan.available_capacity(time_duration, pos)
        if available_capacity < self.__accumulated_requests:
            return False
        else:
            return True
        
        
    def make_request(self, method='GET', custom_rate = None, **kwargs):
        '''
        Make a request to the API. If the subscription is regulated, it will wait until the next request is available.
        '''
        
        plan_rate = self.__plan.rate_frequency if custom_rate is None else custom_rate
        if self.__regulated:
            if self.available_request(time.time() - self.__subscription_time):
                if self.__accumulated_requests > 0:
                    logging.info(f"Waiting {plan_rate}")
                    time.sleep(plan_rate.to_seconds())
            else:
                logging.info(f"Waiting {plan_rate}")
                time.sleep(plan_rate.to_seconds())
                logging.info(f"Request ({self.__accumulated_requests}) to {self.__url} may be exceeding the rate limit.")
        
        response = requests.request(method, self.__url, **kwargs)
        if response.status_code == 429:
            logging.info(f"Request ({self.__accumulated_requests + 1}) to {self.__url} exceeded the rate limit.")
            if 'Retry-After' in response.headers:
                logging.info(f"The Retry-After header is: {response.headers['Retry-After']} seconds")
            else:
                logging.info(f"The Retry-After header is not present.")
        elif response.status_code == 200:
            logging.info(f"Valid request ({self.__accumulated_requests + 1}) to {self.__url}")
        else:
            logging.info(f"Request ({self.__accumulated_requests + 1}) to {self.__url} failed with status code: {response.status_code}")
        self.__accumulated_requests += 1
        return response

    def api_usage_simulator(self, time_simulation: TimeDuration):
        """
        Simulate API usage for a given time duration. If the quota is exceeded,
        wait until the quota resets and continue.
        """
        self.__accumulated_requests = 0
        end_time = time.time() + time_simulation.to_seconds()
        responses = []

        while time.time() < end_time:
            elapsed_time = time.time() - self.__subscription_time

            if self.__accumulated_requests >= self.plan.quotes_values[-1]:
                wait_time = self.plan.quotes_frequencies[-1].to_seconds() - elapsed_time
                if wait_time > 0:
                    logging.info(f"Quota exceeded. Waiting {wait_time} seconds for quota reset...")
                    time.sleep(wait_time)
                     
                self.__accumulated_requests = 0
                self.__subscription_time = time.time()
            response = self.make_request()
            responses.append((response.status_code, response.elapsed.total_seconds()))
            
            if response.status_code == 429:
                self.__429_requests.append((len(responses), response.headers['Retry-After']))

        df = pd.DataFrame(responses, columns=['Status Code', 'Response Time'])
        return df
    

if __name__ == "__main__":
    plan_dblp = Plan('DBLP', (0.0, TimeDuration(1, TimeUnit.MONTH)), overage_cost=None, 
                     unitary_rate=Limit(1, TimeDuration(2, TimeUnit.SECOND)), quotes=[Limit(20, TimeDuration(1, TimeUnit.MINUTE))])
    
    dblp_subscription = Subscription(plan_dblp, 'https://dblp.org/search/publ/api')
    
    dblp_subscription.regulated(False)
    
    plan_dblp.show_available_capacity_curve(TimeDuration(2, TimeUnit.MINUTE))









