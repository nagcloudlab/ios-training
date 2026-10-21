# Lesson 0.2 — iOS App Architecture: Who Does What?

*iOS Architecture Mastery · No coding required for this lesson*

> Lesson text as shared; the deck (`index.html`) uses **only this text**. The running example app is **NPay**.
> The original walkthrough shows only step 1 of 8; steps 2–8 below were written to follow the five
> responsibilities (marked *authored*). The MVVM slide shows the three short code snippets below.

In Lesson 0.1, we learned how iOS starts an application. Now let's understand who manages the application after it starts.

Imagine we're building a banking app. The user opens it, checks their balance, and transfers money.
Who is responsible for displaying the screen, handling a button tap, communicating with the bank, and storing information?

## 1. Five important responsibilities

User taps "Check Balance" →

1. **View — SwiftUI**: displays balance and receives interaction
2. **ViewModel**: manages screen state and coordinates actions
3. **Service / Repository**: loads data and hides implementation details
4. **Network**: bank server
5. **Storage**: local database

This is an example of a layered MVVM-style application architecture, not a structure that iOS forces every app to use.

## 2. Understand the difference between iOS and your app architecture

| iOS platform architecture | Application architecture |
|---|---|
| Operating system | View |
| Kernel and processes | ViewModel |
| System frameworks | Model |
| Hardware access | Services and repositories |
| App lifecycle | Business logic and data flow |

iOS architecture explains how Apple manages apps and system resources. Application architecture explains how developers organize code inside their apps. They are related, but they are not the same thing.

## 3. What happens when the user taps "Check Balance"?

The request moves down through the application and the result moves back up.

| Step | Who | What happens |
|---|---|---|
| 1 | User | User taps button: the user initiates an action on the balance screen. |
| 2 | View | *Authored:* the SwiftUI view calls the ViewModel, for example `loadBalance()`. |
| 3 | ViewModel | *Authored:* marks the screen as loading and asks the service for the balance. |
| 4 | Service | *Authored:* decides where the data comes from and calls the network. |
| 5 | Bank server | *Authored:* checks the request and returns the balance. |
| 6 | Service | *Authored:* decodes the response, may save a copy to local storage, returns a model. |
| 7 | ViewModel | *Authored:* turns the model into what the screen needs, such as the balance text. |
| 8 | View | *Authored:* SwiftUI re-renders; the user sees the new balance. |

## 4. How SwiftUI differs from traditional UI programming

Traditional UIKit programming often involves explicitly changing interface properties. SwiftUI uses a declarative approach: **the UI is a function of its state.**

| UIKit style | SwiftUI style |
|---|---|
| 1. Create UILabel | 1. Declare a view |
| 2. Set its text | 2. Connect it to state |
| 3. Update it manually when needed | 3. Change state |
| *Imperative:* tell the interface what to change. | *Declarative:* describe the desired result. |

**State → interface demonstration** (on the slide): Available balance ₹12,500, with "Simulate ₹1,000 deposit" and "Reset balance"; the current state `balance = …` updates alongside. Local interactive simulation only; no real banking request or Swift runtime.

When the balance state changes, the displayed amount changes. That is the central mental model behind SwiftUI.

## 5. Where does MVVM fit?

MVVM stands for Model–View–ViewModel.

- **Model**: what the data means
- **ViewModel**: what the screen needs
- **View**: what the user sees

```swift
struct Account {
    let id: String
    let balance: Decimal
}
```

```swift
@Observable
class AccountViewModel {
    var balanceText = "₹12,500"
}
```

```swift
struct BalanceView: View {
    var model: AccountViewModel

    var body: some View {
        Text(model.balanceText)
    }
}
```

These are simplified teaching examples. A production app would also address dependency injection, currency formatting, error handling, and secure data access.

## 6. Knowledge check

1. **Who creates and manages an iOS application's process?** The operating system. Process creation and management are OS responsibilities; SwiftUI operates within the application process.
2. **What should happen when observable SwiftUI state changes?** Update the affected UI. SwiftUI re-evaluates relevant view descriptions and manages the necessary interface updates.
3. **Which component normally coordinates a balance-screen loading state in MVVM?** The ViewModel. It commonly owns presentation state and coordinates loading through a service.

## What comes next

The next lesson goes one layer deeper into the iOS application lifecycle:

- App process versus scene
- Foreground, background, and suspension
- What happens when the user presses Home
- Why iOS may terminate apps under memory pressure
- Cold launch versus warm activation
- SwiftUI lifecycle versus UIKit AppDelegate and SceneDelegate

## Deck changes after the Unit 00 audit

The text above is unchanged. The deck now differs from it as follows.

**Corrections and consistency (NPay canon)**
- "Check Balance" is now **"Refresh balance"** everywhere (hero, outcomes, Part 3 walkthrough; the view calls `refresh()`).
- Part 5 code uses the unit's canonical types: `Balance` with `balanceMinor: Int64` (whole paise), `@MainActor @Observable final class DashboardViewModel` that formats the amount with `.formatted(.currency(code: "INR"))`, and `DashboardView` owning it with `@State`. The state demo starts at ₹25,000.
- "No coding" is kept: the Part 5 live demo uses a prepared project that students watch; the slide says the code is "to read rather than write".
- Part 4 adds the idea this lesson owns: a view's `body` is a *description* of the screen that SwiftUI reads again when its state changes.

**Authored additions (flagged)**
- "Where we are" slide after the outcomes: the shared NPay architecture map (View, ViewModel, Service, Model lit), with Last time (0.1) / Today.
- One-line pointer on the MVVM slide: Unit 04 covers MVVM in depth (4.2) and dependency injection (4.5).
- Recap slide (map + three points) before the review.
- Review grows from 3 to 5 questions: two multiple-choice items (where ₹ formatting belongs; spaced review from 0.1: what runs first at launch).
- "Where this goes next" slide: 2.1, 2.5, 3.2, 4.2, 4.5.
- Title slide question reworded to "How do NPay's components communicate?" (the course plan's central question for 0.2).
- Lab: sort ten NPay job cards into View / ViewModel / Service / Model (answers in the speaker notes).
- End slide: "Next: Lesson 0.3 — iOS Application Lifecycle Deep Dive".
