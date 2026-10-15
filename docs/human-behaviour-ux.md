# Human-Behaviour UX Heuristics

Status: Active guidance

Use this guidance when a task changes or reviews user journeys, information architecture, interaction design, navigation, forms, onboarding, settings, purchase or upgrade flows, notifications, empty states, feedback states, or other user-facing product behaviour.

These are **principles and hypotheses, not hard rules**. They are starting points for design decisions. Context, user needs, accessibility, platform conventions, product goals, qualitative research, usability testing, analytics, experiments, and observed outcomes decide whether an application of a principle is successful.

Do not force a heuristic where it makes the experience worse. Record the intended user outcome, the design choice, and the evidence used to validate it when the decision is material.

## Core heuristics

### 1. Jakob's Law: favour useful familiarity
Users bring expectations from products they already know.

Consider:
- familiar interaction patterns, navigation models, labels, and icons;
- reusing learned behaviour where it reduces friction;
- limiting unnecessary interaction novelty;
- introducing unfamiliar patterns only when they produce a meaningful benefit.

Test whether familiarity improves comprehension and task completion for the target users. Familiar patterns can still be inaccessible, outdated, or wrong for the context.

### 2. Hick's Law: reduce unnecessary decision load
Decision time tends to increase as the number and complexity of choices increases.

Consider:
- removing low-value options;
- grouping related choices;
- recommending a sensible default when evidence supports one;
- revealing advanced options progressively;
- separating distinct decisions instead of presenting one dense choice set.

Avoid hiding choices users need for control, safety, accessibility, or informed consent merely to make a screen look simpler.

### 3. Fitts's Law: make important targets easy to acquire
The time and effort needed to reach a target is affected by its size and distance.

Consider:
- sufficiently large interactive targets;
- placing high-frequency or time-critical actions within easy reach;
- separating adjacent actions that have different or destructive outcomes;
- avoiding tiny targets and precision-heavy interactions;
- checking reachability across pointer, touch, keyboard, switch, and assistive input where relevant.

Validate against accessibility requirements and real device use rather than visual size alone.

### 4. Miller's Law: manage working-memory load
People can hold only a limited amount of information in working memory.

Consider:
- breaking dense content into meaningful chunks;
- grouping related information;
- using short sections and clear steps;
- preserving context so users do not need to remember information across screens;
- reducing avoidable mental arithmetic, recall, and cross-referencing.

Chunk by meaning, task, and user model rather than applying an arbitrary item count.

### 5. Proximity: use space to communicate relationships
Items placed near one another are usually perceived as related.

Consider:
- keeping labels, controls, validation, and supporting text visually connected;
- grouping related controls and content;
- using larger separation to distinguish unrelated groups;
- letting layout and spacing communicate structure before decoration is added.

Check that grouping remains clear under responsive layouts, zoom, localisation, dynamic type, and assistive technology.

### 6. Von Restorff Effect: make the important difference visible
A visually distinctive item is more likely to attract attention and be remembered.

Consider:
- giving the primary action appropriate emphasis;
- using contrast intentionally;
- making a recommended or exceptional option visibly distinct when that recommendation is justified;
- keeping secondary elements quieter so the hierarchy remains meaningful.

Do not rely on colour alone, manufacture urgency, or visually bias users toward a choice that conflicts with informed consent or their interests.

### 7. Serial Position Effect: use beginnings and endings deliberately
People often remember the first and last items in a sequence more readily than the middle.

Consider:
- placing the strongest orientation or highest-value information early;
- putting critical confirmation, next steps, or closure at the end;
- avoiding burial of essential information in long undifferentiated middles;
- using summaries, sectioning, and repeated context when material information must appear mid-flow.

Do not move legally, ethically, or operationally important information solely to optimise recall. The full journey must remain understandable.

### 8. Tesler's Law: let the system absorb avoidable complexity
Every product has some irreducible complexity. Good product design decides where that complexity should live.

Consider:
- smart defaults;
- autofill and remembered preferences with appropriate consent;
- automation of repetitive work;
- deriving values the system already knows;
- reducing duplicate entry and unnecessary manual coordination;
- preserving user control where automation can be wrong or consequential.

Prefer moving complexity into the product when the system can handle it reliably, transparently, privately, and reversibly.

### 9. Doherty Threshold: keep the interaction responsive and legible
People stay engaged when the system responds quickly and clearly.

Consider:
- immediate acknowledgement of user input;
- useful loading states when work takes time;
- progress indicators for meaningful waits;
- clear success, error, and recovery feedback;
- optimistic interaction only where failure can be handled safely.

Measure actual and perceived responsiveness. Never use fake progress or ambiguous state to create the impression of speed.

### 10. Peak-End Rule: design memorable moments and endings
People often judge an experience disproportionately by its most intense moments and how it ends.

Consider:
- making onboarding success feel clear and earned;
- marking meaningful milestones;
- designing consequential moments with care;
- giving completed actions strong confirmation and useful next steps;
- making failure recovery humane and confidence-restoring;
- designing the end of a journey, cancellation, empty state, or completion state as intentionally as its beginning.

Evaluate the whole journey. A polished peak or ending must not compensate for chronic friction elsewhere.

## Apply the heuristics as a system

A useful review asks how attention, memory, choice, action, feedback, and completion work together. Individual heuristics can conflict. For example, reducing choices may harm expert control, familiarity may preserve a poor legacy pattern, and visual emphasis may become manipulation.

For a material UX decision:
1. identify the user goal and context;
2. select only the heuristics relevant to the problem;
3. state the hypothesis and expected outcome;
4. prototype or implement the smallest useful version;
5. check accessibility and platform conventions;
6. test with representative users or suitable behavioural evidence;
7. measure task success, errors, comprehension, confidence, time, or other relevant outcomes;
8. keep, revise, or remove the design based on evidence.

Treat disagreement between a heuristic and observed user behaviour as useful evidence. The desired outcome has priority over mechanical compliance with the heuristic.