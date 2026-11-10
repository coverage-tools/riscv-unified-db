# Coverage semantics overlay

Each file under `inst/<extension>/<instruction>.yaml` adds reviewed
`custom_semantics` to the corresponding standard UDB instruction. The files use
UDB's native overlay layout. Each patch retains its specification references.

`schema.json` validates the patches. The PR regression
`regress-coverage-overlay` checks the data and rejection cases through the
shared regression runner. The tracecow generator selects this directory through
`--overlay` or CMake's `RVCVD_UDB_OVERLAY`. Without an overlay, generation uses
upstream facts alone.

Roles describe explicit register dataflow during successful execution. Immediate
and modifier operands use `not_applicable`; `unused` marks ignored register
fields. Preserving masked-off, tail or prestart vector elements does not make a
destination an input. These fields do not list all implicit register or CSR
effects, conditional effects, memory widths or register groups.

Memory properties describe architectural data accesses, excluding address
translation. Categories distinguish loads, stores, atomics, prefetch hints and
cache maintenance. `environment_defined` and `csr_dependent` preserve effects
that require an execution environment or a selected CSR. Control flow excludes
incidental faults and trap delivery; `environment_call` and `csr_dependent`
identify explicit environment calls and CSR-dependent behavior. Missing fields
remain unknown.

References identify the sources used to review the facts; they do not enforce
per-instruction content checks. A missing instruction or operand,
or contradictory extracted fact fails consumer validation.
Operand kinds and roles default from UDB field names: `x`, `f` and `v`
register fields select the bank; source fields read, destination fields write,
and combined fields read and write. Non-register operands use `not_applicable`.
Memory and control-flow facts derived from instruction encodings are omitted.
The overlay records only exceptions to the derived facts. An operand entry may
provide `kind`, `role`, or both. For example, FLI overrides `xs1` to `immediate`;
its `not_applicable` role follows from the corrected kind.
An already-known matching fact produces a redundancy warning and can be removed.
Generated source metadata includes a digest of the selected overlay and schema.

The overlay, schema and tools are licensed under
[MIT](../../../../LICENSES/MIT.txt). File attribution is recorded in
[REUSE.toml](../../../../REUSE.toml).
