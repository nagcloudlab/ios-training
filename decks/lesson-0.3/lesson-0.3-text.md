# Lesson 0.3 — iOS Application Lifecycle Deep Dive

*iOS Architecture Mastery · Foundation Series*

> Lesson text as shared; the deck (`index.html`) uses **only this text**. The running example
> banking app is **NPay**. **Gaps:** the text ends inside section 8 (after "UIKit — Delegate-driven approach");
> the lifecycle simulator shows only scenario 1 of 5 and the memory simulation only the 35% level, so the deck's
> scenarios 2–5 and the 65% / 90% levels were authored to follow the text (flagged below).

Today we'll answer a fundamental question: **When a user leaves an iPhone app, what actually happens to that app?**
Does it stop? Does it keep running? Is it destroyed? And what happens when the user returns?

## Our learning journey

1. Process versus scene
2. Foreground, background and suspension
3. Cold launch versus warm activation
4. Memory pressure and app termination
5. SwiftUI versus UIKit lifecycle
6. Real-world architecture and challenges

## 1. Process versus scene — the most important distinction

Imagine a shopping mall. The mall building is an application **process**; each shop is a **scene**; the operating system is the mall management; the user visits different shops. One building can contain several shops; one app process can manage multiple scenes.

Example: one app process (shared executable code, memory, threads and services) with Scene A, product catalog, **active**, and Scene B, order details, **background**. Conceptual multiwindow example; most relevant on iPadOS, while an ordinary iPhone app commonly has one main window scene.

- **Process:** a running instance of your application; its execution environment.
- **Scene:** an instance of your app's UI that the system manages, with its own lifecycle states.

**Critical point:** a scene can be in the background while another scene of the same app is active, so scene lifecycle and process execution state are not identical.

## 2. Understand the lifecycle states

- Scene states (SwiftUI `scenePhase`): **active, inactive, background**.
- Process execution conditions: **running, suspended, terminated**.
- **Suspended is not a SwiftUI scenePhase value.**

Typical single-scene iPhone app: Not running (no process) → Active (foreground, accepting interaction) → Inactive (foreground, temporarily not active) → Background (no longer foreground; may run briefly) → Suspended (kept in memory, not executing) → Terminated (process no longer exists). One possible progression, not a mandatory sequence.

## 3. Let's simulate the app lifecycle (NPay)

| # | Scenario | Scene | Process | Next event |
|---|---|---|---|---|
| 1 | App not running | No scene | Not running | Tap the icon: the system launches the app and activates its initial scene |
| 2 | *Authored:* Using the app | Active | Running | Swipe up to the Home Screen |
| 3 | *Authored:* Just left the app | Background | Running briefly | Wait while the user is in another app |
| 4 | *Authored:* Suspended | Background | Suspended | The user opens a memory-heavy game |
| 5 | *Authored:* Terminated | No scene | Terminated | Tap the icon again: a fresh launch |

**Misconceptions:** "When the user switches apps, the old app is killed": incorrect; iOS usually moves the scene to the background and may eventually suspend the process; termination is separate. "Background means continuous execution": background does not mean unrestricted execution.

## 4. Cold launch versus warm activation

The same tap can mean different internal work:

- **New process (cold):** application initialization must happen again.
- **Existing process (warm):** application state may already be in memory.
- **Existing running process:** the app can become foreground without being resumed from suspension (it is still executing eligible background work; the scene transitions and foreground interaction resumes).

Cold, warm and hot launch are used informally; precise meanings vary by tool.

**Example:** NPay shows ₹50,000; the user switches away and returns. If the process survived, the in-memory balance may still be ₹50,000; if terminated, NPay must reconstruct its interface and retrieve or restore data.
**Rule:** Never design an iOS application assuming that its process will remain alive.

## 5. Why does iOS suspend applications?

Illustrative workload: Messaging suspended, Camera running, Shopping suspended, Music background audio. The system balances responsiveness, battery, memory and permitted background activity. A suspended process can remain in memory but does not execute instructions. Advantages: saves CPU time and energy; preserves state in memory; can make returning faster; lets the system prioritize foreground work.

**Music and navigation:** audio playback can continue when properly configured and under the audio rules; navigation may receive background location updates under appropriate permissions. These are specific permitted capabilities, not a general exemption.

**Question:** Can an app start a normal timer and assume it fires every second after suspension? **No.** Suspended code is not executing; time-sensitive or background work needs a system-supported mechanism, subject to iOS policies.

## 6. Memory pressure — why iOS terminates apps

A memory-intensive game needs memory; suspended apps may be terminated to reclaim it. Teaching simulation: 35% low pressure (text); *authored* 65% rising and 90% high, where suspended apps are terminated. Not a real measurement or Apple's algorithm.

**Jetsam:** a suspended app can be terminated without being resumed; it cannot rely on a final cleanup callback; the next launch may need to reconstruct state; foreground apps can also be terminated if memory use becomes problematic. Persist important data at appropriate moments.

## 7. How to design for termination

Registration form: **poor design** keeps everything only in memory, so termination loses progress; **better design** persists a draft as the user goes, so a new process recovers it. **Process memory is temporary. Durable user data belongs in persistent storage.** SwiftData, files and Keychain serve different purposes; sensitive data needs protection.

## 8. SwiftUI lifecycle versus UIKit lifecycle

Historically UIKit apps used `UIApplicationDelegate`; modern UIKit apps may also use `UISceneDelegate` (delegate-driven). SwiftUI introduced a more declarative way to define application structure and observe scene lifecycle changes.

*Authored for the deck:* Part 8 shows two short snippets side by side: a UIKit `AppDelegate` with `application(_:didFinishLaunchingWithOptions:)`, and a SwiftUI `@main` `NPayApp` with a `WindowGroup` observing `scenePhase`.

> *The shared text ends here ("Compare application entry approaches — UIKit — Delegate-driven approach").*

## Deck changes after the Unit 00 audit

The text above is unchanged. The deck now differs from it as follows.

**Corrections**
- Part 2 lifecycle diagram: on launch the scene is **inactive** while its first frame is drawn, then becomes **active** (the earlier diagram went from not running straight to active). Leaving goes inactive → background → suspended → possibly terminated. The simulator's first scenario says the same.
- Part 1 no longer implies scenes are optional: Apple's TN3187 says apps built with SDKs released after iOS 26 must adopt the scene-based lifecycle.

**Cuts**
- Part 8 (SwiftUI vs UIKit lifecycle, and its two authored snippets) is removed from the deck: Lesson 0.4 owns that material, and the shared text was truncated there. The end slide now points to Lesson 0.4 instead of promising content already shown.

**Consistency**
- The shopping-mall analogy is replaced by the unit's hotel analogy (from 0.1): NPay's suite is the process, each room of the suite is a scene, the guest is the user.
- Non-NPay examples became NPay: scenes "NPay accounts" / "NPay statement"; "open NPay in three different situations"; the registration form is NPay's account-opening form; the balance example uses ₹25,000.

**Authored additions (flagged)**
- Outcomes slide replaces the "learning journey" agenda.
- "Where we are" map slide (scene, SpringBoard, sandbox lit) with Last time (0.2) / Today.
- One-line pointers: launches from a notification or link (Unit 10: 10.6, 10.8), BackgroundTasks (10.7), drafts and state restoration (6.9), storage choices (Lesson 0.9).
- Recap slide before the review.
- Review grows from 1 to 5 questions (the text's timer question plus: scenes in different states; which value is a scenePhase; what happens to a suspended app under memory pressure; spaced review from 0.2: who reloads the balance after termination).
- "Where this goes next" slide: 0.4, 6.9, 8.8, 10.7, 10.8.
- Lab: predict NPay's scene state and process condition for seven event cards (answers in the speaker notes).
