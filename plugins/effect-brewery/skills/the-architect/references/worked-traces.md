# Worked Traces

The principles in this skill conflict routinely. That is by design — the Principle of Dependencies is the tiebreaker. These traces show what applying it actually looks like, including the cases where it says _do nothing_.

## Trace 1: A Conditional That Selects Behavior

**Situation.** A module dispatches notifications. One conditional selects email, SMS, or push.

**First read — the principles disagree.**

- _Isolate Things That Vary_ says the branching selects behavior and will gain new cases. Replace it with polymorphism behind a factory.
- _Cost of Abstraction_ says a factory plus three implementations is indirection for something one conditional already handles.

**Neither wins yet.** Counting variants does not settle this. A single centralized conditional already keeps the choice in one place, which is most of what a factory would buy you. "A fourth variant is coming" is not evidence — it is a headcount.

**Tiebreaker — Principle of Dependencies.** Ask whether the knowledge has spread:

- Is the same discriminator re-interpreted elsewhere — retry policy, formatting, or rate limits each switching on channel again?
- Do the branches change on independent schedules, for independent reasons?
- Do implementations need independent lifecycle or independent testing?
- Are variants supplied from outside this module?
- Has the branch stopped being locally understandable?

**If none of these hold:** the dependency is already explicit and local. Leave the conditional alone — even with a fourth channel coming. Adding an interface here would _increase_ the number of things that depend on each other, not reduce them.

**If the discriminator is re-read in three places:** the knowledge is now implicit and duplicated. Every new channel forces correlated edits across modules that have no business knowing about channels, and forgetting one is a silent bug. Isolate it: the factory gives that knowledge one owner and one place to change.

**The lesson.** The evidence decides, not the variant count. The same code warrants opposite decisions depending on whether the knowledge has leaked.

## Trace 2: A Vendor Type in a Function Signature

**Situation.** A use case returns the payment provider's SDK charge object. It compiles, tests pass, and the provider is not going to be replaced this year.

**First read — the principles disagree.**

- _Own the Contract at the Boundary_ says the SDK type is vendor-owned and should not be the application contract.
- _Cost of Abstraction_ says translating into a local result type is a mapping layer protecting against a swap nobody plans to make.

**Tiebreaker — Principle of Dependencies, via the two tests.**

_Ownership:_ the type's shape is decided by the vendor's release notes, not by what the use case means. It fails the ownership test regardless of swap probability. This is the point people miss — "we're never replacing them" answers the wrong question.

_Economics:_ probability of change is not replacement probability. It is the probability the _shape_ changes: SDK major versions, deprecated fields, a renamed status enum. Blast radius is every layer that pattern-matches on it — here, the use case and every caller above it.

**Decision.** Translate at the adapter. Not to prepare for a migration, but because a vendor's release schedule is now an input to code that has nothing to do with the vendor.

**Now change one fact.** The type appears in exactly one adapter-internal function, never crossing outward. Ownership is fine — the vendor's shape is living in the vendor's adapter, which is where it belongs. No translation needed. The rule was never "wrap every vendor type"; it was "don't let vendor shapes become application contracts."
