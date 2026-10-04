# Evidence

Three results: a same-plan comparison with and without the route skill, a compaction test, and a figure from the author's real use. Numbers come from the test reports named in each section. The with/without test is small, and on that plan the route skill cost more.

## With and without the route skill, same plan

**Method.** The same 7-stage plan (rename and docs stages, a review stage) was run 2 times with the route skill and 2 times without, headless, on Claude Code 2.1.289. All four runs exited cleanly and none read answer files. The skill was loaded in both runs with it and in neither run without it. Cost is as reported by Claude Code.

| | Without the skill (2 runs) | With the skill (2 runs) |
|---|---|---|
| Who-does-what table before starting | 0 of 2 | 2 of 2 |
| Subagents given a model | 0 of 6 | 10 of 10 |
| Rename and docs stages (mechanical) ran on | main session, Opus 5.5, 2 of 2 | a Sonnet subagent, 2 of 2 |
| Review on a different model from the work | 0 of 2 (Opus reviewed Opus) | 2 of 2 (Opus reviewed Sonnet) |
| Cost per run | $1.52, $1.26 | $1.71, $1.68 |

Mean cost was $1.39 without and $1.70 with the skill: 22% more with it.

**Likely reasons for the extra cost (inference, not measured):** the skill's own instructions add tokens to every run, and the runs with it used two more subagents each (10 against 6 across two runs). Those outweighed the cheaper Sonnet tokens on a plan this small. The test does not show where the cost breaks even.

## Compaction test

**Method.** A six-stage plan with long outputs (300 lines per stage that needed one, 600 items to classify) was run 6 times on Claude Code 2.1.288 with automatic compaction forced to happen early (a 100,000-token window). Three variants of the skill text were compared, 2 runs each. In the control variant the allocation table was never written to a file.

**Results.**

- 6 of 6 runs finished with all six stages Done and correct output, after 3 to 4 compactions each.
- No step was started twice after a compaction in any run.
- In 3 runs a worker started before a compaction and finished after it; its result was used and its stage completed correctly.
- The only dispatch after a compaction in each run was the last stage's reviewer, and it used the same model as the table printed before the first compaction in all six runs. Claude Code's own compaction summary carried the table forward, and the board carried status. The variants did not differ, so the kit ships the simplest text, the control variant.
- A separate check compacted at 50% of the window on the same plan: 2 of 2 runs passed, with 2 compactions each and no step started twice.

**Limits.** One plan of six stages, 3 to 4 compactions per run, and only one delegated stage left after the first compaction. A much longer run, with many compactions and many rows still to dispatch, was not tested.

## Real use

From the transcripts of 34 of the author's sessions that called an earlier version of the route skill (subagents started before 2026-10-02):

| | Cost at API rates |
|---|---|
| Subagent work dispatched with a Sonnet model after the route skill ran | $1,232 |
| The same tokens priced at Opus 5.5 | $2,070 |
| The route skill's own cost: its text written to the cache once per call, then re-read on every later turn until the next compaction | about $20 |
| Upper bound on its own cost, also counting the output of the turn that wrote the allocation table | $38 |

The earlier version's text was about 3,300 tokens (median of 46 calls where it could be measured). This release's is about 1.7× longer, which scales the skill's own cost to about $34 (upper bound $64).

Qualifiers:

- It is the author's earlier version of the skill, not this release.
- The author's setup also had other rules that sent work to Sonnet: sessions where the route skill never ran set a Sonnet model on about the same share of subagents (59% against 58%). So these numbers show that the skill's own cost is small next to the work it routes; they do not show how much of the saving the route skill alone caused. The controlled test above is the evidence that, without the skill, Claude Code gave no subagent a model.
- It is a price comparison on the same tokens, not a controlled test. A top model might have needed fewer turns, and an API-equivalent price is not what a subscription user pays.

This figure is not a claim that the plugin saves money on a small plan. The with/without test above shows the opposite on a 7-stage plan.
