This project is a Reliability-Based Maintenance Interval Optimizer that helps engineers decide when to inspect, maintain, or 
replace a system before it becomes too likely to fail. The core idea is to take simple failure data like how many times something failed 
and how long it has been running and turn that into a prediction of how the system behaves over time. Instead of reacting after a failure occurs, the
 tool uses reliability models to estimate the probability that a system will continue working, and then determines when that probability becomes too low to be acceptable.

The process starts by computing basic reliability metrics. The failure rate is calculated as

\lambda = \frac{\text{number of failures}}{\text{operating time}}


which tells us how quickly failures occur. From this, we can compute the mean time to failure (MTTF) or mean time between failures (MTBF) using

\text{MTTF or MTBF} = \frac{\text{operating time}}{\text{number of failures}}


These values give a baseline understanding of how long a system typically lasts, but they do not tell us how failure risk evolves over time.

To model how reliability changes, the project uses two main reliability functions. The first is the exponential reliability model,

\text{MTTF or MTBF} = \frac{\text{operating time}}{\text{number of failures}}

which assumes a constant failure rate. The second is the Weibull reliability model,

R(t) = e^{-\lambda t}

which is more flexible and captures different failure behaviors depending on the value of β. When β<1, failures are more likely early on (infant mortality); when β=1, failures occur randomly at a constant rate; and when β>1, failures increase over time due to wear-out. These models allow the system to estimate the probability that a component will survive up to any given time.

Finally, the optimizer determines maintenance intervals by defining reliability thresholds and finding when the system crosses them.
 For example, an engineer might require that at least 85% of systems survive to a given time. The tool finds the first time t such that

R(t)<threshold

and recommends maintenance at that point. Different thresholds can be used for inspection, servicing, and replacement depending on how critical the component is.
 This turns abstract reliability math into concrete, actionable decisions, making it easy to plan maintenance schedules and reduce unexpected failures.


Plot generation
What the user sees

The tool saves plots to the output folder, such as:

reliability curves
threshold lines
marked action times
What the tool does

It visualizes the results.

What is happening internally

The plotting system creates graphs such as:

Plot 1: reliability vs time
x-axis = time
y-axis = reliability
line 1 = exponential reliability
line 2 = Weibull reliability
Plot 2: threshold lines

Horizontal lines at:

0.95
0.85
0.70
Plot 3: crossing markers

Dots or vertical lines where:

inspect happens
maintain happens
replace happens




What the user sees

The output directory may contain files like:

metrics.csv
recommendations.csv
relay_A_plot.png
sensor_B_plot.png
summary.json
What the tool does

It saves the analysis in reusable forms.




Feature 11: Compare mode
What the user sees

They run a command like:

reliability-cli compare --input components.csv --tmax 10000 --out results/

and get an overlay plot plus ranking outputs.

What the tool does

It compares multiple components side by side.

What is happening internally

The tool repeats the analysis for each component, then overlays the reliability curves on one chart.



The tool takes reliability data from a CSV, computes metrics like failure rate and MTBF, models survival over time using exponential and Weibull equations, applies criticality-based reliability thresholds, and then finds the exact times where maintenance actions should occur. It also generates plots and summary files so the results are easy to interpret and share.
