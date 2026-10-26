# Unit 3 · Lesson 3.3 — TabView: Building NPay's Main Navigation

> Lesson text as shared, in three pieces: Sections 1–11 (cut off at the knowledge check), "Part 2: TabView Internals &
> NPay Integration" (Sections 11–19), and a note offering the complete Lesson 3.3 project as a ZIP, which was not
> shared. Interactive widgets are described in brackets. The deck (`index.html`, built by `tools/gen3_3.py`) follows
> all three. The complete code at the end is **authored**: the text's sections assembled onto the 3.2 code following
> its project structure, and run in the simulator. Evidence and authored additions are listed under "Deck changes".

NPay iOS Engineering Masterclass · Incremental Development · SwiftUI Navigation Internals

In Lesson 3.2, we introduced typed routes and programmatic navigation using NavigationStack. Now we'll introduce another essential navigation concept: TabView. Our goal is to transform NPay from a dashboard with navigation links into a mobile application with four main sections. We'll learn how tabs work, how selection is managed, how TabView differs from NavigationStack, and how multiple navigation stacks can coexist.

## 1. The engineering requirement

Currently, NPay navigates from Dashboard to Send Money and History using a navigation stack. But in a real payment application, users frequently switch between major sections. We want persistent navigation between Home, Payments, History and Profile.

[Interactive NPay tab navigation preview: Profile — "NPay Demo User", "Account settings and preferences"; tab bar Home, Payments, History, Profile. "Try switching between the four tabs."]

Notice that these are top-level application sections, not simply screens pushed onto one navigation stack.

## 2. What exactly is TabView?

TabView is a generic SwiftUI container that presents multiple selectable child views. A simple example:

```swift
import SwiftUI

struct TabExperiment: View {
    var body: some View {
        TabView {
            Text("Home Screen")
                .tabItem {
                    Label("Home", systemImage: "house")
                }

            Text("History Screen")
                .tabItem {
                    Label("History", systemImage: "clock")
                }
        }
    }
}

#Preview {
    TabExperiment()
}
```

Run this in Xcode. You'll see a tab bar with Home and History.

| API | Responsibility |
|---|---|
| TabView | Hosts selectable tab content |
| .tabItem | Provides tab label and icon |
| Label | Combines text and symbol |
| Selected tab | Determines which content is active |

TabView supports different presentation styles. On iPhone, the conventional tab-based style presents a tab bar.

## 3. How is TabView different from NavigationStack?

This is the most important architectural distinction.

[NavigationStack: Dashboard → Payment → Confirmation — "Moves deeper within a navigation hierarchy." TabView: Home, Payments, History, Profile — "Switches between major application sections."]

**The key principle.** TabView answers: Which major section is active? NavigationStack answers: How deep have we navigated within a section? They solve different problems and are often used together.

## 4. Control the selected tab using @State

Let's make tab selection explicit.

```swift
enum NPayTab: Hashable {
    case home
    case payments
    case history
    case profile
}
```

Now create state: `@State private var selectedTab: NPayTab = .home`. Bind it to TabView:

```swift
TabView(selection: $selectedTab) {
    Text("Home")
        .tabItem {
            Label("Home", systemImage: "house")
        }
        .tag(NPayTab.home)

    Text("Payments")
        .tabItem {
            Label("Payments", systemImage: "arrow.up.right")
        }
        .tag(NPayTab.payments)

    Text("History")
        .tabItem {
            Label("History", systemImage: "clock")
        }
        .tag(NPayTab.history)

    Text("Profile")
        .tabItem {
            Label("Profile", systemImage: "person")
        }
        .tag(NPayTab.profile)
}
```

**What is .tag()?** The tag identifies a tab's selection value. When the user selects a tab, SwiftUI updates the bound selectedTab. When code changes selectedTab, SwiftUI can switch the active tab. This is another example of the state-driven UI model.

## 5. Behind the scenes — tab selection pipeline

[How tapping a tab changes the interface — a 5-stage stepper; only Stage 1 was shared: "1. User taps History. iOS delivers the interaction to the tab control." Caption: "Conceptual SwiftUI selection flow; internal tab-controller implementation is not guaranteed."]

## 6. Programmatically switch tabs

Suppose NPay has a button on the dashboard:

```swift
Button("View All Transactions") {
    selectedTab = .history
}
```

This changes the active tab without pushing a new navigation destination.

**Important distinction.** Changing the selected tab is not the same as calling `path.append(.history)`. The first switches major sections. The second pushes a destination onto a navigation stack. For NPay, we should choose one consistent navigation meaning for each action.

## 7. Should each tab have its own NavigationStack?

For a larger application, often yes.

[Recommended NPay tab architecture: TabView (selected tab state) → Home, Payments, History, Profile, each a NavigationStack.]

This allows each major section to manage its own navigation hierarchy. For example: Home → Account Details; Payments → Payment Confirmation; History → Transaction Details; Profile → Settings.

**Does every app need four NavigationStacks?** No. The correct structure depends on the intended navigation experience. But independent stacks are a useful design when each tab has its own deeper navigation flow.

## 8. The subtle question — does tab switching destroy state?

Suppose the user begins entering a payment. Then switches to History. Then returns to Payments. Should the entered amount remain? That depends on how state ownership and view identity are structured. SwiftUI can preserve tab-associated state, but you should not rely on undocumented view-construction details for critical draft persistence. If a payment draft must survive tab changes, we should place its state in a deliberate owner whose lifetime spans those changes. We'll investigate this in Lesson 3.5.

## 9. Incremental NPay implementation

Now let's integrate TabView into our existing application. We'll keep the existing balance and transaction state in a shared parent for now. Create NPayTab.swift (the `NPayTab` enum above). Then introduce a root tab container:

```swift
import SwiftUI

struct NPayRootView: View {
    @State private var selectedTab: NPayTab = .home

    var body: some View {
        TabView(selection: $selectedTab) {

            NavigationStack {
                Text("Home Dashboard")
                    .navigationTitle("NPay")
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack {
                Text("Payments")
                    .navigationTitle("Payments")
            }
            .tabItem {
                Label(
                    "Payments",
                    systemImage: "arrow.up.right"
                )
            }
            .tag(NPayTab.payments)

            NavigationStack {
                Text("History")
                    .navigationTitle("History")
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack {
                Text("Profile")
                    .navigationTitle("Profile")
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
    }
}
```

This is the initial tab-navigation scaffold. In the integration step, we'll replace the placeholder content with the real NPay screens from Lesson 3.2.

## 10. Connect the root view to NPayApp

```swift
import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            NPayRootView()
        }
    }
}
```

Now the application launches into the tab-based root interface.

## Part 2: TabView Internals & NPay Integration

NPay Engineering Lab · Continuing from Section 11. We've learned how TabView creates top-level navigation and how each tab can contain its own NavigationStack. Now we'll complete Lesson 3.3 by understanding three important engineering questions: (1) How do we combine our existing NPayRouter with TabView? (2) Where should NPay's shared balance and transaction state live? (3) What happens to navigation paths and view state when users switch tabs? First, let's finish our assessment.

## 11. Senior engineer knowledge check

[Tab Navigation Assessment, 0 / 5 answered; the first piece showed the same five questions.]
1. What is TabView primarily responsible for? (Switching major application sections / Pushing a route onto a navigation stack / Performing network requests)
2. What does `.tag(NPayTab.history)` provide? (A tab selection value / A database ID / A thread identifier)
3. Does changing selectedTab to .history necessarily push a NavigationStack route? (Yes / No)
4. Can each tab contain its own NavigationStack? (Yes / No)
5. Should payment draft state lifetime be designed explicitly? (Yes / No)

## 12. How do TabView and NPayRouter work together?

Our earlier router had one navigation path (`var path: [NPayRoute] = []`). But now NPay has four tabs. Suppose the user follows this journey: (1) Home → Account Details; (2) switch to History → Transaction Details; (3) switch back to Home. Ideally, Home can retain its navigation position independently of History. One shared path for every tab would make that behavior harder to manage.

[Better design — separate paths: NPayRouter (selected tab + independent paths) → Home Path (account details), Payments Path (payment success), History Path (transaction details), Profile Path (settings).]

**Implement the router**

```swift
import SwiftUI

enum NPayTab: Hashable {
    case home
    case payments
    case history
    case profile
}

enum NPayRoute: Hashable {
    case accountDetails
    case paymentSuccess(UUID)
    case transactionDetails(UUID)
    case settings
}

@MainActor
@Observable
final class NPayRouter {

    var selectedTab: NPayTab = .home

    var homePath: [NPayRoute] = []
    var paymentsPath: [NPayRoute] = []
    var historyPath: [NPayRoute] = []
    var profilePath: [NPayRoute] = []

    func select(_ tab: NPayTab) {
        selectedTab = tab
    }

    func showPaymentSuccess(_ id: UUID) {
        selectedTab = .payments
        paymentsPath.append(.paymentSuccess(id))
    }

    func returnHome() {
        paymentsPath.removeAll()
        selectedTab = .home
    }
}
```

**Why @MainActor?** Navigation state affects the user interface. Main-actor isolation helps ensure that navigation mutations occur in the appropriate UI execution context.

**Why @Observable?** The Observation framework allows SwiftUI to track relevant property reads and respond to changes. We'll study Observation in depth in Unit 4. For now, understand that this router is a reference-type object that owns navigation state.

## 13. Connect Router to TabView

```swift
import SwiftUI

struct NPayRootView: View {

    @State private var router = NPayRouter()

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {

            NavigationStack(path: $router.homePath) {
                HomeScreen()
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsScreen()
            }
            .tabItem {
                Label(
                    "Payments",
                    systemImage: "arrow.up.right"
                )
            }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen()
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
    }
}
```

This is an architectural scaffold, not yet the complete integrated NPay application: HomeScreen, PaymentsScreen, HistoryScreen, and ProfileScreen must be supplied, and the History screen from Lesson 3.1 requires transaction data. We'll connect those dependencies next.

## 14. Where should NPay's balance and transactions live?

This is a crucial design question. Our earlier ContentView owned `@State private var balancePaise = 2_500_000` and `@State private var transactions: [Transaction] = []`. But now the same data is needed across multiple tabs. We should not create a separate balance in each tab. For Unit 3, we'll introduce a shared application state object.

```swift
import SwiftUI

@MainActor
@Observable
final class NPayStore {

    var balancePaise = 2_500_000

    var transactions: [Transaction] = []

    func recordDemoPayment(
        recipient: String,
        amountPaise: Int
    ) -> UUID? {

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              amountPaise > 0,
              amountPaise <= balancePaise else {
            return nil
        }

        let id = UUID()

        balancePaise -= amountPaise

        transactions.insert(
            Transaction(
                id: id,
                title: "Sent to \(trimmed)",
                amountPaise: -amountPaise,
                date: .now
            ),
            at: 0
        )

        return id
    }
}
```

**What changed?** Previously, ContentView owned the balance and transactions. Now NPayStore owns them. The root view will own one instance of the store and pass it to the tabs. This prepares us for MVVM and dependency injection later.

**Important distinction.** This is still local, in-memory demo state. It is not persisted, authenticated, or backed by a payment server.

## 15. Connect shared state to the root view

```swift
struct NPayRootView: View {

    @State private var router = NPayRouter()
    @State private var store = NPayStore()

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {

            NavigationStack(path: $router.homePath) {
                HomeScreen(store: store)
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsScreen(
                    store: store,
                    router: router
                )
            }
            .tabItem {
                Label("Payments", systemImage: "arrow.up.right")
            }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen(
                    transactions: store.transactions
                )
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
    }
}
```

The same store instance is shared across Home, Payments, and History. When the balance changes, views reading that observable value can update.

## 16. How does SwiftUI track changes across tabs?

[NPay shared-state update flow: PaymentsScreen (user submits demo payment) → NPayStore (validates and updates balance and transactions) → Observation (tracks relevant reads and state changes) → HomeScreen (displays updated balance), HistoryScreen (displays updated transactions).]

**Senior engineer insight.** Observation doesn't mean SwiftUI automatically redraws every tab whenever any property changes. It tracks dependencies and coordinates relevant updates. The precise evaluation and rendering behavior remains framework-managed.

## 17. Navigation state versus business state

| NPayRouter | NPayStore |
|---|---|
| Selected tab | Available balance |
| Home navigation path | Transactions |
| Payments navigation path | Demo payment validation |
| History navigation path | Payment recording |
| Profile navigation path | Application data |

This is an important separation of responsibilities. The router decides where the user goes. The store manages what the application knows. Neither should take over the other's responsibilities.

## 18. Unit 3.3 architecture checkpoint

[NPay application architecture: NPayApp → NPayRootView (owns NPayRouter + NPayStore) → Home (balance and dashboard), Payments (form and confirmation), History (transactions), Profile (user settings).]

## 19. Lesson 3.3 completion checklist

[Lesson 3.3 review, 0 / 8]
- [ ] Understand TabView versus NavigationStack
- [ ] Understand selectedTab and .tag()
- [ ] Create the NPayTab enum
- [ ] Create independent navigation paths
- [ ] Understand the NPayRouter responsibility
- [ ] Understand shared NPayStore ownership
- [ ] Explain why business state should not live inside the router
- [ ] Review the root architecture diagram

**Lesson 3.3 — Conceptual lesson complete.** We've covered tab selection, independent navigation stacks, route coordination, shared state ownership, Observation, and navigation architecture. The remaining practical integration is to supply the actual Home, Payments, History, and Profile screens using the existing NPay components. We should do that as the complete Lesson 3.3 Xcode code checkpoint before advancing.

Next — Lesson 3.4: Sheets, Alerts & Modal Presentation. We'll build NPay's payment review flow and investigate how SwiftUI presents temporary screens over the current navigation hierarchy.

## Complete Xcode project (note from the text)

[NPay — Unit 3, Lesson 3.3: Complete Xcode Project. SwiftUI · TabView · NavigationStack · NPayRouter · NPayStore · iOS 17+. Building on 3.2: four working tabs, each with its own navigation stack, sharing one application store. Illustration: NPay, Available Balance ₹25,000.00, NPay Demo Account, Send Money / History, Recent Transactions (Coffee Shop −₹250, Electricity Bill −₹1,200, Salary Credit +₹45,000), tab bar Home, Payments, History, Profile.]

Project structure:

```
NPay/
├── NPayApp.swift
├── App/
│   ├── NPayRootView.swift
│   └── NPayRouter.swift
├── Models/
│   ├── Money.swift
│   └── Transaction.swift
├── Store/
│   └── NPayStore.swift
├── Components/
│   ├── BalanceCard.swift
│   └── TransactionRow.swift
└── Screens/
    ├── HomeScreen.swift
    ├── PaymentsScreen.swift
    ├── PaymentSuccessScreen.swift
    ├── HistoryScreen.swift
    ├── TransactionDetailScreen.swift
    └── ProfileScreen.swift
```

[A ZIP "NPay Lesson 3.3 Complete Code" was offered (ContentView.swift, NPayApp.swift and a README), with the note that it had not been compiled. It was not shared; the code below replaces it.]

**Verify these five behaviors.** (1) Switch between Home, Payments, History, and Profile. (2) Send a demo payment of ₹1,500.50. (3) Confirm the updated balance is ₹23,499.50. (4) Open History and select a transaction to view its details. (5) Return to Home and verify that the shared state is preserved.

## Complete code through Lesson 3.3 (authored)

Written from Sections 9–18 and the structure above, on top of the 3.2 code, and run unchanged in the simulator
(`tools/sim3_3/App.swift`). Models/Money.swift, Models/Transaction.swift, Components/BalanceCard.swift and
Components/TransactionRow.swift are unchanged from 3.1; Screens/PaymentSuccessScreen.swift is unchanged from 3.2 (see
the earlier lesson texts). The Unit 2 BalanceEditor is not in the structure and is dropped.

Choices that go beyond the text (flagged): seed transactions in `NPayStore` (the illustration shows them); Home gets the
router (its Send Money and History buttons switch tabs) and an Account Details link; one `destination(_:)` function
registered on every tab's root; transaction details resolved by ID from the store with a `ContentUnavailableView` when
missing; History rows as `NavigationLink(value:)`; PaymentsScreen clears its fields after a successful payment;
`AccountDetailsScreen` (in HomeScreen.swift) and `SettingsScreen` (in ProfileScreen.swift).

### NPayApp.swift

```swift
import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            NPayRootView()
        }
    }
}
```

### App/NPayRouter.swift

```swift
import SwiftUI

enum NPayTab: Hashable {
    case home
    case payments
    case history
    case profile
}

enum NPayRoute: Hashable {
    case accountDetails
    case paymentSuccess(UUID)
    case transactionDetails(UUID)
    case settings
}

@MainActor
@Observable
final class NPayRouter {

    var selectedTab: NPayTab = .home

    var homePath: [NPayRoute] = []
    var paymentsPath: [NPayRoute] = []
    var historyPath: [NPayRoute] = []
    var profilePath: [NPayRoute] = []

    func select(_ tab: NPayTab) {
        selectedTab = tab
    }

    func showPaymentSuccess(_ id: UUID) {
        selectedTab = .payments
        paymentsPath.append(.paymentSuccess(id))
    }

    func returnHome() {
        paymentsPath.removeAll()
        selectedTab = .home
    }
}
```

### Store/NPayStore.swift

```swift
import SwiftUI

@MainActor
@Observable
final class NPayStore {

    var balancePaise = 2_500_000

    var transactions: [Transaction] = [
        Transaction(
            id: UUID(),
            title: "Coffee Shop",
            amountPaise: -25_000,
            date: .now
        ),
        Transaction(
            id: UUID(),
            title: "Electricity Bill",
            amountPaise: -120_000,
            date: .now
        ),
        Transaction(
            id: UUID(),
            title: "Salary Credit",
            amountPaise: 4_500_000,
            date: .now
        )
    ]

    func recordDemoPayment(
        recipient: String,
        amountPaise: Int
    ) -> UUID? {

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              amountPaise > 0,
              amountPaise <= balancePaise else {
            return nil
        }

        let id = UUID()

        balancePaise -= amountPaise

        transactions.insert(
            Transaction(
                id: id,
                title: "Sent to \(trimmed)",
                amountPaise: -amountPaise,
                date: .now
            ),
            at: 0
        )

        return id
    }
}
```

### App/NPayRootView.swift

```swift
import SwiftUI

struct NPayRootView: View {

    @State private var router = NPayRouter()
    @State private var store = NPayStore()

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {

            NavigationStack(path: $router.homePath) {
                HomeScreen(store: store, router: router)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsScreen(
                    store: store,
                    router: router
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Payments", systemImage: "arrow.up.right")
            }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen(
                    transactions: store.transactions
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
    }

    // One mapping from route to screen, registered in every tab's stack
    @ViewBuilder
    private func destination(_ route: NPayRoute) -> some View {
        switch route {
        case .accountDetails:
            AccountDetailsScreen(balancePaise: store.balancePaise)

        case .paymentSuccess(let id):
            PaymentSuccessScreen(
                transactionID: id,
                onDone: { router.returnHome() }
            )

        case .transactionDetails(let id):
            if let transaction = store.transactions.first(where: { $0.id == id }) {
                TransactionDetailScreen(transaction: transaction)
            } else {
                ContentUnavailableView(
                    "Transaction not found",
                    systemImage: "questionmark.circle"
                )
            }

        case .settings:
            SettingsScreen()
        }
    }
}
```

### Screens/HomeScreen.swift

```swift
import SwiftUI

struct HomeScreen: View {
    let store: NPayStore
    let router: NPayRouter

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                BalanceCard(balancePaise: store.balancePaise)

                HStack(spacing: 12) {
                    Button {
                        router.select(.payments)
                    } label: {
                        Label("Send Money", systemImage: "arrow.up.right")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                Color.blue.opacity(0.1),
                                in: RoundedRectangle(cornerRadius: 12)
                            )
                    }

                    Button {
                        router.select(.history)
                    } label: {
                        Label("History", systemImage: "clock")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                Color.blue.opacity(0.1),
                                in: RoundedRectangle(cornerRadius: 12)
                            )
                    }
                }

                NavigationLink(value: NPayRoute.accountDetails) {
                    Label("Account Details", systemImage: "person.text.rectangle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text("Recent Transactions")
                        .font(.headline)

                    ForEach(store.transactions.prefix(3)) { transaction in
                        TransactionRow(transaction: transaction)
                        Divider()
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .padding()
        }
        .navigationTitle("NPay")
    }
}

struct AccountDetailsScreen: View {
    let balancePaise: Int

    var body: some View {
        List {
            LabeledContent("Account", value: "NPay Demo Account")
            LabeledContent("Holder", value: "NPay Demo User")
            LabeledContent("Available", value: Money.display(balancePaise))
        }
        .navigationTitle("Account Details")
    }
}
```

### Screens/PaymentsScreen.swift

```swift
import SwiftUI

struct PaymentsScreen: View {
    let store: NPayStore
    let router: NPayRouter

    @State private var recipient = ""
    @State private var amountText = ""

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    private var parsedAmount: Int? {
        Money.parsePaise(amountText)
    }

    private var isValid: Bool {
        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              let amount = parsedAmount else {
            return false
        }

        return amount > 0
            && amount <= store.balancePaise
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text(
                    "Available: \(Money.display(store.balancePaise))"
                )
                .foregroundStyle(.secondary)

                TextField(
                    "Recipient ID",
                    text: $recipient
                )
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .recipient
                )
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .amount
                }

                TextField(
                    "Amount (₹)",
                    text: $amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )

                if !amountText.isEmpty && !isValid {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                Button("Send Demo Payment") {
                    guard let amount = parsedAmount else {
                        return
                    }

                    if let id = store.recordDemoPayment(
                        recipient: recipient,
                        amountPaise: amount
                    ) {
                        focusedField = nil
                        recipient = ""
                        amountText = ""
                        router.showPaymentSuccess(id)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isValid)
            }
            .padding()
        }
        .navigationTitle("Payments")
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()

                Button("Done") {
                    focusedField = nil
                }
            }
        }
    }
}
```

### Screens/HistoryScreen.swift

```swift
import SwiftUI

struct HistoryScreen: View {
    let transactions: [Transaction]

    var body: some View {
        List(transactions) { transaction in
            NavigationLink(value: NPayRoute.transactionDetails(transaction.id)) {
                TransactionRow(transaction: transaction)
            }
        }
        .navigationTitle("History")
    }
}
```

### Screens/TransactionDetailScreen.swift

```swift
import SwiftUI

struct TransactionDetailScreen: View {
    let transaction: Transaction

    var body: some View {
        List {
            LabeledContent("Title", value: transaction.title)
            LabeledContent("Amount", value: Money.display(transaction.amountPaise))
            LabeledContent(
                "Date",
                value: transaction.date.formatted(date: .abbreviated, time: .shortened)
            )
            LabeledContent("ID") {
                Text(transaction.id.uuidString)
                    .font(.caption2.monospaced())
            }
        }
        .navigationTitle("Transaction")
    }
}
```

### Screens/ProfileScreen.swift

```swift
import SwiftUI

struct ProfileScreen: View {
    var body: some View {
        List {
            Section {
                HStack(spacing: 16) {
                    Image(systemName: "person.crop.circle.fill")
                        .font(.system(size: 48))
                        .foregroundStyle(.blue)

                    VStack(alignment: .leading, spacing: 4) {
                        Text("NPay Demo User")
                            .font(.headline)
                        Text("Account settings and preferences")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            NavigationLink(value: NPayRoute.settings) {
                Label("Settings", systemImage: "gearshape")
            }
        }
        .navigationTitle("Profile")
    }
}

struct SettingsScreen: View {
    @State private var notifications = true

    var body: some View {
        List {
            Toggle("Payment notifications", isOn: $notifications)
            LabeledContent("Version", value: "Lesson 3.3 demo")
        }
        .navigationTitle("Settings")
    }
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_3.py`, 45 slides) follows all three pieces, grouped into 7 Parts: the
requirement (1), TabView (2, 3), selection is state (4–6), a stack per tab (7, 12, 13), does switching destroy state?
(8), shared state: NPayStore (14–17), NPay after Lesson 3.3 (9, 10, 18, 19 and the complete code); then recap,
review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_3/`, rerun with `sh tools/sim3_3/run.sh`; buttons through
accessibility, Back by popping the hosting navigation controller as in 3.1; tab buttons don't respond to accessibility
activation in the simulator either, so a tab is selected as a tap does: ask the tab bar controller's delegate, select,
tell the delegate. SwiftUI's selection binding updated each time.)
- TabExperiment: launch and History selected (screenshots).
- Section 4/6 selection, printed by `onChange`: History → `home → history`, Home → `history → home`; "View All
  Transactions" → `home → history`.
- Section 12's journey on the complete app with the router state printed (`TracedRootView` = NPayRootView + prints):
  homePath `[accountDetails]`; History, Coffee Shop → historyPath `[transactionDetails(3341DC68…)]`; back on Home it still
  shows Account Details (screenshot). Payment: paymentsPath `[paymentSuccess(CB81C78F…)]`; Back to Dashboard →
  selectedTab home, paymentsPath `[]`, and Home still on Account Details now showing ₹23,499.50 (returnHome clears only
  the payments path; raised as a design question on the slide and in the lab).
- Section 8, authored experiment: four probe tabs. Only Home built at launch; a tab's body runs on first selection;
  switching fires onAppear/onDisappear and keeps `@State` (same timestamp); Payments and Profile never built. On the
  complete app, a typed draft (ravi@npay, 1500.50) survived History and back.
- Section 16, authored experiment: one observable store, three tabs reading different properties; after a payment only
  the two readers of changed properties re-ran their bodies (including the off-screen one); the profile-name tab did not.
- The five behaviors, all run: four tabs; ₹1,500.50 → Payment Recorded in the Payments tab; ₹23,499.50 on Home; History
  → transaction details (Sent to ravi@npay, -₹1,500.50); Home keeps the shared state. Screenshots of every screen.

**Authored (flagged)**
- The complete code (choices listed above) and the slides that show it.
- Section 5's stages 2–5 (only stage 1 shared), marked conceptual with the text's caption.
- The lifetime and Observation experiments and the draft run; the "design the draft's lifetime" slide restates Section 8.
- Review: the text's 5 questions (options reordered so answers vary) plus two predict items (Home's position after a tab
  round trip; which body didn't re-run), a router-vs-store item, and a spaced item from 3.2; 1 of 9 verdicts is "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.4 and 3.5 as the text names them; Unit 4 for Observation,
  MVVM and DI as the text says), lab, end slide.

**Wording**
- "Senior engineer knowledge check / insight" became "Check your understanding" and neutral callouts.
