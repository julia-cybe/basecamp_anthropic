# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: An agent with tools to get passenger details and flight details so that he can suggest alternatives, provide a refund or escalate to a human.
Does: Customers can now refer to our support agent which responds immediately and either proposes solutions or escalates to a human.
Number: $0.0565 per resolved contact, 5 shapes, 3 runs, cold
Guardrail: The agent escalates to a human rather than attempting to resolve situations that are out of scope or legally sensitive — so it can never make a commitment it shouldn't. 
Next: I have no eval case that tests whether the agent handles a connection the passenger might have missed correctly. That's a gap — and it's one of the harder shapes to get right because the agent has to reason about timing across two flights.
Still broken: Cache hit could not be tested successfully. 
Lever: intelligence

## Priya asked

Costs: $756/week vs $94,530 human
Wrong: Before the fix, when a customer threatened legal action, the agent offered rebooking options instead of escalating.
Runs it: we need a support team at Larkspur
Left out: it cannot handle requests for groups
