---
name: the-architect
description: Use when deciding what belongs where — module boundaries, what to expose or hide in a public API, where a contract should live, whether an abstraction earns its keep, or when transport, vendor, or framework shapes are leaking into core logic.
---

# The Architect

A thinking framework for making design decisions in code. The goal is always: **maximize good design with the least amount of code**.

These principles are language-agnostic at their core, but how heavily you apply them depends on the language, codebase, and problem at hand. A 50-line script doesn't need the same design machinery as a large system. Use judgment.

## Principle of Dependencies

Never rely on assumed or implicit behavior. Dependency means trouble, unless you are extra clear about it. Bringing in knowledge into a system, from another system, means dependency. Bringing in assumed, implicit or unclear knowledge into a system, from another system, means disaster.

This is the first-pass filter for every design decision. All other principles in this skill — the Knowledge Plot, Messaging over Behavior, Isolate Things That Vary, Cost of Abstraction — are tools for applying this principle in specific situations. When principles conflict, the Principle of Dependencies is the tiebreaker: prefer the option that creates fewer or more explicit dependencies.

## Own the Contract at the Boundary

When data crosses a boundary, ask: **whose language is this shape speaking?** The contract belongs to the side whose purpose it serves.

If a shape exists because of transport, framework, vendor, or persistence mechanics, it belongs to an **adapter**. If it exists because of a use case, an application workflow, or a business concept, it belongs to the **application/core**. See [Ports & Adapters](references/ports-and-adapters.md) for the specific shapes on each side.

This is a general dependency rule, not just a Ports & Adapters one. When a transport or vendor payload becomes the application contract, you have imported someone else's axis of change into the core. The layering may still look clean, but the knowledge is leaking inward, and that leak creates shotgun surgery. The smell test: if changing a transport payload forces a port or use case signature to change, the contract is owned by the wrong layer.

Do not cargo-cult extra mapping types everywhere. Add translation where the reason to change is different. When the boundary owns different knowledge, it should own a different contract.

### Errors Are Contracts Too

Failures cross boundaries like everything else, and the same question applies. Status codes, exception classes, driver error codes, and vendor error payloads are adapter-owned. The core expresses failure in its own language — what went wrong in application terms — and adapters translate that outward.

Two failures a caller must handle differently should be distinguishable without parsing a string or matching on a vendor type. Two failures a caller handles identically do not need separate cases.

### How Hard to Insulate

Two independent tests decide this, and they are easy to conflate:

1. **Ownership** — does this shape express application intent, or external implementation detail? This decides _whether_ the contract sits in the right place.
2. **Economics** — does **probability of change × blast radius** exceed the cost of insulation? This decides _how much_ machinery the boundary deserves.

Ownership can fail even when replacement is unthinkable. Deliberately committing to a framework lowers the value of insulating against _wholesale replacement_; it does not make every framework type application language. Version churn, testability, and blast radius are reasons to translate even a dependency you will never swap. The converse holds too: a wrapper protecting only against a hypothetical replacement — no ownership problem, no blast radius to contain — is indirection you are paying for and not using.

## The Knowledge Plot

The primary decision framework. First a gate — does this belong here at all? — then a plot on two axes.

### The Gate: Purpose — Should this even be here?

| Region                 | Meaning                                                                |
| ---------------------- | ---------------------------------------------------------------------- |
| **Within My Purpose**  | This behavior belongs in this module/component/service                 |
| **Outside My Purpose** | This behavior doesn't belong here — it's someone else's responsibility |

If it's outside your purpose, remove it or delegate it. Don't keep it around "just in case." Everything below assumes you passed the gate.

### The Plot: Stability × Visibility

**Stability** — how likely is this to change? Unstable means volatile, experimental, still being learned. Stable means settled and well-understood.

**Visibility** — how much can consumers see? Visibility is partly a choice, not merely an observation: ask both what it _is_ today and what it _needs to be_.

|              | **Public / visible**                                                                        | **Internal / hidden**             |
| ------------ | ------------------------------------------------------------------------------------------- | --------------------------------- |
| **Stable**   | **Expose** — this is your contract                                                          | **Minimize** — keep it small      |
| **Unstable** | **Declare the guarantee** if exposure is genuinely required; otherwise **Hide** or **Move** | **Hide** — correct; keep it there |

> **Default bias:** When in doubt, treat things as unstable and hide them. Engineers routinely overestimate stability. The cost of hiding something stable is low (you can expose it later); the cost of exposing something volatile is high (consumers now depend on it).

**Remove / delegate** is the gate's outcome, not a cell on the plot.

### The Decision Sequence

When looking at any piece of code, ask in order:

1. **Should this even be here?** → If no, remove it or delegate it. (Gate)
2. **Stable and part of my contract?** → **Expose** it. This is what consumers may depend on.
3. **Stable but internal?** → **Minimize** it. Keep it small and focused; reduce surface area.
4. **Unstable and visible?** → **Hide** it behind this module's interface.
5. **Must it stay visible despite being unstable?** → **Declare the guarantee**: settle the contract, version it, or mark it explicitly experimental. Any of the three is fine; leaving consumers to guess is not.
6. **Can't hide it here, because it changes for a different reason than everything around it?** → **Move** it behind its own boundary, where it can change freely.

## Messaging over Behavior

Prefer sending a message to another object over implementing the behavior yourself. The two fundamental building blocks of design are **messages** and **dependencies**.

- No dependency means no external cause of change
- Knowledge of another object's internals should be avoided
- When you find yourself implementing behavior that requires knowing how another component works, send a message instead and let the other component handle it

This keeps coupling low and makes each piece of code responsible only for its own decisions. "Tell, Don't Ask" and "Law of Demeter" are two examples of this design framework.

## Isolate Things That Vary

When conditionals choose behavior (not validate data or guard logic), they tend to break the Open/Closed Principle — you have to modify existing code every time a new variant appears.

The remedy:

- **Use polymorphism instead of conditionals** for behavior selection
- **Place behavior-choosing conditionals inside factories** when conditionals are needed
- Factories should be **isolated** (one place), **shared** (reused), **simple** (easy to read), and **ignorable** (the rest of the code doesn't care how the choice was made)

This is the Strategy Pattern and other forms of dependency injection. Isolate the decision about _which_ behavior to use from the behavior itself.

However — sometimes a simple `if/else` is clearer than a class hierarchy. Apply this principle when branching is growing, repeated, or likely to gain new cases. Don't apply it to a stable one-off check.

## Cost of Abstraction

Every abstraction has a price. Before introducing one, it must justify itself:

- **What change does it protect against?** If you can't name a concrete, likely change — you're speculating.
- **What duplication does it remove?** If none, the abstraction is adding indirection without reducing work.
- **What complexity does it add?** Layers, interfaces, and indirection all have a cognitive tax.

**Data shape or behavior?** Use a named data contract when you need to fix a shape and its meaning at a boundary — that is cheap and usually worth it. Introduce an interface only when behavior genuinely varies across implementations. Conflating the two produces interfaces with a single implementation: indirection wearing an abstraction's clothes.

If an abstraction is no longer buying you anything — inline it. Systems rot not just from missing abstractions, but from _stale_ ones that no longer match reality. Collapsing unnecessary layers is as important as creating useful ones.

## Clear Code

Clear code is always better than clever code. If a complication exists, you should be able to justify the advantage it provides. Otherwise, simplify.

Sometimes simplification means breaking into smaller parts. Sometimes it means _fewer_ parts — a longer but straightforward function can be better than a deep hierarchy of abstractions. The test is: can someone unfamiliar with this code understand what it does and why, without heroic effort?

Optimization is a specific type of stability decision. Don't optimize unstable code — it sacrifices clarity for performance in code that's likely to be rewritten anyway.

## Adapting to Language and Context

These principles apply universally, but their expression varies by language:

The vocabulary translates. In class-based languages the Knowledge Plot maps onto class design and SOLID applies almost literally. In functional languages, "messaging" becomes function composition and passing functions as arguments, "hide" becomes module boundaries and opaque types, polymorphism comes from protocols or pattern matching, and factories become configuration functions. In dynamic languages the principles hold, but be extra careful about "Expose" — they make it easy to depend on internals by accident.

**Small scripts and prototypes**: Apply these principles lightly. A 100-line script doesn't need dependency injection. But once code grows to the point where you're confused about what does what, reach for these principles.

**General rule**: The larger and longer-lived the codebase, the more rigorously to apply these. For throwaway code, _Clear Code_ is the only one that always matters.

## Applying This Skill

When helping with design decisions:

1. **Principle of Dependencies**: Always check for hidden dependencies. If you find one, ask: "Is this dependency explicit and intentional? If not, how can we make it so?"
2. **Check contract ownership.** Ask: "Whose language is this shape speaking?" See _Own the Contract at the Boundary_.
3. **Run the Knowledge Plot.** Walk the decision sequence. This usually resolves what belongs where and what to expose or hide.
4. **Check messaging.** Is the code reaching into another component's internals? Suggest message-passing instead.
5. **Look for varying behavior.** If conditionals select behavior, weigh isolating them — against the evidence, not the variant count.
6. **Ensure clarity.** Is this the simplest design that achieves the goal? If not, simplify.

### Patterns & Principles

1. **Ports & Adapters**: Reach for this pattern when external churn, multiple entry points, or independently changing infrastructure justify a core-owned contract. Ports belong to the core and speak its language; adapters own transport, framework, vendor, and persistence detail. All dependencies point inward, and adapters must not depend on each other. See [Ports & Adapters](references/ports-and-adapters.md) for contract layers and smell checks.
2. **Reference SOLID as supporting arguments** when they clarify _why_ a particular design choice is better. SOLID principles often explain why a Knowledge Plot decision is correct: SRP aligns with "Should this even be here?", OCP motivates "Isolate Things That Vary", DIP underpins Ports & Adapters. Cite them as evidence, not as the primary decision framework.

Always explain the reasoning behind design recommendations. "Move this to a separate module" is less useful than "This payment calculation is outside the purpose of your User class, and it's unstable — business rules change quarterly — so it should live behind its own boundary where it can change independently."

> **Structural review does not replace correctness review.** These questions surface where knowledge belongs; they will not surface an off-by-one, a swallowed error, or a missing case. Run both passes.

## Out of Scope

This skill is about code structure: what belongs where, what is visible, and what contracts exist between the parts. Runtime topology — what runs as a separate process or service, how work is distributed, what fails independently — is a real set of decisions but not this framework's subject.

## References

- [Ports & Adapters - Architecture Guidelines](references/ports-and-adapters.md)
- [Worked Traces](references/worked-traces.md) — how the principles conflict, and how the tiebreaker resolves them
