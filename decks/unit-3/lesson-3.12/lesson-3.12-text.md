# Unit 3 · Lesson 3.12 — NPay Final Integration & Architecture Mastery

NPay iOS Engineering Masterclass · Unit 3 Capstone · Lessons 3.1–3.12
We've reached the final lesson of Unit 3.
Over the last 11 lessons, we learned individual SwiftUI concepts. Now we need to answer a much bigger question:
How do all these concepts work together inside one running iOS application?
This lesson will connect the architecture, data flow, navigation, UI lifecycle, and performance concepts we've studied. We'll also identify which responsibilities should move into MVVM when we begin Unit 4.

## 1. Our final NPay milestone

NPay
Demo
Available Balance
₹25,000.00
NPay Demo Account
Send Money
History
Recent Transactions
Coffee Shop
−₹250
Electricity Bill
−₹1,200
Salary Credit
+₹45,000

Home
Payments
History
Profile
Interactive NPay capstone prototype. The Xcode implementation uses native SwiftUI navigation, sheets, and integer-paise money values.

## 2. Complete Unit 3 feature inventory

| Lesson | Concept | Integrated NPay feature |
|---|---|---|
| 3.1 | NavigationStack | Screen navigation |
| 3.2 | Typed routes | Programmatic payment-success navigation |
| 3.3 | TabView | Four top-level tabs |
| 3.4 | Sheets and alerts | Payment review |
| 3.5 | State preservation | Payment drafts survive tab changes |
| 3.6 | Animations | Balance and success feedback |
| 3.7 | Reusable components | NPay design system |
| 3.8 | Adaptive layout | Responsive quick actions |
| 3.9 | Environment | Appearance preferences |
| 3.10 | Accessibility and localization | Accessible controls and translated resources |
| 3.11 | Performance | Lazy transaction history and search |
| 3.12 | Integration | Complete multi-screen NPay |

## 3. The final architecture

NPayApp
@main · WindowGroup
NPayRootView
Application composition root
NPayRouter
Tabs + paths
NPayStore
Balance + transactions + draft
NPayPreferences
Appearance + configuration
TabView
Four independent navigation hierarchies
Home
Dashboard + balance
Payments
Form + review + success
History
Search + details
Profile
Settings + appearance
The most important architectural decision is that navigation, application data, and appearance preferences have separate owners.
This prepares NPay for the MVVM refactoring in Unit 4.

## 4. Trace a complete payment through the architecture

Let's follow one demo payment of ₹1,500 to ravi@npay.
Payment execution trace
*(Interactive stepper in the original, 7 steps; only step 1 was shared.)*
@Bindable · Observation
PaymentsScreen
User enters recipient and amount. TextField bindings update the shared PaymentDraft.

Important engineering insight
The router should never deduct money. The review sheet should never own the account balance. And the balance card should never process a payment.
Each component has a specific responsibility.

## 5. Unit 3 architecture limitations

Our NPay application is now a functional learning prototype, but it still has important limitations.
| Current implementation | What we'll improve |
|---|---|
| NPayStore combines multiple responsibilities | Feature-specific ViewModels |
| Payment logic lives in an observable store | Dedicated payment use case |
| Transactions are in memory | Persistence and API repositories |
| UI directly coordinates some operations | MVVM and dependency injection |
| No automated test coverage | Unit, integration, and UI tests |
| No real authentication or payment backend | Secure API-driven workflow |

This is intentional. Unit 3 teaches SwiftUI application composition; Unit 4 will teach architecture and testability.

## 6. Final Xcode integration checklist

Before advancing, verify the complete NPay project.
NPay Unit 3 acceptance tests
*(Interactive checklist in the original; its items were not shared in Part 1.)*

*(Part 1 ends here; Part 2 restarts at Section 4.)*

---

## Part 2: Complete NPay Architecture & Runtime Integration

Final Unit 3 Capstone · Continuing from Section 3
We've assembled the architecture of NPay: four tabs, a typed router, shared state, preferences, and reusable components.
Now we'll investigate what actually happens inside NPay when a user completes a payment, from tapping the button to updating the dashboard and transaction history.
This is the final architecture walkthrough before Unit 4.

## 4. Trace a complete payment through NPay

Imagine the user sends ₹1,500.50 to ravi@npay.
NPay end-to-end execution flow
*(Interactive stepper in the original, 10 steps; only step 1 was shared.)*
1. Text input
TextField updates the shared PaymentDraft through @Bindable.

Important engineering distinction
This flow contains three different kinds of state:
| State | Owner | Example |
|---|---|---|
| Business/demo state | NPayStore | Balance, transactions |
| Navigation state | NPayRouter | Selected tab, route paths |
| Presentation state | PaymentsScreen | Review sheet visibility |

Keeping these responsibilities separate reduces coupling and makes debugging easier.

## 5. What does the SwiftUI runtime actually do?

Let's connect our Unit 0 architecture knowledge with everything we've learned in SwiftUI.
From application state to pixels
Application event
Tap, text input, navigation or data change
State mutation
@State, Binding or Observable model changes
Dependency invalidation
SwiftUI determines which descriptions may need updating
View evaluation
Relevant body values are reevaluated
Reconciliation and layout
SwiftUI coordinates identity, structure and geometry
Rendering and presentation
The platform presents the resulting interface
Conceptual runtime pipeline. SwiftUI's exact reconciliation and rendering implementation is not publicly specified.
The key principle
When the balance changes, SwiftUI does not require us to manually call a method such as refreshBalanceCard().
We change the state.
The view descriptions express how the interface should look for that state.
SwiftUI coordinates the resulting updates.

## 6. State ownership — the most important Unit 3 concept

Let's review where each value belongs.
| Property | Owner | Reason |
|---|---|---|
| balancePaise | NPayStore | Shared application data |
| transactions | NPayStore | Shared transaction collection |
| paymentDraft | NPayStore | Must survive tab switches |
| selectedTab | NPayRouter | Top-level navigation |
| paymentsPath | NPayRouter | Payment navigation hierarchy |
| reviewDraft | PaymentsScreen | Temporary modal presentation |
| focusedField | PaymentsScreen | Local keyboard focus |
| showSuccessAnimation | PaymentSuccessScreen | Temporary visual state |
| appearance | NPayPreferences | Shared UI preference |

Why not put everything in NPayStore?
Because state should be owned at the narrowest level that supports its intended lifetime and sharing requirements.
A focus indicator doesn't need to be global.
A balance shouldn't be duplicated independently in four tabs.
This is a foundational architectural skill.

## 7. Final integration test — simulate a complete transaction

Our starting balance is ₹25,000.
The user sends ₹1,500.50.
Starting balance
₹25,000.00
Payment
−₹1,500.50

Expected balance
₹23,499.50
Integer-paise calculation: 2,500,000 − 150,050 = 2,349,950 paise.
What should the application verify?
Unit 3 integration checklist
*(Interactive checklist in the original.)*
Dashboard initially displays ₹25,000.00
Payments tab accepts a valid recipient and amount
Review sheet displays the exact entered payment
Canceling review preserves the draft
Confirming records exactly one demo transaction
Payment success screen appears after sheet dismissal
Dashboard displays ₹23,499.50
History contains the new transaction
Payment draft is cleared after success
Appearance preference applies across tabs
VoiceOver can identify important controls
History remains responsive with a larger dataset

## 8. Architecture limitations — what still needs improvement?

Our NPay application is a functional local prototype, but several engineering concerns remain.
| Current implementation | Future improvement |
|---|---|
| NPayStore contains payment rules | Dedicated use cases and domain services |
| Screens access shared store | Feature ViewModels |
| Demo transactions in memory | Repository and persistence |
| Local payment simulation | Backend API integration |
| Simple error handling | Typed errors and loading states |
| Manual testing | Automated unit and UI tests |
| One application module | Feature modularization |

These are not reasons to rewrite everything immediately.
They are the motivation for Unit 4.

## 9. Unit 3 senior-engineer final assessment

Unit 3 Final Assessment
*(Interactive quiz in the original.)*

**1. Who should own NPay's shared account balance?**

Each tab independently

One shared application state owner

The review sheet

**2. What is the purpose of NPayRouter?**

Navigation state

Payment calculations

Currency formatting

**3. Why preserve PaymentDraft outside the review sheet?**

To survive review dismissal

To create a new process

To avoid using Swift

**4. Does LazyVStack automatically fetch transactions from an API?**

Yes

No

**5. Why use stable transaction IDs?**

To preserve logical identity

To increase frame rate automatically

To create a new navigation stack

**6. What is the role of @Environment?**

Read contextual values from the view hierarchy

Persist data to disk

Create threads

**7. Should the payment success animation determine whether the transaction succeeded?**

Yes

No

**8. What is the main purpose of Unit 4?**

Introduce maintainable application architecture

Replace SwiftUI with UIKit

Remove all protocols

Unit 3 — Conceptual curriculum completed
We've covered all 12 lessons of Advanced SwiftUI, including navigation, tabs, modal presentation, state lifetime, animation, reusable components, layout, environment, accessibility, localization, and performance.
The integrated Xcode implementation and verification for Lessons 3.7–3.12 are still outstanding. The architecture walkthrough above completes the conceptual portion, not the final runnable codebase.
Our next practical milestone is to produce and test the consolidated NPay Unit 3 source before beginning Unit 4 — MVVM & Application Architecture.

## Integration through Lesson 3.12 (authored)

The text says the integrated Xcode implementation for Lessons 3.7–3.12 is still outstanding. For this deck it was built
and verified. It is the complete NPay from the 3.7–3.11 integrations, kept in `tools/sim3_12/App.swift` below the
"Complete code through Lesson 3.12" marker. Lesson 3.12 adds only two accessibility fixes, which checklist item 11 demanded:

```swift
// Screens/PaymentsScreen.swift
TextField("Recipient ID", text: $store.paymentDraft.recipient)
    // … unchanged modifiers …
    .accessibilityIdentifier(NPayAccessibilityID.recipientField)
    .accessibilityLabel("Recipient")          // the field had an empty label (3.10)

TextField("Amount (₹)", text: $store.paymentDraft.amountText)
    // … unchanged modifiers …
    .accessibilityIdentifier(NPayAccessibilityID.amountField)
    .accessibilityLabel("Amount in rupees")

// Screens/PaymentSuccessScreen.swift
Image(systemName: "checkmark.circle.fill")
    // … unchanged modifiers …
    .accessibilityHidden(true)                // was read as "Selected"; the text says it all
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_12.py`, 38 slides) has 7 Parts:
1. The finished NPay (sections 1, 2).
2. The final architecture (3, plus Part 1's section 4 insight).
3. One payment, end to end (Part 2's section 4).
4. The SwiftUI runtime (5).
5. State ownership (6).
6. The final integration test (7).
7. Limitations and Unit 4 (Part 1's section 5 and Part 2's section 8, merged).

Then recap, review, next, lab and end. Part 2 restarts at Section 4, so its Sections 4–9 replace Part 1's partial 4–6.
The trace uses Part 2's ₹1,500.50, not Part 1's ₹1,500.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_12/`, rerun with `sh tools/sim3_12/run.sh`):
- **How it was driven:** the app is driven through accessibility. A DEBUG-only hook in NPayRootView hands the router,
  store and preferences to the test driver; the hook is not part of NPay.
- **Trace, as printed:**
  - Typing writes the store's draft; Review presents the sheet and leaves the store unchanged.
  - Confirm: balance 2,500,000 → 2,349,950 paise, transactions 3 → 4, draft emptied, sheet gone, paymentsPath
    [.paymentSuccess].
  - Back to Dashboard: tab .home, path [].
- **Checklist:** all 12 items pass.
  - Item 5: Confirm activated twice → 1 transaction.
  - Item 10: dark in all four tabs.
  - Item 11 **failed on the 3.11 code** (both payment fields had an empty label) and passes after the two fixes above.
- **Item 12:** 50,000 demo transactions added (50,003, +5 MB). History exposes 8 rows. Search "49999" finds one match.
  The display delivers 60 frames in the second after typing. These are counts, not a benchmark.
- **Screenshots:** Home before and after, the review sheet, success, History after, and Home in dark.

**Authored (flagged)**
- Section 4 (Part 2): steps 2–10 of the trace, read from NPay's code; only step 1 was shared.
- Part 1's Section 4 insight table: the NPayStore row.
- Section 6: the text's `reviewDraft` / `showSuccessAnimation` are `review` / `showContent` in our code (noted on the
  slide).
- Section 7: the checklist results, the item 11 fix, and the item 12 run.
- Section 8: the merged limitations table and its Unit column (mapping to the curriculum).
- Outcomes, "Where we are", recap, "Where this goes next", lab (Unit 3 checkpoint) and end slide.
- Review: the text's 8 questions (options reordered so answers vary), a predict item (double Confirm) and a spaced item
  from 3.11; 2 of 10 verdicts are "No".

**Not used:** the interactive prototype of Section 1, replaced by the real app's screenshots. Part 1's Section 6 checklist
items were not shared; Part 2's twelve items are used.

**Wording**
- "Senior-engineer final assessment / insight" became neutral callouts and "Check your understanding".
