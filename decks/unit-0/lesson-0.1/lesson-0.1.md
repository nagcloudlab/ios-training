# Lesson 0.1 — iOS Architecture & App Startup

> **Status:** Comprehensive reconstructed teaching guide, **not a verbatim transcript** of the original chat.  
> **Audience:** Experienced programmers new to iOS; senior-developer / trainer depth.  
> **Running example:** NPay, a fictional SwiftUI banking app.  
> **Deliverable target:** Fullscreen, offline HTML animated masterclass, with presenter notes and learner questions.

## Learning outcomes

By the end, participants should be able to:

1. Distinguish an installed app bundle from a running app process and a UI scene.
2. Explain the major iOS platform layers and the boundaries between app code, frameworks, services, kernel, and hardware.
3. Narrate a tap on an app icon through system launch coordination, process startup if needed, dynamic loading, SwiftUI application entry, scene setup, and first frame.
4. Distinguish cold launch from foreground activation of a surviving process.
5. Explain Mach-O, dyld, virtual address space, thread, sandbox, `@main`, `App`, `WindowGroup`, `View`, and `body` at the correct abstraction level.
6. Identify startup performance risks and formulate appropriate investigations.

## Teaching contract and narrative

The whole lesson answers a single question: **What happens inside an iPhone after the user taps the NPay icon?** Start from the visible user experience and progressively reveal invisible mechanisms. Keep returning to the same phone and app. Every segment follows **predict → reveal → explain → connect**. Never claim that a conceptual diagram is a precise trace of undocumented Apple internals.

## Act 1 — The mystery: one tap

**Opening scene:** Show only a large, realistic iPhone with an NPay icon on a clean white background. No diagram yet. Ask: “Does Swift begin executing the moment your finger touches the icon?” Allow guesses. Reveal that the icon is system UI and that an installed application need not have a running process.

**Core distinction:**

- **App bundle:** Signed executable and associated resources installed on storage.
- **Process:** OS-managed execution environment, with identity, virtual address space, threads, resources, and restrictions.
- **Scene:** A system-managed instance of an app's user interface. A process and a scene are not interchangeable concepts.

**Analogy:** A recipe book (installed program) is not the same as a working kitchen (running process); a dining room (scene) is where the user interacts with the experience.

**Ask:** Can an installed app have zero running processes? **Answer:** Yes.

## Act 2 — The platform beneath the app

### Conceptual layer map

```text
NPay application code (Swift)
            ↕
SwiftUI / UIKit / Foundation / Security and other frameworks
            ↕
iOS services and platform facilities
            ↕
Darwin / XNU kernel (processes, scheduling, virtual memory, protection)
            ↕
Apple hardware (CPU, GPU, memory, storage, input)
```

This is a **responsibility map**, not a mandatory one-way call chain. Frameworks and system services cooperate through multiple mechanisms.

**Trainer script:** “The app doesn't directly create its own OS process or control the display hardware. It expresses intentions using APIs; the platform mediates execution and resources.”

**Question:** Which layer schedules threads? **Expected:** OS/kernel scheduling mechanisms.

## Act 3 — The icon tap and system coordination

1. User touches the Home Screen icon.
2. The Home Screen/system UI (commonly associated with **SpringBoard**) handles the interaction.
3. The system coordinates launching or activating the target app.
4. The next path depends on whether a usable app process already exists.

**Technical accuracy note:** SpringBoard is an important system process, but specific internal daemon and IPC sequences are private and can change between iOS versions. Present the flow as conceptual.

### Branching diagram

```text
User taps NPay
         │
         ▼
System coordinates launch/activation
         │
    Existing process?
       /       \
     Yes        No
      │          │
Foreground /    Create new process
activate scene  + load executable
       \        /
         UI becomes available
```

**Question:** Does every icon tap create a new process? **Answer:** No. An existing process may be resumed or activated.

## Act 4 — Process creation

A new process is not merely “calling a Swift function.” The OS establishes an execution context, which includes:

- Process identity and OS-managed resources.
- A **virtual address space** with mappings for executable code, data, dynamic libraries, heap and thread stacks.
- At least an initial execution thread; more threads may be created as needed.
- Security constraints including sandbox and signing-related enforcement.

### Virtual memory model

```text
┌──────────── NPay process ─────────────┐
│ Virtual address space                       │
│  • executable / shared library mappings     │
│  • globals and static storage               │
│  • dynamic allocations (heap)               │
│  • thread stacks                            │
│  • other mapped regions                     │
├─────────────────────────────────────────────┤
│ Thread execution + OS resources             │
│ Security context and sandbox restrictions   │
└─────────────────────────────────────────────┘
```

**Caution:** These regions are conceptual, not a fixed physical layout; virtual addresses do not equal physical RAM addresses. Avoid “struct always stack/class always heap.”

**Analogy:** An office building (process) with a managed address plan (virtual memory) and workers (threads). Workers execute tasks; they are not the building itself.

**Ask:** Is a process the same as a thread? **Answer:** No.

## Act 5 — From Swift source to executable

### Build-time pipeline (simplified)

```text
.swift source
   ↓
Swift frontend: parsing + type checking
   ↓
SIL (Swift Intermediate Language)
   ↓
LLVM IR and machine-code generation
   ↓
Linking and signing
   ↓
Mach-O executable in the app bundle
```

**Mach-O** is the executable file format used by Apple platforms. It contains structured headers, load commands, segments/sections and other metadata needed for loading and execution. The installed `.swift` source is not interpreted on every normal native app launch.

**Question:** Is Mach-O the Swift programming language? **Answer:** No, it is a binary format.

## Act 6 — dyld and runtime preparation

**dyld** is Apple's dynamic loader. Broadly, it helps prepare executable images and their dynamic dependencies, including required loading and binding work. Exact details vary with platform, OS version and optimizations such as shared caches.

```text
NPay Mach-O
       │
       ▼
Dynamic loader (dyld)
       ├── dependent dynamic code
       ├── loading / mapping support
       └── symbol binding and initialization support
       │
       ▼
Application entry and runtime initialization
```

**Analogy:** Before a play begins, the stage crew prepares necessary props and sets. The stage crew is not the playwright (compiler), and the performance is not the script file.

**Ask:** Does dyld compile Swift source? **Answer:** No.

## Act 7 — Entering SwiftUI

### Minimal NPay app

```swift
import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

Line-by-line:

- `import SwiftUI`: makes the framework's declarations available.
- `@main`: identifies the application's entry-point type.
- `struct NPayApp: App`: defines a SwiftUI app conforming to the `App` protocol.
- `body: some Scene`: declares the app's scene content.
- `WindowGroup`: describes windows and their root content under system management.
- `ContentView()`: creates a **view description**, not an immediate bitmap or direct drawing command.

**Important:** A SwiftUI `App` value is not the OS process; `WindowGroup` is not a thread; `ContentView` is not the window server.

### Root view

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("NPay")
                .font(.largeTitle)
            Text("Your money, clearly.")
            Button("Check Balance") {
                print("Tapped")
            }
        }
        .padding()
    }
}
```

This sample is for macOS/Xcode iOS targets; it cannot render SwiftUI natively on ordinary Windows Swift installations.

## Act 8 — Scene, view, layout, first frame

### Conceptual first-frame pipeline

```text
Scene becomes active / content established
                    ↓
SwiftUI evaluates view descriptions
                    ↓
Framework reconciles relevant UI changes
                    ↓
Layout resolves size and placement
                    ↓
Graphics preparation and compositing
                    ↓
First displayed frame
```

A view's `body` may be reevaluated without the entire display being redrawn. SwiftUI declarative values are descriptions of the desired interface; the system handles presentation.

**Trainer question:** Does `ContentView()` draw pixels immediately? **Answer:** No.

## Act 9 — Launch performance

### Cold launch versus surviving-process activation

| Concern | Cold launch | Existing process foregrounded |
|---|---|---|
| New OS process | Typically yes | No, if surviving |
| Loading and initialization | Required for new process | May reuse initialized state |
| In-memory state | Must reconstruct | May survive |
| Scene activation | Yes | Yes |
| Fresh backend data | Often useful | Often useful |

Avoid promising that one path is always a specific number of milliseconds. An app may be terminated by the OS; background state does not guarantee process survival.

**Potential startup costs:** Excessive synchronous initialization, blocking the main thread, heavy work before the first useful frame, dependency loading overhead, and expensive initial UI work.

**Engineering investigation:** Measure baseline → inspect launch and time profiling in Instruments → identify actual bottleneck → optimize → measure again. Avoid generic claims such as “dyld is always the bottleneck.”

## Act 10 — End-to-end reconstruction

```text
User taps NPay icon
   ↓
SpringBoard / system launch coordination
   ↓
Existing process? ── yes ──► foreground / activate scene
   │ no
   ▼
OS creates protected process and virtual address space
   ↓
Mach-O executable and dependencies prepared (dyld)
   ↓
Swift entry-point application initialization
   ↓
SwiftUI App → Scene / WindowGroup → ContentView
   ↓
View evaluation → layout → graphics → first frame
   ↓
User sees and interacts with NPay
```

### Five misconceptions to correct

1. **“The icon directly calls Swift.”** No: system UI coordinates the action.
2. **“An app is the same as its process.”** No: installed bundle and running process differ.
3. **“A process is the same as a scene.”** No: execution context versus UI instance.
4. **“dyld compiles the app.”** No: compilation is build time; dyld handles loading duties at runtime.
5. **“SwiftUI `body` paints the screen.”** No: it describes UI, which frameworks render and present.

## Trainer-level knowledge checks

1. **Who handles the Home Screen tap?** System UI / SpringBoard and launch coordination.
2. **Can a running app have more than one scene?** Yes, supported configurations (notably iPadOS) can.
3. **Who manages virtual memory?** OS/kernel mechanisms.
4. **What does `@main` mark?** Application entry-point type.
5. **What is Mach-O?** Apple executable/object file format.
6. **What does dyld do?** Dynamic loading/runtime dependency preparation.
7. **Does `await` matter to app launch?** It can matter if asynchronous startup work is used, but async alone does not guarantee a faster first frame.
8. **What happens after process termination?** In-memory state is lost; appropriate persisted state must be restored on a new launch.
9. **Can a UI be visible yet unresponsive?** Yes, if the main thread is blocked or other critical work stalls.
10. **How do you find startup bottlenecks?** Measure with Xcode tools and Instruments rather than guess.

## Suggested live demonstration

1. Create a new iOS SwiftUI App project in Xcode.
2. Inspect the `@main` App declaration and `WindowGroup`.
3. Replace the root view with the NPay `ContentView` sample.
4. Run in iOS Simulator; observe the first screen.
5. Add a simple stateful balance display in a later lesson.
6. Explain which parts are Swift language, SwiftUI framework, OS-managed scene, and process.
7. Use Instruments or Xcode diagnostics for a first look at startup behavior, where available.

## Presentation specification for Codex

**Output:** One self-contained offline HTML file (16:9 fullscreen), with accessible keyboard navigation, reduced-motion support, presenter notes, and no external CDN dependencies.

**Visual reference:** The user's Scaler-style screenshot: white canvas, centered visual narrative, delicate outlines, inactive nodes faded, active node highlighted, smooth staged transitions. Use a tasteful iPhone mockup as a recurring anchor; avoid repeated generic card stacks.

**Recommended visual chapters:**

1. **Cinematic question:** iPhone and icon only; dramatic pause.
2. **Program versus process:** Two states, side-by-side, animated conversion metaphor.
3. **Platform X-ray:** Peel back phone to reveal responsibility layers.
4. **SpringBoard handoff:** Animated request traveling from Home Screen into system coordination.
5. **Branching launch:** Cold vs existing process; audience predicts which path occurs.
6. **Process assembly:** Virtual memory, threads, and sandbox appear one by one.
7. **Mach-O close-up:** From Swift source to binary file layout.
8. **dyld dependency network:** Dependencies and initialization progressively illuminated.
9. **Code-to-runtime:** Highlight `@main`, `App`, `WindowGroup`, `ContentView` while matching visual elements activate.
10. **Scene and first frame:** UI tree resolves into a visible NPay screen.
11. **Performance detective:** Compare a healthy startup with unnecessary synchronous work.
12. **Reconstruction:** Full animated story; learners narrate the journey.

### Mandatory presenter notes per scene

- **SAY:** Natural explanation, technically accurate, 60–120 seconds when needed.
- **ASK:** One prediction or diagnostic question.
- **EXPECT:** Correct answer and likely misconception.
- **CONNECT:** One transition sentence to the next scene.

### Acceptance criteria

- Every substantive point in this guide is covered somewhere in the finished deck or its notes.
- No false precision about undocumented internal iOS behavior.
- No overlap/clipping at 1920×1080 or 1366×768; test fullscreen.
- Animations convey causality, not decoration.
- All Swift snippets compile in an appropriate Xcode iOS project.
- No mandatory internet access for presenting.
- Trainer can explain the entire launch path without needing external notes.

## Final teaching script

“An app icon is only the visible doorway. The system receives the user's action and decides whether to activate an existing app process or start a new one. For a new launch, iOS establishes a protected process environment. The executable and its dependencies are prepared, Swift application entry executes, SwiftUI establishes a scene and root view, and the graphics pipeline eventually presents the first frame. From one tap, we have crossed the boundaries between user experience, system execution, compiled code, framework abstractions and display rendering.”

**Bridge to Lesson 0.2:** “We now know how NPay comes alive. Next, how should we organize the code inside that running app—views, state, services and data?”


---
# Extended teaching manuscript and presentation production brief

This is a comprehensive reconstructed lesson, not a verbatim transcript. The lesson's single narrative is: **one user taps NPay, and we reveal everything needed to present the first screen**. Build a visual story, not a glossary.

## Detailed instructor sequence

### 1. Installed app, process, scene: three separate entities

Start by showing an iPhone with NPay installed. Ask whether NPay currently has a running process. Explain that an installed bundle contains executable code, metadata, and resources, while a process is an OS-managed execution environment. A scene is an instance of UI managed through the application and system lifecycle. A process may host more than one scene. Use the analogy of a recipe (program), working kitchen (process), and dining room (scene). The analogy is limited: the scene is not a separate process.

**Say:** “The icon is a doorway. The program exists on disk even when nothing is executing.”

**Ask:** “If an app is installed but never opened, must it have a running process?” **Expected:** No.

**Visual:** Split disk/bundle and process/scene. Reveal the latter only after the launch decision.

### 2. Platform architecture: who is responsible?

The app's Swift code relies on SwiftUI, UIKit, Foundation, Security and other frameworks. System services coordinate app launch and lifecycle. Darwin/XNU underpins processes, scheduling, memory and security enforcement. Hardware executes machine instructions. This is a conceptual responsibility diagram, not a literal synchronous stack of calls.

**Ask:** “Who schedules threads: SwiftUI or the OS?” **Expected:** OS scheduling mechanisms.

**Visual:** An exploded layered iPhone. Keep the current layer highlighted while the others are faded.

### 3. The tap and SpringBoard

When the user taps the Home Screen icon, system UI receives that interaction. SpringBoard is associated with Home Screen and app switching. The system coordinates a launch or activation request. Do not invent private daemon names, exact IPC hops or undocumented ordering. NPay's own SwiftUI Button actions are not involved in tapping its Home Screen icon.

**Ask:** “Does the tap immediately call `NPayApp.body`?” **Expected:** No.

**Visual:** Animated tap ripple, a request token leaving the Home Screen and entering a system launch coordinator.

### 4. Launch versus activation

If no usable process survives, the OS starts a new process. If a process survives, the system may foreground or reactivate its UI without repeating the complete cold-launch path. A suspended process retains memory but is not executing ordinary work. Process survival is never guaranteed.

**Ask:** “Will returning after ten minutes always be a warm activation?” **Expected:** No.

**Visual:** A fork that the audience selects. The two paths merge at the visible dashboard.

### 5. Process creation and virtual memory

Explain process identity, virtual address space, executable mappings, shared libraries, static storage, heap, thread stacks, open resources and sandbox restrictions. Virtual memory is an abstraction: it is not a promise that the entire executable has been copied into physical RAM. Threads are execution contexts inside the process. A Swift Task is not synonymous with a thread.

**Ask:** “Does every class live on the heap and every struct on the stack?” **Expected:** No, that is not a reliable Swift language rule.

**Visual:** Exploded process diagram: mappings, heap, stack, threads, OS resources and a surrounding sandbox boundary.

### 6. Executable format and dynamic loading

Swift source is compiled and linked before normal native iOS execution. Mach-O is the executable/object-file format, with headers, load commands and segments/sections. dyld is the dynamic loader that prepares required dynamic code and binding-related work. Some code may be mapped from shared caches; avoid simplistic claims that every library is fully copied into RAM. The compiler and dyld have different responsibilities.

**Ask:** “Does dyld compile `.swift` source when the user taps?” **Expected:** No.

**Visual:** Source → compiler/linker → Mach-O; then zoom into runtime loader and dependency graph.

### 7. Swift application entry

In a SwiftUI app, `@main` identifies an entry-point type conforming to `App`. Its `body` provides scene definitions. `WindowGroup` supplies root content for managed windows. These are application abstractions executed within an OS-managed process. Do not say that `@main` creates the OS process or that `App.init` is necessarily the first machine instruction.

```swift
import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            DashboardView()
        }
    }
}
```

**Ask:** “Does `DashboardView()` draw pixels?” **Expected:** No; it creates a SwiftUI view value.

**Visual:** Highlight one line at a time and synchronize with a diagram of app, scene and root view.

### 8. Scene and view hierarchy

A scene is a managed UI instance, distinct from a process. A typical iPhone app often has one main scene; multiple windows are especially relevant on iPadOS. SwiftUI view values describe UI. Views compose into a tree. View identity and state matter for subsequent updates.

```swift
struct DashboardView: View {
    var body: some View {
        VStack(spacing: 16) {
            Text("NPay").font(.largeTitle)
            Text("Available balance")
            Text("₹25,000").font(.title)
            Button("Check Balance") {
                print("Tapped")
            }
        }
        .padding()
    }
}
```

**Ask:** “Is `body` an imperative paint method?” **Expected:** No.

**Visual:** Swift source on left; hierarchical tree assembled on right; iPhone interface shown last.

### 9. First frame and responsiveness

SwiftUI evaluates relevant view descriptions and coordinates updates. Layout determines geometry. Graphics and compositing contribute to presented frames. The exact private pipeline varies by OS and framework version. Re-evaluating `body` does not necessarily redraw the entire screen. First visible frame and fully interactive state are not necessarily the same milestone.

**Ask:** “Can the first screen be visible but unresponsive?” **Expected:** Yes, if main-thread work stalls interactions.

**Visual:** View tree → layout boxes → graphical surface → phone display. Add a separate responsiveness indicator.

### 10. Performance investigation

Startup cost can come from loading dependencies, expensive initialization, synchronous main-thread work, and first-frame preparation. Teach hypothesis → measurement → change → remeasurement. Use Instruments and Xcode diagnostics appropriate to the installed toolchain. Do not invent benchmark numbers or imply one bottleneck applies to all apps.

**Ask:** “Should we optimize dyld first when startup is slow?” **Expected:** Not without measurement.

**Visual:** Two timing lanes, one showing blocked initialization and one deferring nonessential work.

## NPay demo: minimal runnable app

The following example requires an iOS app target on macOS with Xcode. It is not executable as a SwiftUI app on Windows.

```swift
import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            DashboardView()
        }
    }
}

struct DashboardView: View {
    @State private var balanceText = "₹25,000"

    var body: some View {
        VStack(spacing: 20) {
            Text("NPay").font(.largeTitle.bold())
            Text("Available balance")
            Text(balanceText).font(.title)
            Button("Refresh balance") {
                balanceText = "₹25,000"
            }
        }
        .padding()
    }
}
```

The balance is intentionally hardcoded; this is a startup and view-composition demonstration, not a networking or banking implementation.

## Hands-on exercises

**Exercise A — Responsibility map.** Draw distinct entities for Home Screen system UI, NPay process, scene, SwiftUI view, kernel and hardware. Explain each boundary.

**Exercise B — Cold versus warm.** Draw two execution paths and explain which stages may be reused. Explain why process survival is not guaranteed.

**Exercise C — Source to binary.** On macOS, inspect a known built executable using `file` and `otool -l`. Verify its path from Xcode build products; do not guess bundle paths.

**Exercise D — First frame diagnosis.** Given a blank screen during launch, propose at least three hypotheses and corresponding observations or measurements. Avoid claiming the cause before measuring.

## Audience question bank with expected answers

1. Is SpringBoard inside our app? **No.**
2. Does every tap create a new PID? **No.**
3. Is a scene the same as a process? **No.**
4. Does virtual memory mean exclusive physical RAM? **No.**
5. Does SwiftUI schedule OS threads? **No.**
6. Does iOS interpret `.swift` source on each launch? **No.**
7. Is dyld the Swift compiler? **No.**
8. Does `@main` create the OS process? **No.**
9. Is `ContentView()` a drawing command? **No.**
10. Does `body` reevaluation always redraw all pixels? **No.**
11. Can one process have multiple scenes? **Yes, on supported platforms/configurations.**
12. Does code signing guarantee absence of vulnerabilities? **No.**
13. Can a sandboxed app share any data? **Yes, through authorized mechanisms.**
14. Is the first frame proof of full responsiveness? **No.**
15. Should we optimize startup without profiling? **No.**

## Visual storyboard: 36 scenes

| Scene | Presentation moment | Teaching animation |
|---|---|---|
| 01 | One tap | iPhone hero and tap ripple |
| 02 | A question | Prediction pause |
| 03 | Installed bundle | Disk and files cutaway |
| 04 | Running process | Separate execution environment |
| 05 | Scene identity | UI versus process comparison |
| 06 | Hardware | Foundation layer reveal |
| 07 | Kernel | Process scheduling reveal |
| 08 | System services | Launch coordination reveal |
| 09 | Frameworks | Developer API layer |
| 10 | SpringBoard | Home Screen spotlight |
| 11 | Request path | Animated launch request |
| 12 | Launch fork | Cold/warm choice |
| 13 | Warm activation | Existing process timeline |
| 14 | Cold launch | New process timeline |
| 15 | Process ID | Execution container |
| 16 | Virtual memory | Mapped address-space regions |
| 17 | Threads | Main and worker lanes |
| 18 | Sandbox | Security boundary |
| 19 | Build-time compilation | Source-to-machine-code transformation |
| 20 | Mach-O anatomy | Binary cutaway |
| 21 | dyld | Loader reveal |
| 22 | Dependencies | Library graph |
| 23 | Initialization | Critical-path timing |
| 24 | @main | Code highlight |
| 25 | App protocol | Scene definition |
| 26 | WindowGroup | Window creation abstraction |
| 27 | Scene versus process | Side-by-side model |
| 28 | ContentView | View value reveal |
| 29 | View tree | Incremental hierarchy |
| 30 | State | State-to-UI relationship |
| 31 | Reconciliation | Selective update concept |
| 32 | Layout | Geometry reveal |
| 33 | Graphics | Frame preparation |
| 34 | First frame | Phone screen appears |
| 35 | Performance mystery | Evidence-based debugging |
| 36 | Reconstruction | 90-second end-to-end explanation |

## HTML deck production contract for Codex

- Source of truth: this Markdown file; preserve its technical concepts, code and Q&A.
- Design: fullscreen 16:9, Scaler-inspired visual storytelling, predominantly white, restrained accent colors, clear typography.
- Vary slide types: hero, question, diagram, timeline, code trace, system cutaway, comparison, debugging exercise and recap.
- Never use the same generic stack of cards for every slide.
- Reveal each mechanism only when the audience needs it; show arrows and data/control movement, not decorative motion.
- Provide speaker notes per scene: **Say**, **Ask**, **Expected**, **Misconception**, **Transition**.
- Include keyboard controls, full-screen mode, presenter notes, reduced-motion support and offline assets.
- Test at 1920×1080, 1440×900 and 1366×768; check overflow, contrast and animation sequencing.
- Technical diagrams of undocumented iOS internals must be labeled conceptual; do not invent private IPC call chains.
- Use actual executable Swift snippets when the slide claims code is runnable; label Xcode/macOS requirements.
- Build and review the opening scenes before expanding all 36. Visual quality and teachability matter more than slide count.

## Acceptance checklist

- [ ] A learner can distinguish installed app, process and scene.
- [ ] A learner can narrate launch/activation without claiming every tap starts a process.
- [ ] A learner can explain virtual memory and the role of threads.
- [ ] A learner can distinguish Swift compiler, Mach-O and dyld.
- [ ] A learner can explain @main, App, WindowGroup and view values.
- [ ] A learner can trace a conceptual path from view description to first frame.
- [ ] A learner can identify why first-frame performance and interactivity differ.
- [ ] Every scene has trainer notes and a meaningful learner question.
- [ ] The deck works offline in fullscreen and has no clipping.

## Final trainer challenge

“Starting from the moment I tap the NPay icon on the Home Screen, explain what the system owns, what our Swift code owns, what happens only on a new process launch, and how a view description eventually becomes the first visible frame.”

A correct explanation distinguishes **system UI → launch coordination → process (if required) → executable loading → Swift app entry → scene → view evaluation/layout/rendering → presented frame**, without treating this as a guaranteed literal trace of private internals.
