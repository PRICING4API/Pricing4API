# plan module

### *class* Pricing4API.plan.Plan(name: str, billing: Tuple[float, int, float | None] | None = None, rate: Tuple[int, int] | None = None, quote: List[Tuple[int, int]] | None = None, max_number_of_subscriptions: int = 1, \*\*kwargs)

Bases: `object`

A class used to represent a Plan.

* **Variables:**
  * **s_month** (*int*) – Static attribute representing the number of seconds in a month.
  * **\_\_limits** (*list*) – A private list to store limits.
  * **\_\_q** (*list*) – A private list to store q values.
  * **\_\_t** (*list*) – A private list to store t values.
  * **\_\_m** (*int*) – A private attribute to store the length of \_\_q.
  * **\_\_name** (*str*) – The name of the plan.
  * **\_\_price** (*float*) – The price of the plan. Only set if billing is not None.
  * **\_\_billing_unit** (*int*) – The billing unit of the plan. Only set if billing is not None.
  * **\_\_overage_cost** (*float*) – The overage cost of the plan. Only set if billing is not None.
  * **\_\_max_number_of_subscriptions** (*int*) – The maximum number of subscriptions for the plan.
  * **\_\_next_plan** ([*Plan*](#Pricing4API.plan.Plan)) – A reference to the next plan. Initially set to self.
  * **\_\_previous_plan** ([*Plan*](#Pricing4API.plan.Plan)) – A reference to the previous plan. Initially set to self.
  * **\_\_t_ast** – The result of the compute_t_ast method.

#### compute_t_ast()

This method is not defined in this snippet.

#### available_capacity(t: int | str, pos: int)

Calculates the accumulated capacity at time ‘t’ using the given limits.

This method calculates the available capacity at a given time ‘t’ for a specific limit position ‘pos’.
The time ‘t’ can be given as an integer (representing seconds) or as a string (which will be parsed using the parse_time_input method).
The ‘pos’ parameter represents the position of the limit in the \_\_limits list.

* **Parameters:**
  * **t** (*Union* *[**int* *,* *str* *]*) – The time at which to calculate the available capacity. Can be an integer (seconds) or a string (parsed using parse_time_input).
  * **pos** (*int*) – The position of the limit in the \_\_limits list.
* **Returns:**
  *int* – The available capacity at time ‘t’ for the limit at position ‘pos’.
* **Raises:**
  **IndexError** – If ‘pos’ is out of range of the \_\_limits list.

#### *property* billing_unit *: int*

Getter for the billing unit of the subscription plan.

#### compute_t_ast()

#### *property* cost_with_overage_quote

#### *property* downgrade_quote *: int*

#### *property* earliest_coolingdown_threshold

#### *property* limits *: list*

#### *property* max_number_of_subscriptions *: int*

Getter for the maximum number of subscriptions allowed in the subscription plan.

#### *property* max_unavailability_percentage

#### *property* max_unavailability_time

#### min_time(capacity_goal: int, i_initial=None)

Calculates the minimum time to reach a certain capacity goal using the given limits.

#### *property* name *: str*

Getter for the name of the subscription plan.

#### *property* next_plan *: [Plan](#Pricing4API.plan.Plan)*

Getter for the next subscription plan in the linked list.

#### *property* overage_cost *: float | None*

Getter for the overage cost of the subscription plan.

#### *property* overage_quote

#### parse_duration(duration_str)

#### parse_time_input(time_input)

#### *property* previous_plan *: [Plan](#Pricing4API.plan.Plan)*

Getter for the previous subscription plan in the linked list.

#### *property* price *: float*

Getter for the price of the subscription plan.

#### *property* quote_frequency *: list*

Getter for the quotes frequencies of the subscription plan.

#### *property* quote_value *: list*

Getter for the quotes values of the subscription plan.

#### *property* rate_frequency *: int*

Getter for the rate frequency of the subscription plan.

#### *property* rate_value *: int*

Getter for the rate value of the subscription plan.

#### s_month *= 2592000*

#### setNext(plan: [Plan](#Pricing4API.plan.Plan))

#### setPrevious(plan: [Plan](#Pricing4API.plan.Plan))

#### show_available_capacity_curve(time_interval: int, debug: bool = False)

#### show_capacity_areas(time_interval: int)

Shows the accumulated capacity curve and the wasted capacity threshold curve.

#### show_capacity_areas_old(list_t_c: List[Tuple[int | str, int]])

Shows the accumulated capacity curve and the wasted capacity threshold curve.

#### *property* unit_base_cost *: float*

#### *property* upgrade_quote *: int*

### *class* Pricing4API.plan.QuoteFunction(quote_value: int, quote_unit: int)

Bases: `object`

### *class* Pricing4API.plan.RateFunction(rate_value: int, rate_unit: int)

Bases: `object`
