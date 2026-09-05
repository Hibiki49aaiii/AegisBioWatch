# Issue #22 — Human Understanding

We are not "routing the next nearest airwire." We are advancing a validated PCB baseline by one isolated, auditable increment.

The current electrical authority is route-1bo, proven by executed KiCad 9.0.9 DRC and the 268-node pin/net audit at **0 violations / 109 unconnected / PASS**. The next task is to inspect what is actually still disconnected after that accepted change.

Phase A must therefore be read-only. It can reproduce route-1bo, inspect the real 109-item ratsnest, and calculate possible ordinary F.Cu paths, but it must not create copper.

The coarse geometry engine is only a screening tool. A numerical pass can still be unacceptable because it touches RF/high-density/supplier-gated scope, a deferred power/switch net, or an ambiguous mechanical element. Semantic review remains mandatory.

If one safe family survives, refine only that family at 0.05 mm and prove exact source/target identity before Phase B. If none survives, record that result and keep route-1bo as authority.

No manufacturing release is implied. The board remains **NOT_FOR_GERBER**.
