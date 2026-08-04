# Ports & Adapters - Architecture Guidelines

Follow the Ports & Adapters (Hexagonal) pattern when you need the Core insulated from transport, framework, persistence, and vendor churn.

## First Principle: Ports speak the Core's language

A Port is a contract owned by the Core. It should express the application's intent.

It should carry only the minimum data the Core needs to do useful work.

A Port is **not**:

- an HTTP request or response shape
- a queue envelope
- a gRPC or GraphQL schema
- a framework request/response object
- a vendor SDK type
- a database row or ORM model

If a contract exists because of transport, framework, or vendor concerns, that contract belongs to an Adapter, not to a Port.

## Contract Layers

Keep the contracts separate by ownership and reason to change:

- **Transport contracts** live in Adapters. They include HTTP payloads, headers, status codes, query parameters, message envelopes, serialization rules, vendor payloads, and persistence schemas.
- **Application contracts** live at the Port boundary. They are commands, queries, results, and errors expressed in application language.
- **Domain concepts** live in the Core. They are entities, aggregates, value objects, and business rules.

Translation between these layers is intentional. It prevents hidden knowledge from leaking inward and turning every transport change into a Core change.

**Core Structure**

The Core contains:

- Entities, Aggregates, Value Objects
- Domain Services (business logic)
- Application Services (use case orchestration)
- Application-facing request/response models when needed
- Repository interfaces (as Driven Ports)
- Other Port interfaces that describe the Core's needs

The Core does **not** contain:

- framework request/response types
- transport payload shapes owned by HTTP, gRPC, CLI, or messaging protocols
- vendor SDK types
- database row schemas or ORM entities
- status codes, headers, routing metadata, or other protocol details

**Interaction Rules**

- Driving Adapters receive transport input, validate transport concerns, and translate into Driving Port requests.
- Driving Ports expose use cases in application language.
- Application Services orchestrate use cases and may call Domain Services.
- Domain Services may collaborate when necessary, but cyclic dependencies are not allowed.
- Driven Ports describe what the Core needs from external systems.
- Driven Adapters translate between Driven Ports and external systems.
- Adapters should not bypass Ports or depend on each other's internal payload shapes.

## Smell Checks

The contract is probably in the wrong place if:

- renaming a JSON field forces a Port or use case signature to change
- moving from REST to a queue changes Core types instead of only Adapters
- a Port mentions `HttpRequest`, `Response`, `KafkaRecord`, `Row`, `StripeCustomer`, or other transport/vendor types
- repository or gateway Ports return persistence rows or vendor SDK objects directly
- multiple use cases are shaped around a shared transport envelope rather than around application intent

## Example

For `POST /payments`, the HTTP Adapter owns the request body, headers, authentication details, and response format. It translates that payload into an application request such as `CreatePaymentCommand` and calls the Driving Port. The Core returns an application result such as `CreatePaymentResult` or a domain/application error. The Adapter then maps that result back into an HTTP status code and response body.

If the API field names change, or the same use case later arrives through a queue consumer, the Adapter should change first. The Port and the Core should change only if the actual application behavior changed.

**Design Principles**

- All dependencies must point inward toward the Core.
- Each component should have a focused, cohesive responsibility.
- Avoid implicit coupling between adapters; composition must be explicit and intentional.
- Translation belongs at real boundaries where ownership and reasons to change differ.
