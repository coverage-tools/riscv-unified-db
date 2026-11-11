# Coverage semantics overlay

This overlay marks instructions that reference memory or transfer control.
Each `inst/<extension>/<instruction>.yaml` file adds `custom_semantics` through
UDB's native overlay layout. The overlay path identifies the corresponding
UDB instruction.

## Instruction markers

| Property | Values emitted |
| --- | --- |
| `memory_access` | `load`, `store`, `atomic`, `prefetch`, `cache_management` |
| `control_flow` | `branch`, `jump`, `indirect_jump`, `trap_return`, `environment_call`, `breakpoint` |

Add only the applicable properties. A load needs no control-flow field; a branch
needs no memory field. An ordinary arithmetic instruction needs neither.
Missing markers produce no placeholder, warning, or report. The schema permits
only the positive marker values listed above.

Memory references include loads, stores, LR/SC, atomic read-modify-write
operations, prefetch hints, cache management, and explicit jump-table reads.
Acquire loads and release stores use `load` and `store`. Ordinary instruction
fetch and implicit address-translation accesses are outside this classification.
For example, `cm.popret` and `cm.jt` carry both `memory_access: load` and
`control_flow: indirect_jump`.

`environment_call` marks ECALL; `breakpoint` marks explicit breakpoint/debug
transfers. Incidental exceptions and interrupts do not make an instruction a
control-flow instruction. Potential effects of an environment handler or a
selected CSR are outside the markers' scope.

## Licensing

The overlay, schema and tools are licensed under
[MIT](../../../../LICENSES/MIT.txt). File attribution is recorded in
[REUSE.toml](../../../../REUSE.toml).
