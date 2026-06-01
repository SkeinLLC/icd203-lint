<!-- icd203-lint: disable-file -->
# ICD-203 for the rest of us

A working primer on Intelligence Community Directive 203 for analysts who don't write under the DNI seal but still owe their readers honest tradecraft.

## Who this is for

You write reports that decisions get made from. Maybe you're CTI inside a bank, or a Tier-3 SOC analyst writing up an incident, or a vendor researcher about to publish a blog that will get cited by people who weren't in your call. Your readers can't go back to the raw data. They have to trust you. ICD-203 is the cleanest answer the U.S. Intelligence Community has produced to the question "what does trustworthy analysis look like on the page?"

It is not a magic wand. It is a discipline. The point of this doc is to argue that the discipline works outside the IC and to show how it cashes out in habits you can build into your own writing today.

## What ICD-203 actually says

The directive was issued in 2007 and reissued in 2015 under DNI James Clapper. It sets out the analytic standards every IC product is supposed to meet. The full list is short, and worth reading once a quarter:

1. Properly describes quality and credibility of underlying sources, data, and methodologies.
2. Properly expresses and explains uncertainties associated with major analytic judgments.
3. Properly distinguishes between underlying intelligence and the analyst's assumptions and judgments.
4. Incorporates analysis of alternatives.
5. Demonstrates customer relevance and addresses implications.
6. Uses clear and logical argumentation.
7. Explains change to, or consistency of, analytic judgments.
8. Makes accurate judgments and assessments.
9. Incorporates effective visual information where appropriate.

Nine standards. None of them are about what to think. All of them are about how to show your work.

The directive also fixes a vocabulary. Estimative language runs on a probability ladder that any analyst can recite from memory after a week of practice:

| Phrase | Probability band |
|---|---|
| almost no chance / remote | 01-05% |
| very unlikely / highly improbable | 05-20% |
| unlikely / improbable | 20-45% |
| roughly even chance | 45-55% |
| likely / probable | 55-80% |
| very likely / highly probable | 80-95% |
| almost certain / nearly certain | 95-99% |

Separate from the estimative ladder, ICD-203 expects each major judgment to carry a confidence level: **low**, **moderate**, or **high**. Confidence is about the sources and the reasoning chain, not the likelihood of the event. You can have high confidence that something is unlikely. You can have low confidence that something is almost certain. Those two ideas live in different boxes for a reason.

## Why analysts outside the IC should care

The reflex objection is "we're a private company, we don't write under those rules." Fair, in the narrow legal sense. But the standards weren't invented to satisfy lawyers. They were invented because the IC kept getting big calls wrong in ways that were avoidable, and the postmortems kept finding the same pathologies: source quality not declared, alternatives not considered, confidence and likelihood blurred together, and judgments that drifted from the cited evidence.

If you've read a vendor threat report in the last 90 days, you have seen all four of those pathologies in print. The 2002 NIE on Iraqi WMD is the textbook case the IC built ICD-203 against. The 2024 reporting on Volt Typhoon prepositioning in U.S. critical infrastructure is the textbook case the CTI world ought to build something equivalent against. We don't yet have a shared standard. ICD-203 is the closest thing on offer.

Three reasons to adopt it even when nobody is making you:

The first is honesty. Estimative language forces you to commit to a probability band. You cannot hide behind "may," "could," "potentially." Readers know within five seconds whether you think this is a coin flip or a near certainty. If you cannot commit, you have to write that too, and explain why.

The second is collaboration. A SOC analyst handing off to IR, a CTI team briefing a CISO, a vendor publishing for a thousand readers they will never meet — all of these only work if the receiving side can re-derive your reasoning. ICD-203 is a serialization format for analytic thought. It is the closest thing the field has to a wire protocol.

The third is brand. The CTI community is drowning in vendor content that reads like marketing wearing a lab coat. Analysts who write under ICD-203 stand out instantly because the prose carries the marks of discipline: explicit confidence, declared sources, alternatives considered. The signal is unmistakable to anyone who has done the work.

## The five habits that do most of the work

You don't need to memorize the whole directive to write better tomorrow. Five habits, applied repeatedly, account for most of the lift.

### Habit one: every major judgment carries an explicit confidence level

A "major judgment" is any sentence the reader might quote or act on. If the sentence answers a customer question, it is a major judgment. If you can imagine the CISO repeating it to the CFO, it is a major judgment. Every one of them gets a confidence tag.

Not this:

> The group is targeting the financial sector.

This:

> We assess with moderate confidence that Storm-0501 is targeting the U.S. mid-market financial sector based on three sources: Microsoft Threat Intelligence reporting from April, the Mandiant M-Trends 2026 report, and our own telemetry from two GC SOCs in Q1.

The first version is sourceless and unfalsifiable. The second tells the reader exactly what backing the claim has, lets them push back at the right point, and survives being lifted out of context.

A confidence tag does not have to read like a courtroom citation. "We assess with high confidence..." or "Low confidence:" at the head of a sentence is enough. The point is to make the calibration visible.

### Habit two: keep likelihood and confidence in different boxes

This is the rule that takes the longest to internalize and produces the most embarrassing mistakes when you skip it. ICD-203 is explicit: probability and confidence are independent dimensions.

A worked example. You see a new ransomware operator emerge that has, in three months, hit only U.S. logistics firms. You write:

> We assess with high confidence that the operator will continue to target U.S. logistics firms over the next quarter.

What does that sentence mean? Three months of consistent targeting is decent evidence, so the confidence claim is plausible. But the high-confidence framing now reads as a near-certain prediction. If you actually mean "probably, but the sample is small and operators shift," the right sentence is something like:

> We assess that the operator will likely continue to target U.S. logistics firms over the next quarter (moderate confidence based on three months of consistent targeting and limited corroborating sources).

Likelihood: "likely" (55-80%). Confidence: moderate. The reader now knows both your forecast and how much weight to put on it. That is two pieces of information traveling in two channels.

The worst version of this mistake is to read someone else's high-confidence call as a near-certain prediction and re-publish it that way. Half the bad CTI commentary on X works exactly like that.

### Habit three: attribution claims need a TTP or a sourcing chain

Naming an actor is the most cited and least disciplined move in CTI. ICD-203 does not ban it. It demands that the claim be grounded in something the reader can evaluate.

A defensible attribution sentence:

> We assess with moderate confidence that the intrusion is the work of APT41 based on overlap in C2 infrastructure (three IPs published by PwC's 2025 Earth Lusca report), the use of the China Chopper webshell variant first documented by FireEye in 2019, and a Mandarin-language operator note recovered from the staging directory.

That sentence tells the reader the basis: infrastructure overlap, TTP fingerprint, and an in-the-clear artifact. They can argue with each piece. If you cannot produce something equivalent, the attribution claim should not be in the report. "Likely APT-aligned actor" with no chain of reasoning is not analysis; it is decoration.

A useful internal test: would the sentence survive cross-examination from a peer who has read every public APT41 report? If the answer is "no, they would tear the attribution out in two minutes," it does not belong in your deliverable either.

### Habit four: single-source claims do not get moderate or high confidence

If your only source for a judgment is one vendor blog, one Twitter post, or one telemetry hit, the maximum honest confidence you can assign is low. Sometimes that's enough. A SOC product warning of in-the-wild exploitation can fire on a single high-quality source if the report flags it as such. A board pack drawing the same conclusion needs corroboration.

ICD-203 phrases this around source quality and corroboration. The working rule is simpler: count your sources, name them, and let the reader see whether they are independent. Three pieces of vendor reporting that all cite the same Mandiant blog are one source, not three. The dependency graph is what matters.

### Habit five: future-tense predictions need estimative language

The single most common ICD-203 violation in published CTI is the bare future. "The group will pivot to financial services." "Operators are going to weaponize this CVE." Both sentences sound confident and commit the writer to nothing.

The fix is mechanical. Replace the bare future with a phrase from the estimative ladder. "The group will likely pivot to financial services" is a real prediction the reader can argue with. "Operators are roughly even odds to weaponize this CVE within 30 days" is a real prediction the reader can hold you to. "Will" without a hedge or a defensible certainty is a tell that the writer has not done the work.

The exception is verifiable near-term events. "CVE-2026-1234 will be added to the CISA KEV catalog" is fine if you know it from a public CISA pre-announcement. The test is whether the prediction is grounded in something already in motion.

## The arguments against, briefly

This section exists because honest writing about a method includes the strongest objections to it.

**"The estimative ladder is fake precision."** True in the narrow sense that there is no way to back-test the exact probability bands. The directive itself does not claim otherwise. The bands work because they force the writer to commit and the reader to know roughly what was committed to. The alternative is "may" and "could," which commit to nothing.

**"Nobody reads the confidence tags."** Sometimes true. The fix is not to remove the tags but to surface them better. A board pack that opens with a one-line "Bottom line up front (high confidence):" is doing the work in the place the reader will look. ICD-203 does not specify layout, only that the calibration be present.

**"It slows the writer down."** It does, at first. After three months it becomes the default mode of writing and is no slower than the alternative. The slowdown is the point, anyway: the discipline catches sloppy claims before they ship.

**"It's not legally binding outside the IC."** Correct. Nor is the ICS-220 sourcing standard, nor any of the IC standards. Voluntary adoption of a discipline is how every profession works. Lawyers follow the Bluebook because it makes citations legible to other lawyers, not because they are forced to.

## How this primer connects to the linter

The five habits above map directly onto the five default rules in `icd203-lint`:

- `assessment-no-confidence`: assessment sentences without a confidence label
- `attribution-unsourced`: actor naming without a sourcing or TTP chain
- `single-source-overconfidence`: moderate or high confidence asserted on a single-source claim
- `future-unhedged`: future-tense projections without an estimative qualifier
- `quote-unattributed`: direct quotes that don't name a speaker or document

The linter is a tool, not a judge. It catches the patterns a careful analyst would catch on a second pass. It is fastest when run in CI on a markdown report repo, so the linter check is the last green box before the report ships. It is dumbest when applied to a SOC ticket update or a one-line Slack note, which is why every rule can be disabled per file or per line.

## Where to go next

Read the directive itself. It is 14 pages and the writing is plain. The ODNI version lives at intelligence.gov; mirrors are easy to find.

Read Richards Heuer's *Psychology of Intelligence Analysis* if you have a week. The 1999 CIA edition is public domain. ICD-203 reads like a compressed engineering spec written from Heuer's recommendations.

Read the Cyber Threat Intelligence Curriculum from SANS (FOR578) if your team will fund it. The curriculum treats ICD-203 as the default frame, which is rare in private-sector training.

Run `icd203-lint` against your last three reports. The first run will hurt. The second run, after you have rewritten them, will hurt less. Six months in, you stop running into the rules at all because you stop writing the violations in the first place. That is the point.
