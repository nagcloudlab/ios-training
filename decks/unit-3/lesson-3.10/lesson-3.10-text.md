# Unit 3 · Lesson 3.10 — Accessibility & Localization (Part 2)

> Lesson text as shared: only "Part 2: Localization Internals, RTL Layout & Accessibility Testing" (Sections 15–25),
> followed by a short status note ("done?" / Unit 3 runs to 12 lessons). **Part 1 (Sections 1–14: VoiceOver, Dynamic Type,
> String Catalogs) was not shared**; the deck covers Sections 15–25 and can be extended when Part 1 arrives.
> Interactive widgets are described in brackets. The deck (`index.html`, built by `tools/gen3_10.py`) follows the text.
> Evidence and authored additions are listed under "Deck changes".

NPay iOS Engineering Masterclass · Continuing from Section 15

We've learned how VoiceOver interprets SwiftUI views, how Dynamic Type affects layouts, and how String Catalogs support multiple languages. Now we'll finish Lesson 3.10 by investigating localization at runtime, right-to-left layouts, number formatting, and accessibility testing.

## 15. Interactive NPay language explorer — continued

Switch between English, Tamil, and Hindi. Notice how the text changes while the NPay screen structure remains the same.

[English / தமிழ் / हिन्दी; NPay, Available Balance ₹25,000.00, Send Money, Recent Transactions (Coffee Shop · −₹250); tabs Home, Payments, History, Profile. Caption: "Conceptual multilingual NPay interface. Real iOS localization uses localized resources and locale-aware formatting."]

**What should you observe?** The same screen can display different languages without changing its underlying SwiftUI architecture. However, translations can change the length of labels, which affects layout. That's why localization and adaptive layout design must work together.

## 16. Behind the scenes — how localization is resolved

Let's revisit `Text("payment.send")`. Here, the string literal can be interpreted as a LocalizedStringKey. SwiftUI uses the effective localization context to resolve the displayed string.

[Localization resolution pipeline: SwiftUI Text (Text("payment.send")) → Localization key (identifies the translatable resource) → Locale and app language (determine the appropriate localization) → Localizable.xcstrings (contains translations and development-language values) → Rendered text (displays the resolved localized string).]

**Important distinction — String versus LocalizedStringKey.** Compare

```swift
let title: String = "payment.send"
Text(title)
```

with `Text("payment.send")`. The second expression can use SwiftUI's localized-string-key initializer. The first supplies an ordinary String value, so you should not assume it will be resolved as a localization key. For explicit localization, you can write `Text(LocalizedStringKey("payment.send"))`.

## 17. Locale-aware currency formatting

This is especially important for NPay. A financial application must distinguish between the monetary value, the currency, and the formatting locale. For example, ₹1,500.50 is the same monetary amount regardless of how it is displayed.

```swift
import Foundation

let amount = Decimal(150050) / Decimal(100)

let india = amount.formatted(
    .currency(code: "INR")
        .locale(Locale(identifier: "en_IN"))
)

let usa = amount.formatted(
    .currency(code: "INR")
        .locale(Locale(identifier: "en_US"))
)

print(india)
print(usa)
```

Both values represent INR. The presentation may differ according to locale conventions.

**Senior engineer insight.** Changing the user's language must not change the actual currency or monetary value. Localization is a presentation concern; financial calculations remain governed by the domain model.

## 18. Why not build currency strings manually?

Avoid `Text("₹\(amount)")` for production-facing monetary presentation. Manual formatting can create problems with grouping, decimal separators, currency placement, and accessibility announcements. Prefer locale-aware formatting:

```swift
Text(
    amount,
    format: .currency(code: "INR")
)
```

In our NPay domain model, amounts remain integer paise. We convert to an appropriate decimal representation for formatting.

## 19. Right-to-left layout — Arabic and Hebrew

Tamil and Hindi are written left-to-right. But languages such as Arabic and Hebrew use right-to-left writing directions. What happens to NPay's layout in an RTL environment? SwiftUI provides layout-direction awareness: `@Environment(\.layoutDirection) private var layoutDirection`. Possible values include `.leftToRight` and `.rightToLeft`.

[Interactive layout-direction explorer: Left to Right / Right to Left; Send Money, Available Balance ₹25,000, Transaction History. Caption: "Illustration of directional layout changes. Real SwiftUI RTL behavior also depends on localization, semantic alignment, and symbol mirroring support."]

**Important design principle.** Avoid assuming that leading always means left. In SwiftUI, `.frame(maxWidth: .infinity, alignment: .leading)` uses semantic alignment that can adapt to layout direction. For multilingual applications, prefer .leading and .trailing over hardcoded left/right assumptions where appropriate.

## 20. Test RTL layouts in Xcode

You can test an RTL environment in SwiftUI previews.

```swift
#Preview("RTL") {
    ContentView()
        .environment(
            \.layoutDirection,
            .rightToLeft
        )
}
```

This is useful for finding layout assumptions. But it is not a substitute for testing the actual application in a supported RTL language.

## 21. Accessibility and localization together

Now consider a transaction: "Sent to ravi@npay ₹1,500.50". The visual layout may be correct, but how will VoiceOver announce it? A financial application should provide meaningful accessible descriptions. For example:

```swift
TransactionRow(transaction: transaction)
    .accessibilityElement(children: .ignore)
    .accessibilityLabel(transaction.title)
    .accessibilityValue(
        Money.display(transaction.amountPaise)
    )
```

For a fully localized application, the accessibility label and value should also be localized appropriately.

**Important distinction.** Accessibility text should communicate meaning, not merely reproduce the visual arrangement.

## 22. Build a reusable accessible NPay action

Let's improve our design system.

```swift
import SwiftUI

struct NPayActionButton: View {
    let title: LocalizedStringKey
    let symbol: String
    let accessibilityID: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(title, systemImage: symbol)
                .font(.headline)
                .frame(maxWidth: .infinity)
                .padding()
        }
        .buttonStyle(.borderedProminent)
        .accessibilityIdentifier(accessibilityID)
    }
}
```

Usage:

```swift
NPayActionButton(
    title: "payment.send",
    symbol: "arrow.up.right",
    accessibilityID: "npay.sendPayment"
) {
    print("Send Money tapped")
}
```

**Why use LocalizedStringKey?** It allows the component to accept localized SwiftUI text content. **Why use accessibilityIdentifier?** It provides a stable identifier for UI automation. The identifier is not intended as a spoken label.

## 23. Xcode accessibility inspection

Xcode provides accessibility inspection and testing capabilities. A practical workflow is to run NPay in the Simulator, enable VoiceOver, and inspect the order in which elements are announced. You can also use Apple's Accessibility Inspector to examine labels, values, traits, and element relationships.

| Component | Expected accessibility behavior |
|---|---|
| BalanceCard | Announces available balance meaningfully |
| Send Money button | Announces its action |
| Payment TextField | Has a meaningful label |
| Transaction row | Announces transaction details |
| Success screen | Communicates success without relying only on animation |
| Tab bar | Exposes meaningful tab labels |

## 24. Accessibility identifiers for future UI tests

Let's define stable identifiers.

```swift
enum NPayAccessibilityID {
    static let balanceCard = "npay.balanceCard"
    static let recipientField = "npay.recipientField"
    static let amountField = "npay.amountField"
    static let sendButton = "npay.sendButton"
    static let transactionList = "npay.transactionList"
}
```

Use them consistently:

```swift
TextField("Recipient", text: $recipient)
    .accessibilityIdentifier(
        NPayAccessibilityID.recipientField
    )
```

We'll reuse these identifiers in Unit 9 when we write UI automation tests.

## 25. Senior engineer knowledge check

1. Does VoiceOver necessarily expose every SwiftUI layout container as a separate element? (Yes / No)
2. What is the purpose of accessibilityIdentifier? (Stable programmatic identification / Spoken VoiceOver label / Currency formatting)
3. Should changing NPay's language change its underlying monetary values? (Yes / No)
4. Why prefer leading and trailing alignment? (They adapt to semantic layout direction / They are always faster / They disable localization)
5. Is a LocalizedStringKey equivalent to every ordinary String? (Yes / No)
6. Should payment success rely only on a green animated checkmark? (Yes / No)

## Status note (from the text)

"Yes — Lesson 3.10 is conceptually complete!" Unit 3 progress: 10 of 12 lessons covered. Remaining: 3.11 SwiftUI
Performance, Lazy Loading & Profiling (next); 3.12 Complete Unit 3 Integration & Architecture Review. "The complete
integrated Xcode code for Lessons 3.7–3.10 is still pending." Next: Lesson 3.11 — rendering performance, LazyVStack,
unnecessary body evaluations, Instruments, and optimization techniques using NPay's transaction history.

## Integration through Lesson 3.10 (authored)

Applied to the Lesson 3.9 code and run in the simulator (`tools/sim3_10/App.swift`):
- **App/NPayAccessibilityID.swift**: the Section 24 enum.
- **BalanceCard**: `.accessibilityElement(children: .combine)` and `.accessibilityIdentifier(NPayAccessibilityID.balanceCard)`.
- **TransactionRow**: the Section 21 modifiers, applied inside the component so every use benefits.
- **PaymentsScreen**: identifiers on the recipient field, amount field and Review Payment button (`sendButton`).
- **HistoryScreen**: identifier on the List (`transactionList`).
- Not done: real labels for the text fields and the success checkmark (measured problems), and localizing the whole app.

```swift
// App/NPayAccessibilityID.swift (section 24)

enum NPayAccessibilityID {
    static let balanceCard = "npay.balanceCard"
    static let recipientField = "npay.recipientField"
    static let amountField = "npay.amountField"
    static let sendButton = "npay.sendButton"
    static let transactionList = "npay.transactionList"
}
```

```swift
struct TransactionRow: View {
    let transaction: Transaction

    var body: some View {
        HStack(spacing: 12) {
            Image(
                systemName: transaction.amountPaise >= 0
                    ? "arrow.down.left"
                    : "arrow.up.right"
            )
            .font(.title2)
            .foregroundStyle(
                transaction.amountPaise >= 0
                    ? Color.green
                    : Color.blue
            )

            VStack(alignment: .leading, spacing: 4) {
                Text(transaction.title)
                    .font(.headline)

                Text(
                    transaction.date,
                    format: .dateTime
                        .day()
                        .month(.abbreviated)
                )
                .font(.caption)
                .foregroundStyle(.secondary)
            }

            Spacer()

            Text(Money.display(transaction.amountPaise))
                .font(.subheadline.bold())
                .foregroundStyle(
                    transaction.amountPaise >= 0
                        ? Color.green
                        : Color.primary
                )
        }
        .padding(.vertical, 8)
        // section 21: one element, read as meaning rather than layout
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(transaction.title)
        .accessibilityValue(
            Money.display(transaction.amountPaise)
        )
    }
}
```

### Localizable.xcstrings (the lab's catalog; translations are ours and need native-speaker review)

```json
{
  "sourceLanguage" : "en",
  "strings" : {
    "balance.available" : {
      "comment" : "Title above the balance amount",
      "localizations" : {
        "en" : { "stringUnit" : { "state" : "translated", "value" : "Available Balance" } },
        "hi" : { "stringUnit" : { "state" : "translated", "value" : "उपलब्ध बैलेंस" } },
        "ta" : { "stringUnit" : { "state" : "translated", "value" : "கிடைக்கும் இருப்பு" } }
      }
    },
    "payment.send" : {
      "comment" : "Primary action: start a payment",
      "localizations" : {
        "en" : { "stringUnit" : { "state" : "translated", "value" : "Send Money" } },
        "hi" : { "stringUnit" : { "state" : "translated", "value" : "पैसे भेजें" } },
        "ta" : { "stringUnit" : { "state" : "translated", "value" : "பணம் அனுப்பு" } }
      }
    },
    "transactions.recent" : {
      "comment" : "Section header for the latest transactions",
      "localizations" : {
        "en" : { "stringUnit" : { "state" : "translated", "value" : "Recent Transactions" } },
        "hi" : { "stringUnit" : { "state" : "translated", "value" : "हाल के लेन-देन" } },
        "ta" : { "stringUnit" : { "state" : "translated", "value" : "சமீபத்திய பரிவர்த்தனைகள்" } }
      }
    }
  },
  "version" : "1.0"
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_10.py`, 35 slides) covers Sections 15–25 (Part 1 not shared), grouped into
6 Parts: localization at runtime (15, 16), money and locale (17, 18), right-to-left (19, 20), accessibility meets
localization (21, 23), built for every user (22, 24), NPay after 3.10 (integration and the text's status note); then
recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_10/`, rerun with `sh tools/sim3_10/run.sh`; the String
Catalog is compiled into the app with `xcstringstool`; languages via `-AppleLanguages` / `-AppleLocale`; RTL via the
pseudolanguage arguments `-AppleTextDirection YES -NSForceRightToLeftWritingDirection YES`; accessibility elements
printed with label, value, traits and identifier)
- English, Tamil and Hindi lab screens: the literal and `LocalizedStringKey(title)` resolve; `Text(title)` with a String
  shows "payment.send" in every language; NPayActionButton shows the translated title with id `npay.sendPayment`.
- Currency (Mac): the text's example prints ₹1,500.50 twice; added locales and amount: en_IN ₹1,23,45,678.50 vs en_US
  ₹12,345,678.50, de_DE 1.500,50 ₹, fr_FR 1 500,50 ₹, ar_SA Arabic-Indic digits; manual "₹\(amount)" gives ₹1500.5.
- RTL: layoutDirection reads rightToLeft under the pseudolanguage; Home mirrors (tabs, quick actions, rows, leading
  text) under both the environment override and the pseudolanguage; `arrow.up.right` symbols are not mirrored.
- Accessibility: plain row = 4 elements ("arrow.up.right" image, title, amount, date); Section 21 row = 1 element with
  label and value; card 3 texts vs combined; Payments text fields have an empty label with the placeholder as value; the
  success checkmark is announced as "Selected"; tab bar labels and selected state; all five identifiers present.

**Authored (flagged)**
- The String Catalog and its Tamil/Hindi translations; the integration (above); the RTL pseudolanguage and environment
  runs on the full app; the element dumps; the extra locales and amounts.
- Section 16's pipeline as a diagram (shared as a list); the measured column in the Section 23 table.
- Review: the text's 6 questions (options reordered) plus three predict items (Text(title) in Tamil; the checkmark's
  announcement; en_IN grouping) and a spaced item from 3.9; 4 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.11 and 3.12 from the status note; Unit 9 as Section 24
  says), lab, end slide.
- The Unit 3 strip now has 12 lessons (the status note); the strip shrinks labels longer than nine characters in narrow
  boxes (this also fixed Unit 2's clipped "@ViewBuilder" label).

**Wording**
- "Senior engineer insight / knowledge check" became neutral callouts and "Check your understanding".
