# Human Understanding — Issue #15

The prior direct candidate failed before copper was created. The lesson is to compare several ordinary candidates under one geometry model instead of repeatedly guessing.

The screen measures the clearance from each proposed 0.30 mm segment to every different-net or unnetted F.Cu pad, track and via. Same-net copper is allowed as connectivity context.

A passing screen is only a preflight result. KiCad DRC remains authoritative because keepouts, zones and full rule evaluation are richer than this geometric model.

The selected route must still reduce exactly one ratsnest edge and preserve the 268-node physical pin/net audit.
