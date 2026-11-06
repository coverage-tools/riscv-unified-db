# Instruction operand facts

`operand-effects.json` adds coverage-specific operand and memory access facts to
upstream instructions. Instructions with identical facts share one group. Paths
in each `instructions` list are relative to `spec/std/isa/inst/`. Consumers
join the facts to upstream instructions by path.
