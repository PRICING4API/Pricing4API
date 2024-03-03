# pricing module

### *class* Pricing4API.pricing.Pricing(name: str, plans: list, billing_object: str)

Bases: `object`

#### add_plan(plan: [Plan](plan.md#Pricing4API.plan.Plan))

Add a plan to the list of plans.

#### *property* billing_object *: str*

Getter for the billing object.

#### create_table()

#### link_plans()

Link plans together in a linked list fashion. If there is more than one plan, each plan is linked to the next and previous plans. If there is only one plan, it is linked to itself.

#### *property* name *: str*

Getter for the name of the pricing object.

#### *property* plans *: list*

Getter for the list of plans.

#### show_datasheet()

#### show_more_table(df: DataFrame)
