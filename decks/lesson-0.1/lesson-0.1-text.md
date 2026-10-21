# Lesson 0.1 — iOS Architecture & App Startup

*iOS Developer + Trainer Mastery · Foundation Series · Unit 00 · Lesson 0.1*

> **Study companion for the slide deck** (`index.html` in this folder). It follows the deck part by part.
> It is based on the original lesson text, extended with everything the slides and speaker notes add
> (seven-step launch, SpringBoard, compilation, dyld, first frame, performance, review answers).
> The running example app is **NPay**, a fictional SwiftUI banking app.

Our first question is deceptively simple:

**What actually happens inside an iPhone when a user taps an app icon?**

By the end of this lesson you should be able to explain the journey from tapping an icon to seeing the first SwiftUI screen, including the operating system, process creation, application lifecycle and UI rendering.

### Outcomes

1. Distinguish an installed **bundle**, a running **process** and a **scene**.
2. Explain the **platform layers** and the boundaries between them.
3. Narrate a **tap** all the way to the **first frame**.
4. Explain **launch vs activation** and the **app lifecycle**.
5. Place **Mach-O**, **dyld**, `@main`, `WindowGroup` and `body` correctly.
6. Spot **startup performance** risks and plan how to measure them.

---

## Part 1 — The big picture

### How an iOS app works

```
User interacts with iPhone      tap, swipe, type, navigate
        ↓
SwiftUI / UIKit                 user interface and event handling
        ↓
Application logic (Swift)       business rules, models, state and services
        ↓
Storage (SwiftData) · Network (URLSession) · Device (iOS APIs)
```

Simplified conceptual architecture, not a literal iOS system call stack. In NPay terms: the user taps Send, SwiftUI handles the tap, our Swift logic validates the transfer, URLSession talks to the bank, SwiftData can cache recent activity, and device APIs provide features such as biometrics. We write the application logic and the views; storage, networking and device features are Apple frameworks our code calls.

### Installed app ≠ running process ≠ scene

| | Where | What |
|---|---|---|
| **App bundle** | On disk | Signed executable, resources and metadata. Exists even when nothing runs. |
| **Process** | In memory | OS-managed execution: virtual address space and threads. Created only when needed. |
| **Scene** | On screen | A system-managed UI instance. Lives inside a process; one process can host several (notably on iPad). |

A **recipe book** (bundle) is not a **working kitchen** (process). The **dining room** (scene) is where the user interacts. An installed app can have zero running processes.

### Think of an iPhone as a hotel

- **iOS** is the hotel management system.
- **Your app** is a guest occupying a room.
- **The kernel** controls critical resources and access.
- **System services** provide shared facilities.
- **Frameworks** give your app approved ways to use those facilities.
- **The sandbox** prevents one guest from entering another guest's room.

The important idea: **your app does not own the iPhone. It runs under the operating system's supervision.**

### Conceptual iOS architecture

| Layer | Contents |
|---|---|
| Your iOS app | Swift code, SwiftUI screens, business logic |
| Apple frameworks | SwiftUI, UIKit, Foundation, Core Location, … |
| iOS system services | App lifecycle, security, notifications, graphics |
| Darwin / XNU kernel | Processes, threads, virtual memory, scheduling |
| Apple hardware | CPU, GPU, RAM, storage, sensors |

Five layers: your app on top of four platform layers. This is a **responsibility map**, not a rigid call chain; real frameworks and services communicate through several layers rather than one straight path.

**Ask:** Can my Swift app directly read another app's files, or freely access the camera hardware?
**Answer:** No. Apps operate within security restrictions and must use approved APIs and permissions. The operating system mediates access.

---

## Part 2 — What happens when you tap an app icon?

Imagine tapping NPay. Before the first screen appears, the system must set up a **running application environment**.

### App launch, simplified: seven steps

| Step | | What happens |
|---|---|---|
| 1 | **Tap** | The touch reaches the Home Screen, which is system UI (SpringBoard). |
| 2 | **Launch or activate?** | The system decides: start a new process, or bring an existing one forward. |
| 3 | **Process created** | The OS creates the process: identity, virtual memory, a main thread, the sandbox. |
| 4 | **Executable and libraries load** | The dynamic loader, dyld, prepares the executable and required dynamic libraries. |
| 5 | **Swift entry point** | The runtime is ready and Swift's entry point starts your App type. |
| 6 | **Scene created** | iOS creates a scene, and WindowGroup supplies the root view. |
| 7 | **First frame on screen** | SwiftUI evaluates the views, lays them out, and the first frame is displayed. |

Not always a new process: if NPay is already running in the background, iOS may simply bring it to the foreground. Launching a process and activating an existing app are different operations, which matters later for lifecycle management and state restoration.

### SpringBoard handles the tap

1. **A system process.** Part of iOS; none of NPay's code runs here. SpringBoard starts when the iPhone boots. The Home Screen is SpringBoard's interface; the NPay icon is just an image from NPay's bundle that SpringBoard draws. Nothing in our Swift code, not even `@main`, can react to the tap itself.
2. **Owns the Home Screen.** Draws icons and badges and runs the app switcher. An app can set a badge number through notification APIs, but SpringBoard draws it. Switcher cards are snapshots, so an app is not necessarily running while you see its card.
3. **Coordinates the launch.** On a tap it does not start NPay itself; it asks the system to open the app. Meanwhile the system plays the icon animation and shows the app's **launch screen** (a static placeholder) until the first frame is ready.

The exact private system components and IPC hops behind this are undocumented and change between iOS versions, so the diagram stays conceptual ("launch coordinator").

### Cold launch vs warm activation

```
User taps NPay → Process alive?
   YES → Foreground: reuse the process              ─┐
   NO  → Create process → Load + init (dyld)        ─┴→ UI available
```

If the process is still alive, the system reuses it; if not, it builds everything again. A **suspended** process keeps its memory but does no ordinary work, and the OS can end it at any time. So returning to NPay after ten minutes is **not** guaranteed to be a warm activation.

---

## Part 3 — What is an app process?

On disk, an app is **executable code and resources**. A **process** is a running instance of it. The OS establishes:

- Process identity and resources
- A **virtual address space** with mapped regions
- At least one execution **thread**
- **Sandbox** and code-signing enforcement

### Simplified process memory

| Region | Holds |
|---|---|
| Code / text | Machine instructions, mapped executable code |
| Global and static data | Global variables and static storage |
| Heap | Dynamically allocated objects and storage |
| Thread stacks | Function call frames and local execution state |

Illustrative regions, not the actual address order or a complete memory map. Virtual addresses are not physical RAM addresses, and mapping an executable does not mean it was all copied into RAM. **Swift value types are not guaranteed to live on the stack**: "struct on the stack, class on the heap" is not a reliable rule. A Swift `Task` is not the same thing as a thread. Code signing proves origin and integrity, not that the app is free of vulnerabilities; a sandboxed app can share data only through authorized mechanisms such as app groups or the share sheet.

### Program, process, thread

| Concept | Meaning |
|---|---|
| Program | Code stored on disk |
| Process | Running instance of a program |
| Thread | Execution path inside a process |
| Main thread | Handles the app's primary UI events |
| Heap | Dynamic memory storage |
| Stack | Execution storage for one thread |

A restaurant's **recipe book** is the program on disk. **Opening the restaurant**, hiring staff and preparing the kitchen is starting a process. The **workers** are threads doing tasks inside it. Memory management, ARC and Swift concurrency come in later lessons.

---

## Part 4 — Where does your Swift code begin?

### The compilation pipeline (all on your Mac, at build time)

```
.swift source → Frontend → SIL → LLVM → Link + sign → Mach-O executable (ships in the bundle)
```

1. **`.swift` source** — plain text you write. The iPhone never sees it.
2. **Frontend: parse + type check** — builds a structured tree of the program, works out every type, infers the ones you didn't write, and resolves which function each call means. Most compile errors come from here.
3. **SIL (Swift Intermediate Language)** — a Swift-aware internal form. Swift-specific checks and optimizations run here, such as "used before initialized" errors, removing unnecessary retain/release calls (ARC optimization) and specializing generic code.
4. **LLVM: machine code** — lowered to LLVM's general-purpose form, optimized, and turned into ARM64 machine instructions; one object file (`.o`) per source file.
5. **Link + sign** — the linker combines the object files into **one executable**, connects calls between your files, and records which system libraries the app needs (SwiftUI, Foundation, the Swift runtime) without copying them in. The executable is then cryptographically signed; iOS checks the signature at launch.
6. **Mach-O** — the executable format for Apple platforms, placed in the app bundle.

**Inside a Mach-O file**

- **Headers + load commands** — what kind of file and which CPU; instructions for the loader: which libraries to load, where the code starts, where the signature is.
- **Segments and sections** — regions by purpose: `__TEXT` (read-only machine code), `__DATA` (writable globals), `__LINKEDIT` (symbol and linking information); each holds smaller sections such as `__text`.
- **Metadata for loading** — dyld reads it at launch to know what to map and connect. (Exercise C shows it with `otool -l`.)

**Remember:** `.swift` source is not interpreted on launch. It was compiled ahead of time, which is a big reason native apps start fast.

### dyld: the dynamic loader

```
NPay Mach-O → dyld → load dependencies (SwiftUI, Foundation, libswiftCore)
            → map + bind (resolve symbols) → app entry (initializers, then @main)
```

dyld prepares executable images and their dependencies at runtime. System frameworks come from the **dyld shared cache**, prepared ahead of time by Apple, which is why they load quickly; your own embedded frameworks do not get that benefit.

Before a play begins, the **stage crew** (dyld) prepares props and sets. The crew is not the **playwright** (compiler).

### The `@main` declaration

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

Read it in four stages:

1. **`@main`** — identifies the entry-point type. Swift synthesizes the startup entry mechanism.
2. **`struct NPayApp: App`** — defines the app with SwiftUI's App protocol. SwiftUI manages lifecycle integration.
3. **`var body: some Scene`** — declares the scenes: managed portions of the app's interface.
4. **`WindowGroup { DashboardView() }`** — windows holding the root view. iOS manages scene creation and presentation.

`DashboardView()` is not a command to draw pixels immediately; it creates a view value describing the interface. `App` is not the OS process, and `WindowGroup` is not a thread. `@main` does not create the process (it already exists), and `App.init` is not the first machine instruction: dyld, runtime setup and initializers run before it.

---

## Part 5 — How does SwiftUI produce the screen?

### The view is a description, not a drawing

```swift
struct DashboardView: View {
    @State private var balanceText = "₹25,000"

    var body: some View {
        VStack(spacing: 20) {
            Text("NPay")
                .font(.largeTitle.bold())
            Text("Available balance")
            Text(balanceText).font(.title)
            Button("Refresh balance") {
                balanceText = "₹25,480"
            }
        }
        .padding()
    }
}
```

**Declarative:** you describe *what* the interface should look like for the current state; the framework manages *how* to update the screen. If you know React or Jetpack Compose, the idea is the same.

`@State` creates a source of truth. Tap **Refresh** and `balanceText` changes: SwiftUI re-evaluates `body`, then updates only what changed on screen.

### From view values to a screen

```
WindowGroup
└── DashboardView
    └── VStack
        ├── Text("NPay")
        ├── Text("Available balance")
        ├── Text(balanceText)
        └── Button("Refresh balance")
```

Views compose into a tree; the frameworks render it. `body` is not an imperative paint method: it returns a tree of view values, and SwiftUI decides what to show and update. A typical iPhone app has one main scene; on iPadOS one process can show several scenes, each with its own view tree.

### The first-frame journey

```
Scene active → Evaluate view bodies → Reconcile (what changed) → Layout (size & place)
             → Graphics (composite) → First frame on screen
```

`body` may be re-evaluated without redrawing the entire screen. The first frame can be visible while the main thread is still busy with heavy synchronous work; until it finishes, taps wait in line. **First visible frame and fully interactive are not the same milestone.**

---

## Part 6 — The application lifecycle

An iOS app doesn't simply start, run forever and exit. The system manages its execution based on user activity and available resources.

| State | Meaning |
|---|---|
| Not running | No process |
| Active | Receiving user interaction |
| Inactive | Foreground, temporarily not receiving events |
| Background | Not foreground; limited permitted execution |
| Suspended | Process kept in memory, code not executing |

A common path, not every possible transition. **iOS can terminate a suspended app**, and scene lifecycle states differ from process execution states.

### Observing the scene phase

```swift
import SwiftUI

@main
struct NPayApp: App {
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            DashboardView()
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            switch newPhase {
            case .active:
                print("Scene active")
            case .inactive:
                print("Scene inactive")
            case .background:
                print("Scene background")
            @unknown default:
                break
            }
        }
    }
}
```

- `.active` — in front and receiving interaction
- `.inactive` — visible, temporarily not receiving events
- `.background` — not visible: save data, pause work

`@unknown default` keeps the switch future-proof if Apple adds a phase.

---

## Part 7 — Practice

### Lab: observe startup and lifecycle

On your Mac:

1. In Xcode, create an iOS App project named **LifecycleLab**.
2. Choose **SwiftUI** and **Swift**.
3. Replace the generated entry point with the scene-phase example, keeping your project's app type name.
4. Run it in the iPhone Simulator.
5. Watch the debug console while moving between the app and the Home Screen.

| Action | What to observe |
|---|---|
| Launch the app | Initial UI appears; the scene typically becomes active |
| Open Notification Center | The scene may become inactive |

> The original text ends at this table; further experiment rows were not provided.

### Hands-on exercises

- **A: Responsibility map** — draw Home Screen system UI, the NPay process, its scene, a SwiftUI view, the kernel and hardware. Explain every boundary.
- **B: Cold vs warm** — draw both launch paths. Mark which stages a warm activation can reuse, and explain why survival is not guaranteed.
- **C: Source to binary** — on a Mac, find your built app in Xcode's build products and run `file` and `otool -l` on the executable. Use the real path; don't guess bundle paths.
- **D: Blank screen** — the app shows a blank screen at launch. Write three hypotheses and the measurement that would test each one.

---

## Wrap-up — Putting it together

### What a cold launch costs

| Concern | Cold launch | Warm activation |
|---|---|---|
| New OS process | Typically yes | No (if surviving) |
| Loading & init | Full setup | May reuse state |
| In-memory state | Must rebuild | May survive |
| Scene activation | Yes | Yes |
| Fresh backend data | Often useful | Often useful |

Startup cost sources: excessive synchronous init, blocking the main thread, heavy work before the first frame, dependency loading overhead, expensive initial UI work. In-memory state is lost when the OS ends a process, so anything that matters must be persisted and restored. `await` alone does not make launch faster.

### Measure, don't guess

Measure (time the launch) → Profile (Instruments trace) → Identify (find the real cost) → Optimize (change one thing) → re-measure. "dyld is always the bottleneck" is a misconception: every app is different. Hypothesis → measurement → change → remeasurement; never optimize without data.

### From tap to first frame

```
YOU   | SYSTEM UI   | KERNEL  | LOADER | YOUR CODE      | RENDER
Tap   | SpringBoard | Process | dyld   | @main → Views  | Frame
```

One tap crosses **five ownership boundaries** before the first frame appears. Only `@main` and the views belong to NPay's code.

### Five things that are not true

| Myth | Reality |
|---|---|
| "The icon directly calls Swift." | System UI coordinates the launch first. |
| "An app is the same as its process." | The bundle is on disk; a process is created on demand. |
| "A process is the same as a scene." | Execution context vs UI instance. |
| "dyld compiles the app." | Compilation is build time; dyld loads at runtime. |
| "SwiftUI `body` paints the screen." | It describes UI; the frameworks render it. |

### Check your understanding

1. **Which layer schedules threads?** The kernel: Darwin/XNU handles scheduling and memory.
2. **Can your app read another app's files or freely access the camera?** No. Approved APIs and permissions only; the OS mediates.
3. **Does the tap immediately call `NPayApp.body`?** No. Your Swift code hasn't started yet.
4. **Will returning after 10 minutes always be a warm activation?** No. The OS may have ended the process.
5. **Is a suspended app running code?** No. The process is kept, code is not executing, and iOS may terminate it.
6. **Is a process the same as a thread?** No. The process is the container; threads are workers inside it.
7. **Is Mach-O the Swift programming language?** No. It is a binary format; Swift compiles into it.
8. **Does dyld compile Swift source?** No. Compilation is build time; dyld loads at runtime.
9. **Does `DashboardView()` draw pixels?** No. It creates a view value; the framework renders it.
10. **Is `body` an imperative paint method?** No. It returns a tree of view values.
11. **Can the first screen be visible but unresponsive?** Yes. If the main thread is blocked, taps wait in line.

### Your challenge

"Starting from the moment I tap the NPay icon, explain what the **system** owns, what our **Swift code** owns, what happens only on a **new process launch**, and how a view description becomes the **first visible frame**."

- **System owns:** SpringBoard, process creation, sandbox, scheduling
- **Your code owns:** `@main`, `App`, `WindowGroup`, `DashboardView`, `@State`
- **The bridge:** evaluate → layout → graphics → first frame

**Next:** how should we organize the code inside the running app — views, state, services and data? (Lesson 0.2)
