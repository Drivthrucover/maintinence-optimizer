# Basic analysis from a CSV
reliability-cli analyze \
  --input data/component_a.csv \
  --time-col hours \
  --failure-col failures \
  --model weibull \
  --theta 4000 \
  --beta 2.2 \
  --criticality medium \
  --tmax 5000 \
  --out ./results/



The user opens the terminal and runs something like:

reliability-cli analyze --input components.csv --tmax 10000 --out results/
