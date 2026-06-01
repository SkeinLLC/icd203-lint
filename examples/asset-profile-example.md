# Example: linting an analytic report

Save this file as `report.md` and run:

```
icd203-lint report.md
```

The linter will surface anything that violates the five default rules. To
see only errors, raise the severity floor:

```
icd203-lint report.md --severity error
```

To suppress a rule on one line, attach an inline directive:

```
We assess that operators are based in Brazil. <!-- icd203-lint: ignore=assessment-no-confidence -->
```

To disable rules across the whole file, put a directive at the top:

```
<!-- icd203-lint: disable-file=quote-unattributed -->
```
