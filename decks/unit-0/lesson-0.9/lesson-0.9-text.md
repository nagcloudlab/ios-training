# Lesson 0.9 — iOS Data Storage Architecture

*iOS Architecture Mastery · Foundation Series*

> Lesson text as shared; the deck (`index.html`) uses only this text. **PocketBank is renamed NPay.** "Trainer"
> material became speaker notes; the trainer questions became the review. **Authored for the deck** (flagged): the
> outcomes slide (from "Final understanding"); the storage-chooser answers other than dark mode; the "saved draft"
> outcome in the termination simulation; review answers and traps. **Code change:** the SwiftData snippet gains
> `import Foundation` (needed for `Decimal`).

**Question:** The user closes NPay, switches apps or restarts the iPhone. What happens to the data? Where should we store tokens, preferences, transaction records and downloaded images?

## 1. A simple story
NPay receives `{"accountId": "A1001", "balance": 25000, "currency": "INR"}` and shows ₹25,000. Holding data in memory to display it and persisting it for later are different operations. RAM: runtime state, temporary. Persistent storage: files, databases, preferences, durable. **Analogy:** RAM is a classroom whiteboard, storage is a notebook.

## 2. The major storage choices
UserDefaults (preferences) · SwiftData (structured app data) · FileManager (documents and files) · Keychain (credentials and secrets). Also Core Data, SQLite, caches, cloud sync. The question is not "which API is best?" but "what kind of data is this, and what guarantees does it need?"

## 3. UserDefaults
```swift
import Foundation

UserDefaults.standard.set(true, forKey: "darkModeEnabled")
let darkMode = UserDefaults.standard.bool(forKey: "darkModeEnabled")
print(darkMode)
```
Good for theme, onboarding completion, preferred language, simple settings. Not a database, not a credential store.

## 4. SwiftData
SwiftUI screen → SwiftData ModelContext → persistent model storage.
```swift
import Foundation
import SwiftData

@Model
final class TransactionNote {
    var title: String
    var amount: Decimal

    init(title: String, amount: Decimal) {
        self.title = title
        self.amount = amount
    }
}
```
`@Model` marks a persistent model. SwiftData is not a self-saving array: learn containers, contexts, relationships, schema evolution and save behavior.

## 5. Files
| Directory | Typical purpose |
|---|---|
| Documents | User documents and persistent app files |
| Application Support | App-managed support files |
| Caches | Re-creatable cached content |
| Temporary | Short-lived temporary files |

The system can remove cached and temporary content.
```swift
import Foundation

let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
let statementURL = documents.appendingPathComponent("statement.pdf")
```
This builds a URL; it does not download or write the PDF.

## 6. Keychain — choose the storage
Dark mode → UserDefaults (lightweight non-secret preference). *Authored:* auth token → Keychain · PDF statement → files · transaction notes → SwiftData. Sensitive documents may also need file protection, encryption and retention policies.

## 7. When the app is terminated
A transfer note ("Rent payment") typed but not saved is lost when iOS terminates the process. *Authored:* a saved draft survives relaunch. Persist important data before memory can be lost; do not depend on a termination callback; save periodically or on meaningful changes.

## 8. Cache versus source of truth
Offline: cached balance ₹25,000 (last updated earlier) vs current verified balance unavailable. Communicate freshness; the backend stays authoritative.

## 9. SwiftData vs Core Data vs SQLite
| Technology | What it provides |
|---|---|
| SwiftData | Swift-native persistence framework with model-oriented APIs |
| Core Data | Mature object graph management and persistence framework |
| SQLite | Embedded relational database engine |
| FileManager | Filesystem operations rather than database object management |

SwiftData and Core Data can use SQLite-backed stores. New SwiftUI apps: SwiftData is often a good start. Core Data remains important for existing and advanced needs.

## 10. Check your understanding
1. Does `@State` guarantee data survives termination? **No.**
2. Should auth tokens normally go in UserDefaults? **No.**
3. Can iOS remove files in a cache directory? **Yes.**
4. Should a banking app present stale cached balances as verified live balances? **No.**

**Next — Lesson 0.10: Complete iOS Architecture, End to End.** Tap app → process launch → SwiftUI screen → button event → API request → secure authentication → data storage → backgrounding → suspension → relaunch.

## Deck changes after the Unit 00 audit

The deck now differs from the text above as follows (authored items are marked *authored*).

- **Corrections**
  - Sample JSON uses `"balanceMinor": 2500000` (paise, `Int64`), the course-wide money convention. The ViewModel formats ₹25,000.
  - The SwiftData note stores `amountMinor: Int64` instead of `Decimal`. One line notes that `@Model` objects are not Sendable.
  - The file snippet uses `URL.cachesDirectory.appending(path:)` and `URL.applicationSupportDirectory`, and writes with `.completeFileProtection`. It no longer uses `urls(for:).first!` or `appendingPathComponent`.
  - The directory table adds "Backed up". Documents is for user-created documents (backed up, can be shown in Files); app data goes in Application Support; the statement PDF goes in **Caches** because it can be downloaded again.
  - The `@State` answer says it lives with the view's identity in the running process, not "with the app".
- **Consistency:** the whiteboard/notebook analogy is replaced by the course's restaurant-kitchen analogy (counter = RAM, pantry = storage).
- **Token:** "token in UserDefaults?" is no longer a review question (Lesson 0.7 owns it); it is recalled in one line in Part 3.
- **Part 9:** the comparison table became an abstraction-level diagram (SwiftData / Core Data → SQLite store → files; FileManager → files).
- **Forward pointers** (one line each): Unit 06 lessons 6.1, 6.2, 6.5, 6.6 and 6.9 (drafts, state restoration, `@SceneStorage`).
- *Authored:*
  - a "Where we are" map slide with Last time / Today
  - a recap slide
  - a review of 5 questions: multiple choice; predict-the-output; `@State`; offline cached balance (answer Yes); and a spaced item from 0.3
  - a "Where this goes next" slide
  - the storage-chooser lab (10 NPay items)
  - the end line "Next: Lesson 0.10"
