# CAP-004 — Loop Optimization

Detects the safe identity-append loop pattern and can rewrite it to a list comprehension when `parameters['apply']` is true.

## Safety

Only a single-statement loop of the form `out.append(item)` where `item` is the loop variable is rewritten. Other loops remain findings-only.