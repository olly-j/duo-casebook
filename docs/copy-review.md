# CB-002 product summary review

Reviewed all 92 product summaries in `web/catalogue.json` against `AGENTS.md` and the user-supplied writing router, reader brief, sentence craft, plain-language, evidence, AI-tell and register references. Changed 46 summaries and deliberately left 46 unchanged. The complete proposed changes, exact catalogue IDs, original summaries and individual reasons are in `research/editorial-copy.json`. The parent reviewed the patches and integrated them through build_data.py. The build rejects a patch when its recorded original summary changes.

## Six-field reader brief

- Reader: a UK-oriented iPhone Duo buyer browsing on a phone.
- Prior knowledge: knows the phone name but may not understand case materials, separate components, hinge coverage or gaps in published specifications.
- Outcome: understand each option's useful features, configuration and limitations well enough to shortlist cases and check the seller's details.
- Literal ask: none within the summary; browsing, comparing and visiting sources are supported by the surrounding interface.
- Medium and length budget: a short catalogue summary beneath a separately displayed product name. Aim for 15 to 30 words where useful; retain shorter clear summaries and allow necessary detail rather than padding or cutting facts.
- Register: plain UK consumer language, specific, concise and natural, without promotional claims or internal research instructions.

## Structural check

Each summary was read in catalogue order. Lead with the case, component or defining feature; put important limitations close to the relevant feature. Remove repeated phone and product identity where already displayed. Keep distinct options, bundle contents, finishes, removable parts and regional context where present. Retain the distinction between a front frame, a back panel, a complete set and hinge coverage. Avoid adding features merely because they appear in a product name.

Already clear descriptions were left alone, including the separate PITAKA front and back components, exposed-hinge descriptions, made-to-measure sleeves and straightforward Spigen descriptions. Repeated descriptions are not inherently defective when their exact recorded features are the same.

## Sentence check

Read all 92 summaries for clear subjects, natural word order and concise sentences. Replaced abbreviations such as PC and PU with material names, bezel with a raised edge, and articulating with jointed. Kept meaningful technical identifiers such as EPU and TPU with plain descriptions of the film or plastic part. Kept named compatibility standards and features rather than inventing broader compatibility claims.

Split dense clauses where a limitation or removable configuration deserved its own sentence. Used UK wording for notes and folded-note storage. Removed slash shorthand where ordinary conjunctions made the meaning clearer. Checked proposed text for em dashes; none remain. Sentence length was treated as a readability guide, not a reason to omit facts.

## AI-tell and hype check

Removed the subjective Apple finish description, promotional smooth-gliding wording, redundant model-verification phrases and commentary about what a title or official collection lists. Replaced internal family-grouping language with a description of available designs. Retained specific features rather than substituting generic shopping benefits, forced lists, inflated significance or unsupported assurances.

Manufacturer claims that were explicitly attributed remain attributed, including the Benks hinge-protection claim, Poetic features, Nillkin hinge protection and Ridge construction and compatibility. No new comparison, protection ranking, test result, urgency or endorsement was introduced.

## Over-correction check

Compared every proposed summary with its original. Kept useful material, coverage, attachment, configuration, finish, storage, stand and accessory details. Retained both Vaja weights with their exact meanings, the exact Noreve model identifiers and retailer attribution, the German shop context, and photographic attribution for NUDIENT's exposed front and controls. Flexible hinge films remain explicitly distinct from a rigid guard. The QDOS flexible hinge is not recast as structural protection.

Short summaries were not padded to meet a word target. Clear existing sentences were not rewritten merely to vary their style. Product-name repetition was removed where redundant, while names identifying a distinct finish, model or bundled case were retained where useful. No unknown detail was filled in to make a sentence sound more complete.

## Source invariants and verification

The catalogue was the supplied factual baseline; no browsing or new product research was performed. Every patch stores the exact original summary and ID from that baseline. No status, brand, name, source record, image, price, availability record or generated catalogue file was changed. Missing facts remain unknown. No new measurement or comparison claim was added. Historical evidence was not turned into Duo testing or a score.

A focused local validation confirmed 92 catalogue products, unique patch IDs, exact original-summary matches, changed text for every patch, the required JSON shape and no em dashes in proposed summaries. Final counts are 92 reviewed, 46 changed and 46 unchanged. Only the two requested deliverables were written. Repository-wide checks and native writing executables were not run; this task was limited to the specified inputs and editorial outputs. No other agents, installation or publication were used.

## Supplied fresh-reader findings

The findings supplied in the separate context-free reader review, concern the wider site. They are prior reader evidence, not a new reader test of these patches. No fresh reader was commissioned for this task.

The reader understood the phone name, browsing and comparison actions, the dated price snapshot, source currencies, separate coverage areas and the absence of independent Duo testing. They recognised that missing measurements are unknown, rather than zero or evidence of a thinner or lighter case. They also identified local-only saving, public correction reporting and the limits of privacy statements involving hosting, external images and sellers.

Remaining reader questions included delivered totals, current buying terms, exact compatibility beyond the phone name, the mechanics and capacity of sharing and comparison, and the ordering of evidence-related sorts. Those questions cannot be answered by editorial inference.

The supplied recommendations favour precise missing-value wording, price-freshness information near prices, explicit structural hinge-cover labels and a clear separation of front-and-back coverage from hinge coverage. They also favour concise previous-model testing caveats, plain image attribution and removal of internal Thinborne review instructions. Those surrounding-site changes are outside these two deliverables.

The directly relevant Apple finding was applied: remove the subjective finish description while retaining the matte two-part shell and built-in magnets. Across the remaining summaries, the same reader perspective guided removal of internal verification wording, clear component descriptions and preservation of uncertainty. This editorial review does not claim that the wider site's outstanding reader questions have been resolved.
