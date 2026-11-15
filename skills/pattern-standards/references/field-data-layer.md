# Field XVI: Data-Layer Discipline (P106–P108)

Constructs for the layer under every service: the database sessions,
the stream consumers, and the read-after-write path. Shared failure
mode: defaults that hold until the worst possible moment.

### P106 · Database session hygiene
**Failure.** One forgotten `BEGIN` without commit holds locks and bloats the WAL; an unindexed query holds a pool connection for minutes; the pool is sized by vibes; the primary dies of idle-in-transaction.
**Mechanism.** Every session carries enforced guards by default: statement timeout, idle-in-transaction timeout, lock timeout, connection lifetime cap. Pool size is derived from measured saturation, never guessed. Long migrations bypass the guards explicitly and locally, never by disabling them globally.
**Analysis.** Proven (Postgres DBRE doctrine; `statement_timeout` as the first line of defense). Refuse guards-off-by-default with per-query opt-outs; the default must be safe.
**Links.** P26 (lock ordering composes with lock timeouts), P47 (session settings pinned per request epoch), P25 (the pool is the connection arena), P100 (connections are a budgeted resource).

### P107 · Consumer inbox
**Failure.** At-least-once delivery double-applies on the consumer even though the producer's write was idempotent; replays after a DLQ fix re-run effects that already committed.
**Mechanism.** The consumer keeps an inbox table of processed message IDs and checks it in the *same transaction* as the state change; a duplicate conflict acknowledges the message with no effect; inbox retention is bounded and T33-shaped. The atomicity of inbox-check plus state-change is the entire pattern; an inbox consulted outside the transaction is a race.
**Analysis.** Proven (the transactional-inbox pattern; Kafka Streams effective-once discussions). Refuse inbox checks outside the state-change transaction, and unbounded inbox retention.
**Links.** T33 (the producer-side twin), T32 (outbox and inbox close the loop), P53 (quarantine handles the unparseable before the inbox matters).

### P108 · Sticky read-after-write
**Failure.** The write lands on the primary, the immediate read routes to a lagging replica, and the user's data vanishes; support tickets follow the replica lag graph.
**Mechanism.** After a write, the session records the write's position (LSN, GTID, or version token); reads within the staleness window route to a replica that has advanced past that position, or to the primary; past the window, normal replica routing resumes. Positions, not sleep durations.
**Analysis.** Proven (GTID-based read-your-writes in MySQL fleets; LSN-token practice in Postgres stacks). Refuse time-based guessing ("sleep 100ms then read the replica"); the token is the pattern, the nap is the bug.
**Links.** P21 (the staleness contract this composes with), P55 (OCC arbitrates genuinely concurrent writers), T38 (the causal token, datacenter edition).
