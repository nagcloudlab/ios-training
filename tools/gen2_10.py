"""Generates decks/unit-2/lesson-2.10/index.html from the Lesson 2.10 text (ForEach, List & Collection Identity).
The text came in three pieces (Sections 1-14, 14-23, complete code), grouped into 8 Parts. Console output and
screenshots come from tools/sim2_10 (a scripted SwiftUI app run in the iOS Simulator; buttons activated through
accessibility); the compiler error and the computed-id demo were run with swiftc; interface lines from the iOS 26.5 SDK."""
import html, os, re, sys
OUT210 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.10', 'ForEach, List &amp;<br>Collection Identity',
            'NPay shows 100 transactions. One is inserted. How does SwiftUI know <b>which row is which</b>?',
            'NPay can show and edit a balance. A payment app needs transaction history. Today: SwiftUI&rsquo;s collection system, ForEach, List and Identifiable, and the idea underneath them, stable identity. We will flag a row, insert a transaction, and watch the flag stay put, move to the wrong row, or vanish, depending only on how identity is defined. All of it measured in the iOS Simulator.')
outcomes_slide('2.10', [("code", "Why a <code>for</code> loop won&rsquo;t work; what <code>ForEach</code> is"),
                        ("link", "<code>Identifiable</code> and <b>stable</b> IDs"),
                        ("diff", "Position vs <b>identity</b>: what indices get wrong"),
                        ("eye", "Why <code>var id: UUID {{ UUID() }}</code> is a bug"),
                        ("layers", "ForEach vs List; <b>eager</b> vs <b>lazy</b>"),
                        ("check", "NPay&rsquo;s first <b>transaction history</b>")])
S[-1] = S[-1].replace('{{', '{').replace('}}', '}')
where_slide('2.10', 'Today: transaction history', (),
            '2.9: one balance, shown by a card and edited through a binding.',
            'A collection: many rows, each with its own <b>identity</b>.',
            'So far every view described one thing. Today a view describes a whole collection of transactions, and SwiftUI has to tell the rows apart as the collection changes.',
            'The milestone.')

# ================================================================== Part 1 (1)
divider(1, "Transaction history", "Many rows, one screen", 'NPay needs a list of recent transactions.', 'The target.')
S.append(slide("Part 1 &middot; Our next NPay milestone (section 1)", "Milestone 2.10: recent transactions", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 180px 180px 180px;gap:24px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Add", ul("<b>Recent Transactions</b> below the actions", "Mock data first, then <b>dynamic</b>"))}
        {card("Rows", ul("Coffee Shop &minus;₹250", "Electricity Bill &minus;₹1,200", "Salary Credit +₹45,000"))}
      </div>
      {PHONE("img/before.png", "Before: 2.9", 180)}
      <div class="step">{PHONE("img/bottom.png", "After, scrolled down", 180)}</div>
      <div class="step">{PHONE("img/added.png", "+ Add Demo Transaction", 180)}</div>
    </div>
  </div>""", notes(('SAY', 'Where 2.9 ended: balance card, editor, quick actions. The milestone: a Recent Transactions section with mock data, first static, then dynamic.'),
                  ('SAY', 'Click: today&rsquo;s result, scrolled to the bottom: three rows with a credit card icon, title, date and amount; the salary credit in green. Click: and after Add Demo Transaction, Mobile Recharge appears at the top of the list.'),
                  ('CONNECT', 'Start with the simplest collection: an array of strings.'))))

# ================================================================== Part 2 (2-4)
divider(2, "ForEach", "A view for a collection", 'A for loop works in Swift. Does it work in a ViewBuilder?', 'Try it.')
FL = """VStack {
    for transaction in transactions {
        Text(transaction)
    }
}"""
FE = """VStack {
    ForEach(transactions, id: \\.self) { transaction in
        Text(transaction)
    }
}"""
S.append(slide("Part 2 &middot; Display a Swift array (section 2)", "Not <code>for</code>: <code>ForEach</code>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Doesn&rsquo;t compile", FL, "font-size:16px")}
        <div class="step" style="margin-top:10px">{err("closure containing control flow statement cannot be used with result builder &lsquo;ViewBuilder&rsquo;")}<p class="small muted" style="margin:4px 0 0">swiftc, iOS 26.5 SDK</p></div></div>
      <div>{code("Works", FE, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{card("id: \\.self", ul("Each element needs an <b>identity</b>", "Unique strings can be their own ID", "Duplicates or changes: trouble (Part 5)"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'An array of three transaction names, from Unit 01. Can we loop over it inside a VStack with a normal for statement? Click: no. The compiler says a closure containing a control flow statement cannot be used with the result builder ViewBuilder: the builder from 2.3 does not accept this kind of loop as a way to produce child views.'),
                  ('SAY', 'Instead, SwiftUI provides ForEach: it creates a view description for each element. Click: id: \\.self tells SwiftUI what identifies each element: here the string itself. That works for unique strings; with duplicate or changing values it becomes a problem, as Part 5 shows.'),
                  ('CONNECT', 'What is ForEach?'))))

FDECL = """// iOS 26.5 SDK (excerpts)
public struct ForEach<Data, ID, Content>
    where Data : RandomAccessCollection, ID : Hashable

extension ForEach : View where Content : View

extension ForEach where ID == Data.Element.ID,
    Content : View, Data.Element : Identifiable {
    public init(_ data: Data,
        @ViewBuilder content: @escaping (Data.Element) -> Content)
}"""
S.append(slide("Part 2 &middot; What exactly is ForEach? (section 3)", "A generic view: Data, ID, Content", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:28px;align-items:start">
      <div>{code("Interface", FDECL, "font-size:12.5px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Three generic types", ul("<b>Data</b>: the collection", "<b>ID</b>: the identity, <code>Hashable</code>", "<b>Content</b>: the view per element"))}
        <div class="step">{console("type(of:) in the simulator", ["ForEach&lt;Array&lt;String&gt;, String, Text&gt;", "ForEach&lt;Array&lt;Transaction&gt;, UUID,", "        TransactionRow&gt;"], 13)}</div>
        <div class="rule step" data-label="Not a for loop">{ul("A <b>view</b> describing child views <b>and their identities</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'ForEach is a generic struct with three type parameters: Data, the collection, which must be a RandomAccessCollection; ID, the identity type, which must be Hashable; and Content, the view produced for each element. In the SDK it conforms to View when Content does, and it has an initializer for Identifiable elements that we use in a moment. Generics as in Unit 01&rsquo;s generic printValue function, applied to UI.'),
                  ('SAY', 'Click: the printed types make the three parameters concrete: for the strings, ForEach of Array of String, String, Text. For transactions later: ForEach of Array of Transaction, UUID, TransactionRow.'),
                  ('SAY', 'Click: so ForEach is not just a for loop. It is a view that represents a collection of child views together with their identities.'),
                  ('CONNECT', 'How does it turn an array into views?'))))

FP = [("db", "Swift array", "the transaction values"), ("link", "ForEach", "pairs each element with an identity"), ("code", "Content closure", "Text(transaction) per element"),
      ("layers", "Collection hierarchy", "child views tracked by identity"), ("frame", "Layout and rendering", "what you see")]
P = []
for i, (ic, t, sub) in enumerate(FP):
    x = i * 232
    P.append(tall(x, 0, 208, 120, ic, t, sub, str(i + 1) if i < 4 else '5+'))
    if i < 4:
        P.append(wire(f'M{x + 210} 60H{x + 228}' + head(x + 228, 60, 'r')))
S.append(slide("Part 2 &middot; How ForEach creates child views (section 4) &middot; conceptual", "Array in, identified views out", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1136 120', 'Array, ForEach pairs elements with identities, content closure, collection hierarchy, layout and rendering', 'fe', P, 'max-height:150px')}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Selective">{ul("SwiftUI may run content closures <b>selectively</b>: the container decides (Part 6)")}</div>
  </div>""", notes(('SAY', 'Conceptually. Click: the Swift array holds the values. Click: ForEach associates each element with an identity. Click: the content closure produces a view description for an element. Click: SwiftUI tracks the child views by identity. Click: layout and rendering show the result.'),
                  ('SAY', 'Click: SwiftUI may evaluate content closures selectively, depending on the container; Part 6 measures exactly that.'),
                  ('CONNECT', 'Strings are not enough for a payment app. Build a model.'))))

# ================================================================== Part 3 (5-6)
divider(3, "Transaction and Identifiable", "Identity is part of the model", 'Two transactions can look the same. They are still different transactions.', 'The model.')
MODEL = """struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amount: Int
    let date: String
}

ForEach(transactions) { transaction in   // no id: needed
    Text(transaction.title)
}"""
S.append(slide("Part 3 &middot; Transaction and Identifiable (sections 5&ndash;6)", "Identity belongs to the transaction", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Transaction.swift", MODEL, "font-size:14px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Why an id", ul("Same title, amount and date <b>can</b> happen twice", "Identity = the transaction, not its <b>display</b>"))}
        <div class="step">{card("Identifiable", ul("A Swift protocol: has an <code>id</code>", "ForEach uses it: no <code>id: \\.id</code>"))}</div>
        <div class="rule step" data-label="Automatic UUID?">{ul("<b>No</b>: the model must provide a suitable ID", "Ours stores one")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A real Transaction struct, from Unit 01&rsquo;s structs: id, title, amount and date. Why an id? Because two transactions can have the same title, amount and date, say two coffees on the same day. Identity should represent the transaction itself, not what it looks like on screen.'),
                  ('SAY', 'Click: Swift&rsquo;s Identifiable protocol says a type exposes an id. Once Transaction conforms, ForEach can use that id directly: no id: \\.id argument, as the SDK initializer on the previous slide showed.'),
                  ('SAY', 'Click: does Identifiable create a UUID for you? No. The model must provide a suitable value; ours stores one. Where it comes from matters a lot, as Part 5 shows.'),
                  ('CONNECT', 'Now the deepest idea of the lesson: stable identity.'))))

# ================================================================== Part 4 (7-8, 14-15)
divider(4, "Stable identity", "Position is not identity", 'A new transaction arrives at the top.', 'Compare the tables.')
T1 = [("0", "TXN-101", "Coffee Shop"), ("1", "TXN-102", "Electricity Bill"), ("2", "TXN-103", "Salary Credit")]
T2 = [("0", "<b>TXN-104</b>", "<b>Mobile Recharge</b>"), ("1", "TXN-101", "Coffee Shop"), ("2", "TXN-102", "Electricity Bill"), ("3", "TXN-103", "Salary Credit")]
S.append(slide("Part 4 &middot; Stable identity (sections 7&ndash;8, 15)", "Coffee Shop moved; it&rsquo;s still TXN-101", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div><p class="kicker" style="margin:0 0 6px;color:var(--muted)">Before</p>{tbl(["Index", "ID", "Title"], T1)}</div>
      <div class="step"><p class="kicker" style="margin:0 0 6px;color:var(--muted)">After inserting at 0</p>{tbl(["Index", "ID", "Title"], T2)}</div>
    </div>
    <div class="cols step" style="{TWO};gap:24px;margin-top:14px">
      {card("Indices", ul("<b>Positions</b>: every row below shifted by one"))}
      {card("IDs", ul("<b>Identities</b>: unchanged; one new ID appeared"))}
    </div>
    <div class="rule step" data-label="Careful" style="margin-top:12px">{ul("SwiftUI&rsquo;s exact diffing isn&rsquo;t public; stable identity is the requirement")}</div>
  </div>""", notes(('SAY', 'NPay receives transactions from an API: TXN-101 Coffee Shop at index 0, 102 at 1, 103 at 2. Click: then TXN-104, Mobile Recharge, arrives at the top.'),
                  ('SAY', 'Click: compare. Every index changed: Coffee Shop moved from 0 to 1. But every ID stayed the same, and one new ID appeared. With stable IDs SwiftUI can tell that one element was inserted and the others are the same transactions in new positions. The text&rsquo;s explorer made the same point: position and identity are different things.'),
                  ('SAY', 'Click: do not claim SwiftUI uses one particular public diffing algorithm; its internals are not specified. What is certain is that stable identity is the requirement for predictable collection behaviour.'),
                  ('CONNECT', 'What happens step by step when the transaction arrives?'))))

UP = [("db", "Transaction arrives", "stable ID, e.g. TXN-104"), ("diff", "State array changes", "transactions.insert(_:at: 0)"),
      ("eye", "Dependent body re-evaluated", "a new ForEach description"), ("link", "Match by ID", "101-103: same rows; 104: new"),
      ("layout", "Layout", "rows below move down"), ("frame", "Rendered", "Mobile Recharge on top")]
P = [box(0, i * 52, 600, 44, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(UP)]
S.append(slide("Part 4 &middot; When a transaction arrives (section 14) &middot; conceptual", "Insert one; the rest keep their identity", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      {svg('0 0 600 304', 'Transaction arrives, array changes, body re-evaluated, matched by ID, layout, rendered', 'up', P, 'max-height:330px')}
      <div class="rule step" data-label="Two concerns">{ul("<b>Identity</b> keeps row state attached", "It doesn&rsquo;t promise a row&rsquo;s <code>body</code> never runs")}</div>
    </div>
  </div>""", notes(('SAY', 'Conceptual, and only the first stage was in the text&rsquo;s widget. Click: a transaction with a stable ID arrives. Click: the state array changes. Click: the view that depends on the array is re-evaluated, giving a new ForEach description. Click: by ID, the existing three are the same elements and 104 is new. Click: layout moves the old rows down. Click: Mobile Recharge is rendered at the top.'),
                  ('SAY', 'Click: two separate concerns. Stable identity keeps the association between a transaction and its view state; it does not guarantee that a row&rsquo;s body is never evaluated again. Identity preservation and view evaluation are different things.'),
                  ('CONNECT', 'We tested what goes wrong without stable identity.'))))

# ================================================================== Part 5 (9-10, 16)
divider(5, "When identity breaks", "Indices and computed UUIDs", 'Flag Coffee Shop, insert a transaction, see where the flag goes.', 'Three ways.')
FR = """// FlagRow has  @State private var flagged = false
ForEach(items) { FlagRow(title: $0.title) }               // 1
ForEach(items.indices, id: \\.self) { i in                 // 2
    FlagRow(title: items[i].title) }
// 3: same as 1, but  var id: UUID { UUID() }"""
S.append(slide("Part 5 &middot; Stable ID, index, computed UUID (sections 9&ndash;10, 15&ndash;16)", "Flag Coffee Shop, then insert at the top", f"""  <div class="body">
    {code("The experiment", FR, "font-size:12.5px")}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start">
      <div>{crop("img/stable.png", "1 Stable id: flag stays on Coffee Shop", 330)}</div>
      <div class="step">{crop("img/index.png", "2 Index: flag jumps to Mobile Recharge", 330)}</div>
      <div class="step">{crop("img/unstable.png", "3 Computed UUID: flag lost", 330)}</div>
    </div>
  </div>""", notes(('SAY', 'Each row has its own @State, a flag, the kind of row-local state a real list has: a selection, an expanded row, a text field. Three lists of the same three transactions: one with stable IDs, one using array indices as identity, one with an id that is computed as UUID() on every read. In each, we flagged Coffee Shop and then inserted Mobile Recharge at the top.'),
                  ('SAY', 'Left, stable ID: the flag stayed on Coffee Shop, which moved down. Click: middle, indices: the flag stayed at index 0, so it now sits on Mobile Recharge, a transaction the user never flagged. A real bug: positions referred to a different logical transaction. Click: right, computed UUID: every read produced a new id, so every row looked new, and the flag vanished.'),
                  ('CONNECT', 'The console shows the same thing from the inside.'))))

S.append(slide("Part 5 &middot; What the rows reported (sections 9&ndash;10, 16)", "Who is flagged after the insert?", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start">
      {console("1 Stable id", ["row Mobile Recharge: flagged = false", "(only the new row&rsquo;s body ran)"], 13)}
      <div class="step">{console("2 Index", ["row Mobile Recharge: flagged = true", "row Coffee Shop: flagged = false", "…"], 13)}</div>
      <div class="step">{console("3 var id: UUID {{ UUID() }}", ["row Mobile Recharge: flagged = false", "row Coffee Shop: flagged = false", "… all rows fresh"], 13)}</div>
    </div>
    <div class="cols step" style="{TWO};gap:24px;margin-top:14px">
      {console("Plain Swift (Mac): read the id twice", ["computed: id == id → false", "stored:   id == id → true"], 13)}
      <div class="rule" data-label="Rule">{ul("Dynamic domain data: <b>stable domain IDs</b>", "From the API, not the index or a fresh UUID", "Indices for <b>presentation</b> only")}</div>
    </div>
  </div>""".replace('{{', '{').replace('}}', '}'), notes(('SAY', 'Inside, each row printed its state when its body ran. With stable IDs, after the insert only one body ran: the new Mobile Recharge row, unflagged; Coffee Shop kept its flag without even being re-evaluated. Click: with indices, every row was re-evaluated and Mobile Recharge reported flagged = true. Click: with the computed UUID, every row was re-created fresh: all false.'),
                  ('SAY', 'Click: why the computed id fails, in plain Swift on a Mac: reading a computed id twice gives two different UUIDs; a stored id is equal to itself. Possible consequences, as the text says: lost row state, odd transitions, wasted updates.'),
                  ('SAY', 'The rule: for dynamic domain collections use stable domain IDs. For NPay, the transaction ID comes from the model and the trusted backend, not from the array index and not from a UUID generated every time data is decoded, which would make the same transaction look new on every refresh. Indices are fine for presentation, such as deciding where to draw a divider, but never as identity.'),
                  ('CONNECT', 'Next: ForEach or List?'))))

# ================================================================== Part 6 (11, 17)
divider(6, "ForEach vs List", "And eager vs lazy", 'ForEach makes children. List is a list.', 'Compare, then measure.')
CMP = [("Role", "generates child view descriptions", "presents a list interface"), ("Scrolling", "not by itself", "built in"),
       ("Row styling", "decided by the parent", "list-specific"), ("Editing", "depends on the parent", "built-in capabilities"), ("Identity", "important", "important")]
S.append(slide("Part 6 &middot; ForEach versus List (sections 11, 17)", "And which rows actually get built", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:28px;align-items:start">
      <div>{tbl(["", "ForEach", "List"], CMP)}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("1,000 transactions: row bodies evaluated", ["ScrollView { VStack { ForEach } }:  1000", "ScrollView { LazyVStack { ForEach } }:  12", "List:  9"], 13)}</div>
        <div class="rule step" data-label="So">{ul("<b>ForEach</b> doesn&rsquo;t decide laziness", "The <b>container</b> does: eager VStack, lazy List / LazyVStack")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'ForEach generates child view descriptions; it does not scroll by itself, and its rows are styled by whatever contains them. List is a higher-level container that presents a list: built-in scrolling, list styling, and capabilities like selection, swipe actions and editing. Both depend on identity.'),
                  ('SAY', 'Click: Section 17 says an ordinary VStack builds its children eagerly and List or lazy containers suit large collections. We measured it: 1,000 transactions, a counter in each row&rsquo;s body. Inside a plain VStack in a ScrollView: all 1,000 row bodies evaluated at launch. In a LazyVStack: 12, the rows on screen plus a few. In a List: 9.'),
                  ('SAY', 'Click: so ForEach itself does not guarantee lazy creation; the surrounding container decides. That is why NPay&rsquo;s short history can live in the existing ScrollView&rsquo;s VStack, but a full history should use List or a lazy stack. We do not nest a List inside our ScrollView, to avoid two competing scroll containers.'),
                  ('CONNECT', 'Build NPay&rsquo;s history.'))))

# ================================================================== Part 7 (12-13, 18-20)
divider(7, "NPay&rsquo;s transaction history", "Milestone 2.10", 'A row view, a history view, and a button that inserts.', 'The row.')
ROW = """struct TransactionRow: View {
    let transaction: Transaction

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "creditcard")
                .font(.title2).foregroundStyle(.blue)
            VStack(alignment: .leading, spacing: 4) {
                Text(transaction.title).font(.headline)
                Text(transaction.date).font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            Text(transaction.amount, format: .currency(code: "INR")
                     .precision(.fractionLength(0)))
                .font(.subheadline.bold())
                .foregroundStyle(transaction.amount >= 0
                                 ? Color.green : Color.primary)
        }
        .padding(.vertical, 8)
    }
}"""
S.append(slide("Part 7 &middot; A reusable TransactionRow (section 12)", "Everything from 2.1&ndash;2.9 in one row", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:28px;align-items:start">
      {code("TransactionRow.swift", ROW, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Reused", ul("<b>HStack</b> and <b>VStack</b>", "<b>Spacer</b> before the amount", "<b>Currency</b> format", "<b>Conditional</b> colour", "A custom <b>view</b>"))}
      </div>
    </div>
  </div>""", notes(('SAY', 'TransactionRow puts the lessons together: an HStack with a credit card symbol, a leading VStack with the title and a secondary date, a Spacer pushing the amount to the trailing edge, the amount formatted as INR with no decimals, green when it is a credit and the primary colour otherwise, and vertical padding. A reusable view, like BalanceCard. Some modifiers are joined on one line here to fit; the full code is in the lesson text.'),
                  ('CONNECT', 'Then the history view and the button that inserts.'))))

HIST = """struct TransactionHistory: View {
    let transactions: [Transaction]       // display only

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Transactions").font(.headline)
            ForEach(transactions) { transaction in
                TransactionRow(transaction: transaction)
                Divider()
            }
        }
    }
}

// ContentView: @State transactions, then
Button("Add Demo Transaction") { addDemoTransaction() }
// inserts Mobile Recharge (-399) at index 0
TransactionHistory(transactions: transactions)"""
S.append(slide("Part 7 &middot; Make it dynamic (sections 13, 18&ndash;20)", "TransactionHistory and Add Demo Transaction", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) 170px 170px;gap:22px;align-items:start">
      <div>{code("TransactionHistory.swift", HIST, "font-size:12px")}</div>
      {PHONE("img/bottom.png", "Three rows", 170)}
      <div class="step">{PHONE("img/added.png", "After Add: Mobile Recharge on top", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'TransactionHistory is a display component: a headline and a ForEach of TransactionRows, each followed by a Divider. It takes let transactions because it only displays them; ContentView owns the @State array, the same principle as BalanceCard and BalanceEditor in 2.9.'),
                  ('SAY', 'ContentView gets @State transactions with the three mock transactions, an Add Demo Transaction button that inserts Mobile Recharge, minus 399, at index 0, and TransactionHistory(transactions:). On the right, scrolled to the bottom at launch, and click, after the button: Mobile Recharge on top, the other three moved down with their identities intact.'),
                  ('SAY', 'Note the divider inside ForEach: it also draws one under the last row, acceptable for a demo. If you fix that with indices, use them for presentation only, never as identity. And the transaction does not change the balance yet: the two are independent demos until later lessons connect them.'),
                  ('CONNECT', 'Last: what do the rows report when one is inserted?'))))

# ================================================================== Part 8 (21, 23)
divider(8, "Observe updates", "And the architecture so far", 'Ask each row why its body ran.', '_printChanges.')
PC = """var body: some View {
    let _ = Self._printChanges()

    return HStack {
        Text(transaction.title)
        Spacer()
        Text("\\(transaction.amount)")
    }
}"""
TREE = """ContentView
├── @State balance
├── @State transactions
├── BalanceCard          let balance: Int
├── BalanceEditor        @Binding balance
├── QuickAction × 3      action: () -> Void
└── TransactionHistory   let transactions
    └── ForEach(transactions)
        └── TransactionRow"""
S.append(slide("Part 8 &middot; Observe row updates; checkpoint (sections 21, 23)", "One insert, one new row evaluated", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("TransactionRow (temporary)", PC, "font-size:13.5px")}
        <div class="step" style="margin-top:10px">{console("Launch, then Add (test row: ChangesRow)", ["ChangesRow: @self changed.  ×3   (launch)", "ChangesRow: @self changed.  ×1   (the new row)"], 13)}</div></div>
      <div>{code("NPay after 2.10", TREE, "font-size:13px")}
        <div class="rule step" data-label="Learn" style="margin-top:10px">{ul("Use diagnostics to <b>understand</b>, not to panic", "Evaluation &ne; destroyed &ne; redrawn")}</div></div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s diagnostic: _printChanges in the row&rsquo;s body. Click: at launch, three rows reported @self changed: new rows. After Add Demo Transaction, exactly one more line: the new row. With stable IDs the three existing rows were not even re-evaluated in this run. SwiftUI may re-evaluate rows when collection state changes; here it did not need to.'),
                  ('SAY', 'Click: the lesson&rsquo;s point stands either way: a body evaluation does not mean a row was destroyed or completely redrawn. Use diagnostics to understand behaviour, not to assume every evaluation is a performance problem.'),
                  ('SAY', 'The architecture after 2.10: ContentView owns the balance and the transactions; BalanceCard reads a value, BalanceEditor has a binding, the quick actions take closures, and TransactionHistory displays the collection through ForEach and TransactionRow. Test in Xcode: plus and minus, the three actions printing, Add Demo Transaction inserting at the top, and scrolling to the bottom.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.10', (), [("link", "ForEach = views + identities", "a view, not a for loop"),
                      ("diff", "Identity ≠ position", "stable IDs; never indices or fresh UUIDs"),
                      ("layers", "The container decides", "VStack eager; List, LazyVStack lazy")],
         'Three things to remember. ForEach is a view that pairs each element of a collection with an identity and produces a child view for it. Identity is not position: use stable domain IDs, because indices moved our flag to the wrong transaction and a computed UUID lost it. And ForEach does not decide how many rows are built: the container does, all 1,000 in a VStack, about a dozen in a List or LazyVStack.')

review_divider(8)
review([("link", "Choose one", "What does ForEach need to track dynamic elements?",
         "What does <code>ForEach</code> need to track dynamic elements correctly?<br>A. Stable identity<br>B. Only the array index<br>C. A separate thread", "A",
         "With stable IDs the flag stayed on Coffee Shop after the insert.",
         "Using position as identity.", "Most pick A.", None),
        ("layers", "Choose one", "Which provides scrolling by itself?",
         "Which of these provides scrolling by itself?<br>A. <code>ForEach</code><br>B. <code>List</code><br>C. Both", "B",
         "ForEach only generates children; List is a scrolling list container.",
         "Treating ForEach as a list.", "Some pick C.", None),
        ("diff", "Question", "Is var id: UUID { UUID() } safe?",
         "Is a computed <code>id</code> that returns <code>UUID()</code> on every access safe?", "No",
         "Two reads gave two IDs; in the list the flag was lost after one insert.",
         "Thinking any UUID is a stable ID.", "Some say yes.", None),
        ("frame", "Choose one", "What decides lazy row creation?",
         "What decides whether 1,000 rows are built eagerly or lazily?<br>A. <code>ForEach</code><br>B. The surrounding container<br>C. <code>Identifiable</code>", "B",
         "VStack built 1,000 row bodies; LazyVStack 12; List 9.",
         "Assuming ForEach is lazy.", "Some pick A.", None),
        ("file", "Question", "Should read-only TransactionHistory own a copy of the state?",
         "Should a read-only <code>TransactionHistory</code> own an independent copy of mutable transaction state?", "No",
         "The parent owns it; the history takes <code>let transactions</code>.",
         "Duplicating state in children (2.9).", "Some say yes.", None),
        ("eye", "Question", "Does stable identity guarantee body never runs again?",
         "Does stable identity guarantee that a row&rsquo;s <code>body</code> never runs again?", "No",
         "Identity keeps state attached; evaluation is a separate concern.",
         "Confusing identity with evaluation.", "Some say yes.", None),
        ("db", "Predict the result", "Index-based ForEach: flag Coffee Shop, insert at 0. Which row is flagged?",
         "<code>ForEach(items.indices, id: \\.self)</code>. You flag Coffee Shop (index 0), then insert Mobile Recharge at index 0. Which row shows the flag?<br>A. Coffee Shop<br>B. Mobile Recharge<br>C. None", "B",
         "The state stayed with index 0, which is now Mobile Recharge.",
         "Assuming the flag follows the transaction.", "Many pick A.", None),
        ("link", "Choose one", "From 2.9: what should a display-only child receive?",
         "From Lesson 2.9: what should a child that only <b>displays</b> the balance receive?<br>A. A <code>Binding&lt;Int&gt;</code><br>B. A plain value<br>C. Its own <code>@State</code> copy", "B",
         "Give only the access needed; TransactionHistory follows the same rule.",
         "Handing out bindings by default.", "Some pick A.", "Spaced review from Lesson 2.9.")])

S.append(next_slide('2.10', [("2.11", "TextField, input validation &amp; focus", "a payment amount: keyboard &rarr; binding &rarr; state"),
                             ("Later", "Connecting it up", "transactions that change the balance")],
                    'Next lesson adds a payment amount input: how text travels from the iOS keyboard through a SwiftUI binding into state, with validation, focus and keyboard behaviour. Connecting transactions to the balance comes after that.'))

S.append(lab_slide('2.10', "Break identity on purpose", "Predict first, then run.",
                   ["Try a <code>for</code> loop in a VStack; read the error.",
                    "Build Transaction, TransactionRow, TransactionHistory.",
                    "Add a <code>@State</code> flag to the row; flag one; insert at 0.",
                    "Switch to <code>indices</code>, then to a computed <code>UUID()</code>.",
                    "Add <code>_printChanges</code> to the row; tap Add.",
                    "Try 1,000 rows in VStack, LazyVStack, List."],
                   "", 'Expected, as in our runs: "closure containing control flow statement cannot be used with result builder &lsquo;ViewBuilder&rsquo;"; stable IDs keep the flag on its transaction, indices move it to the new first row, a computed UUID loses it; _printChanges prints once for the new row; about 1,000 vs a dozen row bodies.',
                   side=f'<div>{card("You hand in", ul("Three screenshots of the flag experiment", "One sentence: position vs identity", "Your row-body counts"))}</div>'))

end_slide('2.10', 'ForEach, List &amp;<br>Collection Identity', 'Lesson 2.11 &mdash; TextField, Input Validation &amp; Focus',
          'You can now explain why ForEach replaces a for loop in a ViewBuilder, what its Data, ID and Content types are, why Identifiable and stable domain IDs matter, what goes wrong with indices or a computed UUID, how ForEach differs from List and why the container decides laziness, and how NPay&rsquo;s transaction history is built.',
          'Next, Lesson 2.11: TextField, input validation and focus management. A payment amount input, from the keyboard through a binding into state.')

write_deck(OUT210, '2.10', 'ForEach, List &amp; Identity', 'ForEach, List &amp; Identity')
