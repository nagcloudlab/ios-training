# Lesson 0.10 — The Complete iOS Architecture: End to End

*iOS Architecture Mastery · Foundation Series Finale*

> Lesson text as shared; the deck (`index.html`) uses only this text. **PocketBank is renamed NPay**
> (`NPayApp`, `api.npay.example`). "Trainer" material became speaker notes; section 14's teaching-sequence table
> became the "Ten connected lessons" slide (shown as a course map). **Authored for the deck** (flagged): startup
> steps 2–7 (the text shows only step 1); the Check Balance screen states; lifecycle states other than "Active";
> the cold-launch return scenario (the text shows only "process survived"); architecture-review questions 2–5 and
> all review answers (the text shows only question 1 of 5); the "Your challenge" responsibility cards.

The goal: understand what happens, why, who is responsible, and how it all fits together.

## The story: one day with NPay
1. User taps the NPay icon 2. iOS launches the app 3. SwiftUI shows the dashboard 4. User taps Check Balance 5. App contacts the bank securely 6. Server returns ₹25,000 7. Screen updates, appropriate data saved 8. User switches apps 9. iOS suspends NPay and may terminate it 10. User returns.

## 1. The complete architecture
NPay app process: SwiftUI View (screens, navigation, interaction) · ViewModel / presentation state (loading, balance, errors, actions) · application services / repository · networking (URLSession) and storage (SwiftData, files, Keychain). Below: Apple frameworks & iOS services · Darwin/XNU kernel · Apple hardware. The bank backend (authentication, authorization, accounts, transactions) is a separate system. **Application architecture** (how we organize code) vs **platform architecture** (how iOS provides execution, security, frameworks, hardware): do not confuse them.

## 2. Stage one — launch
1. SpringBoard handles the tap and requests launch or activation. *Authored:* launch or activate? → process created → dyld loads code → Swift entry point → scene created → dashboard on screen. **Who owns the process?** The operating system; SwiftUI provides app and scene abstractions inside it.

## 3. Stage two — SwiftUI builds the dashboard
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
@main NPayApp → App protocol → WindowGroup → DashboardView. `DashboardView()` creates a view value; it does not draw pixels.

## 4. Stage three — Check Balance
Touch event reaches the app → Button action executes → ViewModel starts async work → service sends the request → response decoded → observable state changes → SwiftUI updates the balance. The main thread is not blocked while the server responds (URLSession with await suspends the task).

## 5. Stage four — the API request
DashboardView → BalanceViewModel → BalanceService → URLSession → HTTPS/TLS → bank API.
```swift
import Foundation

struct BalanceResponse: Decodable {
    let balanceMinor: Int64
    let currency: String
}

struct BalanceService {
    func fetchBalance() async throws -> BalanceResponse {
        let url = URL(string: "https://api.npay.example/balance")!
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(BalanceResponse.self, from: data)
    }
}
```
Fictional URL; real code needs authentication, authorization-aware errors and secure token management.

## 6. Stage five — security
Code signing · sandbox · Keychain · HTTPS/TLS · backend authorization · data protection. **Client-side security does not replace server-side authorization.**

## 7. Stage six — data returns
`{"balanceMinor": 2500000, "currency": "INR"}` → JSONDecoder → BalanceResponse → ViewModel state → SwiftUI re-evaluates → updated balance. **UI = f(State)**, which does not mean every change redraws the whole screen.

## 8. Stage seven — what to store
| Data | Appropriate storage |
|---|---|
| Dark mode preference | UserDefaults |
| Authentication token | Keychain |
| Downloaded statement PDF | Protected file storage |
| Locally saved transaction notes | SwiftData or another persistence store |
| Current screen loading flag | In-memory ViewModel state |
| Authoritative account balance | Bank backend |

**Challenge:** storing token, balance and all transactions in UserDefaults is wrong — token → Keychain; balance → backend is authoritative, local copy may be stale; transactions → structured persistence with protection and retention; preferences → UserDefaults. Choose storage by sensitivity, size, lifecycle and consistency.

## 9. Stage eight — the user leaves
Active (visible, responding; scene active, process running). *Authored:* inactive → background (runs briefly) → suspended (no code runs) → terminated. Scene phases are `.active`, `.inactive`, `.background`; suspended is a process condition.

## 10. Stage nine — memory during navigation
TransactionHistoryView → TransactionViewModel → TransactionService.
```swift
class TransactionViewModel {
    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = { [weak self] in
            self?.refresh()
        }
    }

    func refresh() {
        print("Refreshing transactions")
    }

    deinit {
        print("ViewModel deinitialized")
    }
}
```
Navigating away does not guarantee immediate deinit; the object may be legitimately retained elsewhere.

## 11. Stage ten — the user returns
Process survived (warm activation): iOS resumes execution, the scene returns, in-memory state may exist, the app refreshes when appropriate. *Authored:* process terminated (cold launch): new process, full launch, memory gone, restore persisted data and fetch fresh data. Work correctly in both; never assume cached financial data is current.

## 12. The complete flow (12 steps)
Tap NPay → iOS starts or activates the app → SwiftUI shows DashboardView → tap Check Balance → ViewModel requests data → service contacts the backend → server returns authorized data → ViewModel updates state → SwiftUI updates the screen → app persists selected data → user leaves → user returns.

## 13. Architecture review (find the mistakes)
1. Synchronous five-second calculation in a Button action → **problem** (blocks the UI).
2. *Authored:* token in UserDefaults → **problem**. 3. *Authored:* cached balance shown as current offline → **problem**. 4. *Authored:* automatic retry of a transfer POST without idempotency → **problem**. 5. *Authored:* relying on in-memory state surviving → **problem**.

## 14. The foundation module
| Lesson | Central question | Prepares for |
|---|---|---|
| 0.1 App Startup | How does an app start? | Swift entry point and Xcode |
| 0.2 Architecture | How do app components communicate? | MVVM and code organization |
| 0.3 Lifecycle | What happens when users leave? | State restoration |
| 0.4 SwiftUI vs UIKit | How does app code receive system events? | UI frameworks |
| 0.5 Threads & RunLoop | How does a tap become UI work? | Swift concurrency |
| 0.6 Memory & ARC | Who owns objects? | Structs, classes, closures |
| 0.7 Security | How does iOS protect data? | Keychain and permissions |
| 0.8 Networking | How does data reach the server? | URLSession and Codable |
| 0.9 Storage | How does data survive termination? | SwiftData and persistence |
| 0.10 Integration | How does everything fit together? | Production app development |

**Final challenge:** "I tap NPay, open my account balance, switch to another app, and return ten minutes later. Explain the entire journey from operating system to SwiftUI, networking, storage, security and lifecycle." Distinguish OS, frameworks, app code and backend.

## What's next — Unit 1: Swift Language Mastery
1. Swift language design and compilation 2. Variables, constants and type system 3. Optionals 4. Functions, parameters and closures 5. Structs, classes and value semantics 6. Enums, protocols and extensions 7. Generics and error handling 8. ARC and ownership in practice 9. Async/await, actors, structured concurrency 10. Build the NPay domain model.
