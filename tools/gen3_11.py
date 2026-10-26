"""Generates decks/unit-3/lesson-3.11/index.html from the Lesson 3.11 text (SwiftUI Performance, Lazy Loading & Rendering
Internals; Sections 1-25 in two parts). Evidence comes from tools/sim3_11: rows evaluated and memory footprint for VStack,
LazyVStack and List with 10,000 records, stable vs computed ids, Observation reads, _printChanges, sorts and filters per
keystroke over 50,000 records, and display frames during a synchronous load. Counts are the point; the few durations are
labelled as simulator runs (Debug build) and are not benchmarks."""
import html, os, re, sys
OUT311 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

SIM = 'iPhone 17 simulator, Debug build'

title_slide('3.11', 'SwiftUI Performance<br>&amp; Lazy Loading',
            'NPay with <b>50,000 transactions</b>: why History can stutter, and how to find out instead of guessing.',
            'Imagine NPay has 50,000 transactions. The user opens History, scrolls quickly, searches for an older payment, and the interface stutters. Why, and how do we diagnose it instead of randomly changing code? Today: SwiftUI&rsquo;s update pipeline, eager versus lazy containers, view identity, Observation, expensive work in body, and measuring. We ran every experiment in the text in the simulator, and we count things: rows built, sorts run, frames delivered. Counts tell the story without pretending to be device benchmarks.')
outcomes_slide('3.11', [("layers", "Separate state, evaluation, layout, rendering and display"),
                        ("diff", "Choose between VStack, LazyVStack and List"),
                        ("db", "Tell data loading from view creation"),
                        ("key", "Keep identity stable and reads narrow"),
                        ("clock", "Keep expensive work out of body and off the main actor"),
                        ("eye", "Measure first: observe, measure, change one thing")])
where_slide('3.11', 'Today: a fast History with 50,000 records', (),
            '3.10: localization, RTL and accessibility.',
            'Performance: lazy containers, identity, measuring.',
            'Lesson 3.10 made NPay usable by every user, in every language. Today NPay has to stay smooth when the data gets large. The History screen is our laboratory. One lesson after this one: 3.12 brings all of Unit 3 together.',
            'The milestone.')

# ================================================================== Part 1 (1, 2)
divider(1, "What &ldquo;slow&rdquo; means", "Performance is more than rendering", 'Several kinds of work, at several stages.', 'The milestone.')
WL = [("1,000", "fine in any container"), ("10,000", "the eager container starts to matter"), ("50,000", "data, sorting and filtering matter too")]
S.append(slide("Part 1 &middot; Our NPay performance milestone (section 1)", "Same rows, three containers, growing data", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Containers we compare", ul("<code>ScrollView</code> + <code>VStack</code> + <code>ForEach</code>", "<code>ScrollView</code> + <code>LazyVStack</code> + <code>ForEach</code>", "<code>List</code>"))}
        <div class="step">{tbl(["Records", "What the text expects"], WL)}
          <p class="small muted" style="margin:6px 0 0">Conceptual workload, not a benchmark.</p></div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("A regular VStack", ul("Eager: processes every child", "Large collection &rarr; large up-front work"))}</div>
        <div class="rule step" data-label="Our task">{ul("Investigate which container suits NPay", "Don&rsquo;t assume one is always fastest")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s workload explorer: the same transaction rows in three containers: a ScrollView with a VStack and ForEach, a ScrollView with a LazyVStack, and a List, with 100, 1,000 or 50,000 records.'),
                  ('SAY', 'Click: the shape of the problem as the text describes it: at a thousand records any container is fine; at ten thousand the eager container matters; at fifty thousand, data handling, sorting and filtering matter too. The text is explicit that this is a conceptual comparison, not a measured benchmark; memory, evaluation counts and frame times depend on the device and content.'),
                  ('SAY', 'Click: a regular VStack processes its children as part of eager layout. Click: our task is to investigate which container suits NPay, not to assume one is always fastest. Later today we measure all three.'),
                  ('CONNECT', 'First: what kind of work is &ldquo;slow&rdquo;?'))))

P = []
STG = [("db", "Application state", "large updates, computations"), ("code", "View evaluation", "dependent bodies re-run"),
       ("frame", "Layout", "measure and position"), ("layers", "Rendering", "draw and composite"), ("phone", "Display", "frames reach the screen")]
for i, (ic, t, sub) in enumerate(STG):
    x = i * 228
    P.append(tall(x, 0, 208, 120, ic, t, sub, f'{i + 1}' if i < 4 else '5+', ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 60H{x + 226}' + head(x + 226, 60, 'r')))
S.append(slide("Part 1 &middot; Performance is more than rendering (section 2) &middot; conceptual", "Five places work can pile up", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 120', 'Application state, view evaluation, layout, rendering, display', 'pipe', P, 'max-height:128px')}
    <p class="small muted" style="margin:6px 0 0">Simplified: SwiftUI may combine, skip or schedule this work differently.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Not equivalent", ul("A view&rsquo;s <b>body was evaluated</b>", "The view was <b>laid out</b>", "<b>Pixels were redrawn</b>"))}</div>
      <div class="rule step" data-label="So">{ul("A body can be evaluated without a full redraw", "Body counts alone don&rsquo;t prove a problem")}</div>
    </div>
  </div>""", notes(('SAY', 'When NPay feels slow, different kinds of work could be responsible. Click through the stages: application state, where large updates or expensive computations happen; view evaluation, where SwiftUI re-runs the bodies that depend on what changed; layout, where views measure and position their content; rendering, drawing and compositing; and display, frames reaching the screen.'),
                  ('SAY', 'This is a conceptual pipeline; SwiftUI may combine, skip or schedule work differently. Click: three statements that are not equivalent: a body was evaluated; the view was laid out; pixels were redrawn. Click: SwiftUI can evaluate a description without a complete visual redraw, which is why counting body evaluations alone does not establish a performance problem. Keep that in mind: we will count bodies today, but as clues, not verdicts.'),
                  ('CONNECT', 'The first experiment.'))))

# ================================================================== Part 2 (3, 4, 5)
divider(2, "Eager and lazy", "VStack builds everything; LazyVStack builds what&rsquo;s needed", 'One line changes the work.', 'An eager VStack.')
EAGER = """struct HistoryPerformanceLab: View {
    let transactions = Array(1...10_000)

    var body: some View {
        ScrollView {
            VStack(spacing: 8) {
                ForEach(transactions, id: \\.self) { id in
                    Text("Transaction #\\(id)")
                        .frame(
                            maxWidth: .infinity,
                            alignment: .leading
                        )
                        .padding()
                }
            }
        }
    }
}"""
S.append(slide("Part 2 &middot; First experiment: an eager VStack (section 3)", "10,000 rows, all of them built", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("HistoryPerformanceLab.swift", EAGER, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(f"Opened with VStack ({SIM})", ["row bodies evaluated on open:&ensp;<b>10,000</b>", "process memory footprint:&ensp;&ensp;&ensp;<b>~1 GB</b>"], 13)}
          <p class="small muted" style="margin:6px 0 0">Our counting copy of the section 19 row; indicative, not a device figure.</p></div>
        <div class="step">{card("Why", ul("<code>VStack</code> is an eager layout container", "Every child is created and measured up front"))}</div>
        <div class="rule step" data-label="Not ForEach">{ul("<code>ForEach</code> isn&rsquo;t the problem", "The surrounding container is")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s first laboratory: ten thousand integers, a ScrollView, an eager VStack, a ForEach of padded Texts. Predict before running: what happens when this view opens?'),
                  ('SAY', 'Click: we ran the same structure with the row from Section 19, counting how many row bodies SwiftUI evaluated. On open: all ten thousand, before the user has scrolled at all. The process footprint, measured inside the app, was about a gigabyte. That is a simulator Debug build, so treat the number as an indication, not a device figure; the count is what matters.'),
                  ('SAY', 'Click: VStack is an eager layout container: for a large collection it creates substantial layout and evaluation work. Click: ForEach itself is not necessarily the problem; the surrounding container matters.'),
                  ('CONNECT', 'Change one line.'))))

LAZY = """ScrollView {
    LazyVStack(spacing: 8) {      // was VStack(spacing: 8)
        ForEach(transactions, id: \\.self) { id in
            Text("Transaction #\\(id)")
                .frame(maxWidth: .infinity,
                       alignment: .leading)
                .padding()
        }
    }
}"""
S.append(slide("Part 2 &middot; Replace VStack with LazyVStack (section 4)", "One line: 10,000 rows becomes 15", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Section 4: one changed line", LAZY, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Same data", "Rows on open", "Footprint"], [("<code>VStack</code>", "10,000", "~1 GB"), ("<code>LazyVStack</code>", "<b>15</b>", "~39 MB")])}
          <p class="small muted" style="margin:6px 0 0">{SIM}.</p></div>
        <div class="step">{card("What changed", ul("Rows created and laid out when needed", "Built for scrolling collections"))}</div>
        <div class="warn step" data-label="Nuance">{ul("The array still holds all 10,000 records", "Lazy layout &ne; lazy data")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Change only one line: VStack becomes LazyVStack. Click: our run: fifteen row bodies on open, the rows that fill the screen plus a few, and a footprint of about thirty-nine megabytes against about a gigabyte.'),
                  ('SAY', 'Click: LazyVStack can defer child creation and layout until content is needed; it is designed for scrollable collections where not every row needs to take part in layout immediately.'),
                  ('SAY', 'Click: the important nuance: lazy loading does not mean the dataset is loaded lazily. Our array still holds ten thousand records in memory. LazyVStack concerns view layout and creation, not database pagination.'),
                  ('CONNECT', 'So there are several kinds of laziness.'))))

P = []
for i, (ic, t, q, l) in enumerate([("db", "Data loading", "How many records are fetched or stored?", '1'), ("code", "View creation", "When are row views constructed?", '2+'), ("layers", "Rendering", "Which visible content is drawn?", '3')]):
    x = i * 373
    P.append(tall(x, 0, 354, 130, ic, t, q, l, ''))
S.append(slide("Part 2 &middot; Three different kinds of laziness (section 5)", "LazyVStack is about one of them", f"""  <div class="body">
    {cues(3)}
    {svg('0 0 1100 130', 'Data loading, view creation, rendering', 'lazy3', P, 'max-height:136px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div class="step">{console(f"Records alone ({SIM})", ["footprint before:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;37 MB", "after 50,000 records:&ensp;&ensp;&ensp;&ensp;&ensp;46 MB", "after 500,000 records:&ensp;&ensp;&ensp;&ensp;94 MB"], 13)}</div>
      <div class="step">{card("Where the data kind is solved", ul("API pagination: Unit 5", "Persistent, fetched data: Unit 6"))}</div>
    </div>
  </div>""", notes(('SAY', 'This distinction is essential. Click: data loading: how many transactions are fetched or stored? Click: view creation: when does SwiftUI construct row content? This is LazyVStack&rsquo;s kind, in teal. Click: rendering: which visible content needs drawing or compositing?'),
                  ('SAY', 'Click: our measurement of the first kind, with no view at all: generating fifty thousand transaction records grew the footprint from thirty-seven to forty-six megabytes; five hundred thousand, to ninety-four. Displaying them in a LazyVStack does not take that memory away.'),
                  ('SAY', 'Click: data laziness is solved elsewhere: API pagination in Unit 5, persistent fetching in Unit 6.'),
                  ('CONNECT', 'NPay&rsquo;s History uses List. How does it compare?'))))

# ================================================================== Part 3 (6, 7)
divider(3, "List and scrolling", "Lazy containers while you scroll", 'List vs LazyVStack; what scrolling creates.', 'The comparison.')
LV = [("Built-in scrolling", "Usually inside a <code>ScrollView</code>"), ("Platform-adaptive row behaviour", "More custom layout control"),
      ("Swipe actions and selection", "Interactions built explicitly"), ("Manages collection presentation", "A lazy stack layout"),
      ("Standard histories", "Customized feeds")]
S.append(slide("Part 3 &middot; List versus LazyVStack (section 6)", "Both lazy; different jobs", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["List", "LazyVStack"], LV, 'tbl')}
        <div class="step">{tbl(["10,000 records", "Rows on open", "Footprint"], [("<code>List</code>", "<b>9</b>", "~39 MB"), ("<code>LazyVStack</code>", "15", "~39 MB")])}
          <p class="small muted" style="margin:6px 0 0">{SIM}.</p></div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("NPay&rsquo;s History: List", ul("Selection, swipe actions", "Accessibility behaviour (3.10)", "Large collections"))}</div>
        <div class="rule step" data-label="Still">{ul("Measure; don&rsquo;t assume it always wins")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The comparison from the text. List brings built-in scrolling, platform-adaptive rows, swipe actions and selection, and manages the collection&rsquo;s presentation: good for standard histories. LazyVStack usually sits in a ScrollView and gives more custom layout control; interactions are built explicitly: good for customized feeds.'),
                  ('SAY', 'Click: our run with ten thousand records: List evaluated nine row bodies on open, its rows are taller with the inset style; LazyVStack fifteen. Both about thirty-nine megabytes. Both lazy.'),
                  ('SAY', 'Click: for NPay&rsquo;s transaction history, List is a good default: selection, potentially swipe actions, the accessibility behaviour from 3.10, and large collections. Click: but we measure rather than assume it always outperforms every custom layout.'),
                  ('CONNECT', 'What happens while the user scrolls?'))))

P = []
LC = [("phone", "History opens", "gets the collection"), ("frame", "Visible region", "what fits on screen"), ("code", "Rows created", "only for that region"),
      ("tap", "User scrolls", "new rows come into view"), ("layers", "Rows leave", "may be released or reused"), ("db", "Data unchanged", "all records still held")]
for i, (ic, t, sub) in enumerate(LC):
    x = i * 188
    P.append(tall(x, 0, 172, 124, ic, t, sub, f'{i + 1}' if i < 5 else '6+', ''))
    if i < 5:
        P.append(wire(f'M{x + 173} 62H{x + 186}' + head(x + 186, 62, 'r')))
S.append(slide("Part 3 &middot; What happens while scrolling? (section 7) &middot; conceptual", "Only the visible region is built", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1120 124', 'History opens, visible region, rows created, user scrolls, rows leave, data unchanged', 'scroll', P, 'max-height:130px')}
    <p class="small muted" style="margin:6px 0 0">Exact caching, row lifetime and reuse are private implementation details.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div class="step">{tbl(["Scrolled to the last of 10,000", "Row bodies", "Footprint"], [("<code>VStack</code>", "10,000 (no new)", "~1 GB"), ("<code>LazyVStack</code>", "15 &rarr; <b>31</b>", "~41 MB"), ("<code>List</code>", "9 &rarr; <b>25</b>", "~45 MB")])}</div>
      <div class="step">{card("Observe", ul("Jumping to the end built a few dozen rows", "Not the 9,990 in between"))}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s lifecycle, conceptually. Click through: History opens and the container receives the collection; it works out the visible region; it creates rows for that region; the user scrolls and new rows come into view; rows that leave may be released or reused; and through all of it the data is unchanged. How rows are cached, kept or reused is a private implementation detail.'),
                  ('SAY', 'Click: we scrolled each container programmatically to the very end. VStack had already built all ten thousand. LazyVStack went from fifteen to thirty-one row bodies; List from nine to twenty-five. Click: the jump to the end built a few dozen rows, not the nine thousand nine hundred in between. That is lazy view creation, measured.'),
                  ('CONNECT', 'Lazy containers rely on identity.'))))

# ================================================================== Part 4 (8, 9, 10)
divider(4, "Identity and Observation", "Stable ids; narrow reads", 'Which rows are &ldquo;the same&rdquo;, and which views depend on what.', 'Identity.')
ID_GOOD = """struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}"""
ID_BAD = """struct Transaction: Identifiable {
    var id: UUID {
        UUID()
    }

    let title: String
}"""
S.append(slide("Part 4 &middot; View identity and performance (section 8)", "A new id every time: every row is new", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Stable (NPay&rsquo;s model)", ID_GOOD, "font-size:12.5px")}
        <div class="step">{code("Incorrect: computed id", ID_BAD, "font-size:12.5px")}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(f"20 rows in a List; one unrelated parent change ({SIM})", ["stable id:&ensp;&ensp;&ensp;<b>0</b> rows appeared again", "computed id: <b>every visible row</b> appeared again", "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;(13&ndash;26 onAppear calls per run)"], 12.5)}</div>
        <div class="step">{card("Costs", ul("Unnecessary work", "Lost row state", "Unexpected animations"))}</div>
        <div class="rule step" data-label="Principle">{ul("Identity = the logical transaction", "Not the current rendering attempt")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Recall Lesson 2.10. Our Transaction is Identifiable with a stored id, and each transaction needs a stable one. Click: the incorrect version: id is a computed property returning a fresh UUID on every access.'),
                  ('SAY', 'Click: our experiment: twenty rows in a List, and the parent changes something unrelated, a counter. With stable ids, no row appeared again. With the computed id, every visible row ran onAppear again, thirteen to twenty-six calls per run: SwiftUI saw thirteen brand-new logical rows, each time.'),
                  ('SAY', 'Click: that means unnecessary work, lost row state, since @State belongs to identity, as 2.10 showed, and unexpected animations. Click: identity must represent the logical transaction, not the current rendering attempt.'),
                  ('CONNECT', 'Which views update when the store changes?'))))

STORE = """@MainActor
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []
}"""
OBS = [("Append a transaction", "0", "1"), ("Change the balance", "1", "0"), ("Set the balance to its own value", "0", "0")]
S.append(slide("Part 4 &middot; Does every state change update every view? (section 9)", "Observation tracks what each body reads", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("NPayStore", STORE, "font-size:13.5px")}
        {card("Two readers", ul("<code>BalanceView</code> reads only <code>balancePaise</code>", "<code>HistoryView</code> reads only <code>transactions</code>"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Change", "Balance body", "History body"], OBS)}
          <p class="small muted" style="margin:6px 0 0">Body evaluations counted in the simulator.</p></div>
        <div class="warn step" data-label="But">{ul("Not a guarantee: parent updates, structure changes and other dependencies still evaluate views", "Investigate actual behaviour")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPay&rsquo;s store is @Observable. Suppose BalanceCard reads only the balance and HistoryScreen reads only the transactions. Modern Observation tracks the property accesses each body makes, which can reduce unnecessary invalidation compared with object-level notifications.'),
                  ('SAY', 'Click: we built exactly that: one store, two small views, and counted their bodies. Appending a transaction: the balance view did not run, the history view ran once. Changing the balance: the reverse. Assigning the balance its own value: neither ran in our run. Lesson 3.3 showed the same mechanism with tabs.'),
                  ('SAY', 'Click: but the text&rsquo;s caution: Observation does not guarantee that unrelated views are never evaluated. A parent that re-runs, a structural change, other dependencies: they can still cause evaluations. Investigate actual behaviour, which is what we just did.'),
                  ('CONNECT', 'A tool for asking SwiftUI why.'))))

DBG = """struct DebugTransactionRow: View {
    let title: String

    var body: some View {
        let _ = Self._printChanges()

        return Text(title)
            .padding()
    }
}"""
S.append(slide("Part 4 &middot; Inspect view evaluations (section 10)", "Self._printChanges(): a debugging aid", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DebugTransactionRow", DBG, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Console, first appearance", ["DebugTransactionRow: @self changed."], 13)}</div>
        <div class="step">{card("What it shows", ul("Why SwiftUI considers the view changed", "<code>@self</code>: the view value itself is new"))}</div>
        <div class="warn step" data-label="Caution">{ul("Not a public metric; not production logging", "Evaluated &ne; slow")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI provides Self._printChanges(), used inside a body. The text&rsquo;s DebugTransactionRow calls it with let underscore, then returns the padded Text: with a statement in body, the return is explicit.'),
                  ('SAY', 'Click: our console when the row first appeared: "DebugTransactionRow: @self changed." Click: it prints why SwiftUI considers the view changed: @self means the view&rsquo;s own value is new; a changed property would be named instead, as Lesson 2.8 showed with @State.'),
                  ('SAY', 'Click: the caution: the leading underscore marks it as a debugging aid, not a public performance metric or a production logging strategy, and a body being evaluated does not make a view slow.'),
                  ('CONNECT', 'What can make a body slow? The work inside it.'))))

# ================================================================== Part 5 (11, 12, 13, 22)
divider(5, "Work inside body", "Sorting and filtering on every update", 'A body runs whenever its dependencies change.', 'A sort in body.')
SORT = """var body: some View {
    let sorted = transactions.sorted {
        $0.date > $1.date
    }

    return List(sorted) { transaction in
        TransactionRow(transaction: transaction)
    }
}"""
S.append(slide("Part 5 &middot; Expensive computations inside body (section 11)", "A sort that runs with every evaluation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Sorting in body", SORT, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(f"50,000 records, search typed &ldquo;4999&rdquo; ({SIM})", ["keystrokes:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;4", "sorts in body:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;<b>4</b>"], 13)}</div>
        <div class="step">{card("Better direction", ul("Sort in a data layer, or cache the result", "Or have the repository return sorted data"))}</div>
        <div class="rule step" data-label="But">{ul("Small collection: probably fine", "Measure before optimizing")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Consider a body that sorts transactions by date and passes the sorted array to List. The sort executes whenever the body is evaluated.'),
                  ('SAY', 'Click: our lab put a sort like this in a body over fifty thousand records with a search field, and we typed four characters. Each keystroke changed state the body reads, so the body ran, and with it a sort of all fifty thousand records: four keystrokes, four full sorts. Nothing about the order had changed.'),
                  ('SAY', 'Click: the better direction: move expensive transformations to a data-processing layer, cache derived results when useful, or have the repository provide sorted data. Click: but avoid premature optimization: for a small collection this may be fine. Measure first.'),
                  ('CONNECT', 'How fast does sorting work grow?'))))

NS = [(100, 664), (1000, 9966), (5000, 61439), (10000, 132877), (50000, 780482)]
P = []
for i, (n, w) in enumerate(NS):
    y = i * 52
    bw = max(4, round(w / 780482 * 470))
    lbl = f'{n:,}'
    P.append(f'<text x="84" y="{y + 27}" text-anchor="end">{lbl}</text>')
    P.append(f'<g class="nd{" lit" if n == 50000 else ""}"><rect class="sh" x="96" y="{y + 8}" width="{bw}" height="28" rx="6"/></g>')
    P.append(f'<text class="sm" x="{96 + bw + 10}" y="{y + 27}">{w:,}</text>')
S.append(slide("Part 5 &middot; Understanding sorting complexity (section 12)", "n log&#8322; n grows faster than n", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.35fr) minmax(0,.65fr);gap:22px;align-items:start">
      <div>
        {svg('0 0 680 252', 'n log2 n for 100, 1,000, 5,000, 10,000 and 50,000 records', 'nlogn', P, 'max-height:300px')}
        <p class="small muted" style="margin:6px 0 0">Illustrative n&thinsp;log&#8322;&thinsp;n: relative work, not measured runtime.</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("A comparison sort", ul("Typically O(n log n)"))}
        <div class="step">{card("From 10,000 to 50,000", ul("5&times; the records", "About <b>5.9&times;</b> the comparisons"))}</div>
        <div class="rule step" data-label="Not a timing">{ul("Cost depends on types, comparator, hardware, memory, compiler")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A comparison sort typically has O of n log n complexity. The bars show n times log base two of n: a hundred records, about six hundred and sixty units of work; fifty thousand, about seven hundred and eighty thousand. These are relative numbers, not a timing.'),
                  ('SAY', 'Click: going from ten thousand to fifty thousand records multiplies the data by five but the comparisons by about five point nine: the log factor grows too.'),
                  ('SAY', 'Click: the text is explicit: this is not a benchmark. Actual cost depends on the data types, the comparator, hardware, memory behaviour and compiler optimizations. Combine it with the last slide: a cost that grows faster than the data, paid on every body evaluation.'),
                  ('CONNECT', 'Now NPay gets search.'))))

FILT = """@State private var searchText = ""

private var filteredTransactions: [Transaction] {
    guard !searchText.isEmpty else {
        return transactions
    }

    return transactions.filter {
        $0.title.localizedCaseInsensitiveContains(
            searchText
        )
    }
}

List(filteredTransactions) { transaction in
    TransactionRow(transaction: transaction)
}
.searchable(text: $searchText)"""
S.append(slide("Part 5 &middot; Introduce transaction filtering (section 13)", "Search in NPay History", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) 170px minmax(0,.8fr);gap:20px;align-items:start">
      {code("HistoryScreen", FILT, "font-size:11.5px")}
      <div class="step">{PHONE("img/history.png", "NPay History: &ldquo;Coffee&rdquo;", 170)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("50,000 records, 4 keystrokes", ["filters of all 50,000: <b>4</b>", "shown: Demo Transaction 4999,", "&ensp;14999, 24999, &hellip;"], 12)}</div>
        <div class="step">{card("Large data, later", ul("Debouncing", "Background processing", "Indexed or server-side search"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text adds a search field to History: searchText as @State, a computed filteredTransactions that returns everything when the text is empty and otherwise filters titles with localizedCaseInsensitiveContains, a List over the filtered collection, and .searchable bound to the text.'),
                  ('SAY', 'Click: integrated into NPay&rsquo;s real History screen, searching "Coffee". Click: in the fifty-thousand-record lab, typing four characters filtered all fifty thousand records four times: once per change of the search text. For a small local dataset that is reasonable.'),
                  ('SAY', 'Click: for large datasets we may introduce debouncing, background processing, indexed searching or server-side queries, studied later.'),
                  ('CONNECT', 'Filtering on every keystroke, examined.'))))

IMM = """.onChange(of: searchText) {
    updateResults()
}"""
S.append(slide("Part 5 &middot; Filtering on every keystroke (section 22)", "Immediate or debounced", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Strategy A: immediate", ul("Every accepted change can trigger filtering"))}
        {code("Strategy A", IMM, "font-size:15px")}
        <div class="step">{card("Strategy B: debounced", ul("Wait for a pause in typing", "Then do the expensive work once"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Records", "Filtering every keystroke"], [("100", "usually inexpensive"), ("50,000", "may become noticeable")])}</div>
        <div class="step">{card("Our run", ul("&ldquo;4999&rdquo;: 4 filters of 50,000", "A debounce would do one"))}</div>
        <div class="rule step" data-label="Principle">{ul("Reduce expensive operations", "Not just view descriptions")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Two strategies. Strategy A, immediate filtering: an onChange of searchText calls updateResults, so every accepted text change can trigger filtering. Click: Strategy B, debounced filtering: wait until the user has paused typing, then do the expensive work. We implement debouncing properly with Swift concurrency later.'),
                  ('SAY', 'Click: the text&rsquo;s scale: for a hundred transactions, filtering every keystroke is usually inexpensive; for fifty thousand it may become noticeable. Click: our four keystrokes cost four full filters; typed without pauses, a debounce would have done one.'),
                  ('SAY', 'Click: the principle: reduce unnecessary expensive operations, not merely the number of view descriptions.'),
                  ('CONNECT', 'How do we measure for real?'))))

# ================================================================== Part 6 (14, 15, 16, 18, 19)
divider(6, "Measuring", "Observe, measure, change one thing", 'Instruments, a fixed dataset, a fair comparison.', 'Instruments.')
MET = [("CPU usage", "expensive computations"), ("Main-thread work", "UI blocking"), ("Memory allocations", "unnecessary growth"),
       ("Animation hitches", "dropped or delayed frames"), ("View update activity", "repeated SwiftUI work")]
P = []
for i, (ic, t) in enumerate([("eye", "Observe"), ("clock", "Measure"), ("decision", "Identify bottleneck"), ("gear", "Change one thing"), ("clock", "Measure again")]):
    x = i * 228
    P.append(tall(x, 0, 208, 96, ic, t, '', f'{i + 1}+', ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 48H{x + 226}' + head(x + 226, 48, 'r')))
S.append(slide("Part 6 &middot; Instruments: measure real performance (section 14)", "Product &rarr; Profile", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:22px;align-items:start">
      {card("Instruments may include", ul("Time Profiler", "Allocations", "Leaks", "Animation Hitches", "SwiftUI-related tools"))}
      {tbl(["Metric", "Why it matters"], MET, 'tbl compact')}
    </div>
    <div class="gap"></div>
    {cues(5)}
    {svg('0 0 1120 96', 'Observe, measure, identify the bottleneck, change one thing, measure again', 'loop', P, 'max-height:100px')}
  </div>""", notes(('SAY', 'Xcode provides Instruments: Product, then Profile. Depending on the Xcode version, the templates include Time Profiler, Allocations, Leaks, Animation Hitches and SwiftUI-related profiling tools.'),
                  ('SAY', 'What to measure: CPU usage, to detect expensive computations; main-thread work, to find UI blocking; memory allocations, for unnecessary growth; animation hitches, for dropped or delayed frames; and view update activity, for repeated SwiftUI work.'),
                  ('SAY', 'Click through the senior engineer&rsquo;s loop: observe; measure; identify the bottleneck; change one thing; measure again. We did not run Instruments for this deck: the text recommends a Release build on a physical device for production performance. Our numbers come from counters inside the simulator app, which is the same loop on a smaller scale.'),
                  ('CONNECT', 'A dataset to measure with.'))))

GEN = """func makeDemoTransactions(
    count: Int
) -> [Transaction] {
    (0..<count).map { index in
        Transaction(
            id: UUID(),
            title: "Demo Transaction \\(index)",
            amountPaise: -(index + 1) * 100,
            date: Date().addingTimeInterval(
                -Double(index) * 60
            )
        )
    }
}"""
S.append(slide("Part 6 &middot; Generate 50,000 transactions (section 15)", "Make the dataset once, outside body", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("makeDemoTransactions", GEN, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Deterministic shape", ul("Titles &ldquo;Demo Transaction 0&rdquo; &hellip;", "Amounts &minus;₹1, &minus;₹2, &hellip;; one a minute apart"))}
        <div class="step">{card("Generate once", ul("Never inside <code>body</code>", "Keep it in a state owner"))}</div>
        <div class="warn step" data-label="Caveat">{ul("50,000 UUIDs and models cost time and memory (+9 MB here)", "Profile generation separately from scrolling")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A deterministic dataset for experiments: makeDemoTransactions maps a range of indices to transactions with a fresh UUID, the title Demo Transaction n, an amount of minus n plus one hundred paise, and a date one minute further in the past for each index.'),
                  ('SAY', 'Click: why generate once? Creating fifty thousand transactions inside body would repeat the work on every evaluation. Generate the dataset when setting up the experiment and keep it in an appropriate state owner, like the @State in our lab.'),
                  ('SAY', 'Click: the caveat: generating fifty thousand UUIDs and models itself takes time and memory; we measured nine megabytes. When profiling scrolling, separate generation cost from the cost of displaying and navigating the list.'),
                  ('CONNECT', 'The full lab.'))))

LABSW = """Group {
    switch selected {
    case .eager:
        ScrollView {
            VStack(spacing: 0) { rows }
        }
    case .lazy:
        ScrollView {
            LazyVStack(spacing: 0) { rows }
        }
    case .list:
        List(records, id: \\.self) { id in
            PerformanceRow(id: id)
        }
    }
}"""
CHK = ["Data once, outside body", "VStack, LazyVStack, List", "Repeat with 10,000", "Profile scrolling (Instruments)", "Compare CPU, allocations, hitches", "Record before optimizing"]
S.append(slide("Part 6 &middot; The runnable performance experiment (sections 16, 18&ndash;19)", "One dataset, one row, three containers", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px minmax(0,1fr) minmax(0,.8fr);gap:20px;align-items:start">
      {PHONE("img/perf.png", "HistoryPerformanceLab", 150)}
      {code("HistoryPerformanceLab (excerpt)", LABSW, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Lab checklist", ul(*CHK))}</div>
        <div class="rule step" data-label="Fair test">{ul("Same data, row, device, build", "Several runs; Release on a device")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s complete experiment, HistoryPerformanceLab.swift, standalone: a segmented Picker chooses VStack, LazyVStack or List; ten thousand integer records in @State; the eager and lazy cases wrap a ForEach of PerformanceRow in a ScrollView; the List case uses PerformanceRow directly. PerformanceRow is a credit-card symbol, "Transaction #n", a Spacer and ₹250. The screenshot is that code, running.'),
                  ('LIVE DEMO', 'Type HistoryPerformanceLab and PerformanceRow from Section 19 into a new file. Show it in NavigationStack. Switch the picker to VStack and wait for it; to LazyVStack; to List. Scroll each. Then run the app rather than the preview for anything you intend to measure.'),
                  ('SAY', 'Click: the text&rsquo;s lab checklist: generate the data once outside body; test the three containers; repeat with ten thousand; profile scrolling with Instruments; compare CPU, allocations and hitches; record observations before optimizing.'),
                  ('SAY', 'Click: the testing rule: same dataset, row, device and build configuration each time; run each scenario more than once; and for production questions, profile a Release build on a physical device. And, in the text&rsquo;s words: don&rsquo;t invent timing results.'),
                  ('CONNECT', 'Our results.'))))

RES = [("<code>ScrollView</code> + <code>VStack</code>", "10,000", "10,000", "~1 GB"),
       ("<code>ScrollView</code> + <code>LazyVStack</code>", "15", "31", "~39&ndash;41 MB"),
       ("<code>List</code>", "9", "25", "~39&ndash;45 MB")]
S.append(slide("Part 6 &middot; Compare three containers: our results (section 16)", "Counts first; memory second", f"""  <div class="body">
    {tbl(["10,000 records, PerformanceRow", "Row bodies on open", "After scrolling to the end", "Process footprint"], RES, 'tbl')}
    <p class="small muted" style="margin:6px 0 0">{SIM}; counting copy of the section 19 row; footprint read inside the app. Indicative, not a device benchmark.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Matches the text&rsquo;s expectation", ul("VStack: expensive with large collections", "LazyVStack and List: built for them"))}</div>
      <div class="step">{card("Not measured here", ul("Scrolling smoothness, CPU: Instruments on a device", "Your hierarchy may differ: measure it"))}</div>
    </div>
  </div>""", notes(('SAY', 'Our results, all three containers, the same ten thousand records and the same row. VStack evaluated every row body on open, and scrolling added nothing because there was nothing left to build; its footprint was about a gigabyte. LazyVStack: fifteen on open, thirty-one after jumping to the end, about forty megabytes. List: nine, then twenty-five, about forty to forty-five.'),
                  ('SAY', 'These are from a simulator Debug build; the memory numbers are indications. The counts would be the same shape anywhere.'),
                  ('SAY', 'Click: this matches what the text expects: VStack becomes expensive with large collections; LazyVStack and List are designed for them. Click: what we did not measure: scrolling smoothness and CPU, which need Instruments on a device. And the exact result depends on your view hierarchy and workload.'),
                  ('CONNECT', 'Lazy containers can&rsquo;t fix everything.'))))

# ================================================================== Part 7 (17, 20, 21)
divider(7, "The main actor and frames", "When the UI can&rsquo;t keep up", 'Big animations, blocking work, frame intervals.', 'Animation.')
ANIM = """withAnimation {
    transactions = newTransactions
}"""
S.append(slide("Part 7 &middot; Performance and animation (section 17)", "Animate meaningful, local changes", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Animating a whole collection replacement", ANIM, "font-size:16px")}
        {card("Remember 3.6", ul("We animated NPay&rsquo;s transaction updates"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Thousands of structural changes", ul("Expensive to animate", "Visually overwhelming"))}</div>
        <div class="rule step" data-label="Better">{ul("Animate meaningful, localized changes", "Not massive replacements, just because you can")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'In Lesson 3.6 we added animations to NPay&rsquo;s transaction updates. But wrapping a whole collection replacement in withAnimation, transactions equals newTransactions, can create unnecessary work.'),
                  ('SAY', 'Click: if the new collection contains a large number of structural changes, inserts, removals and moves, the animation may become expensive or visually overwhelming. Click: the principle: animate meaningful, localized changes, like the one new payment, and avoid animating massive collection replacements merely because animation is available. We did not measure this one; it is the text&rsquo;s guidance.'),
                  ('CONNECT', 'Why can the UI freeze even with a lazy list?'))))

LOAD = """Button("Load Transactions") {

    let records = makeDemoTransactions(
        count: 50_000
    )

    transactions = records
}"""
P = []
BS = [("tap", "User taps Load", ""), ("clock", "Main actor busy", "records generated"), ("cross", "UI work waits", "input, presentation"), ("check", "State updated", "list shows records")]
for i, (ic, t, sub) in enumerate(BS):
    y = i * 70
    P.append(box(0, y, 440, 58, t, sub, f'{i + 1}' if i < 3 else '4+', 'alert' if i == 2 else '', ic))
    if i < 3:
        P.append(wire(f'M220 {y + 59}V{y + 68}' + head(220, y + 68, 'd')))
S.append(slide("Part 7 &middot; Why can the UI freeze with LazyVStack? (section 20)", "The button action runs on the main actor", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,.75fr) minmax(0,.9fr);gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 20", LOAD, "font-size:13px")}
      </div>
      <div>{cues(4)}{svg('0 0 440 268', 'User taps Load, main actor busy, UI work waits, state updated', 'freeze', P, 'max-height:280px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(f"Display frames during the action ({SIM})", ["idle, per 0.5 s:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;~30", "50,000 records:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;<b>0</b> (action 0.02 s)", "500,000 records:&ensp;&ensp;&ensp;&ensp;&ensp;<b>0</b> (action ~0.2 s)", "longest frame gap:&ensp;&ensp;~0.25 s, not 0.017"], 11.5)}</div>
        <div class="rule step" data-label="Principle">{ul("A lazy container can&rsquo;t fix synchronous work", "Later: Swift concurrency moves it off the main actor")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 20: a Load Transactions button whose action generates fifty thousand records synchronously and assigns them to state. Click through the text&rsquo;s sequence: the user taps Load; the action runs on the main actor, generating the records; click: meanwhile UI work waits, input handling and presentation are delayed, in orange; click: generation finishes, state receives the collection, SwiftUI updates and the list shows the records.'),
                  ('SAY', 'Click: we counted display-link callbacks, which run on the main thread, while the action ran. Idle, about thirty per half second in the simulator. During the fifty-thousand-record action: zero. It took only about two hundredths of a second on this Mac, so the user would hardly notice; we repeated it with five hundred thousand: still zero frames, and the longest gap between frames was about a quarter of a second, against the normal seventeen milliseconds. Those durations are simulator measurements on a Mac; a phone, or heavier work, changes them. The zero does not change: while the main actor is busy, no frame work happens on it.'),
                  ('SAY', 'Click: even if the list is a LazyVStack, expensive synchronous work blocks interaction. A lazy view container cannot fix expensive synchronous application logic. Later we use Swift concurrency to move suitable CPU-bound work off the main actor while keeping UI updates correctly isolated.'),
                  ('CONNECT', 'How long is a frame?'))))

P = []
for i, (hz, ms) in enumerate([("60 Hz", 16.67), ("90 Hz", 11.11), ("120 Hz", 8.33)]):
    y = i * 54
    bw = round(ms / 20 * 860)
    P.append(f'<text x="96" y="{y + 26}" text-anchor="end">{hz}</text>')
    P.append(f'<g class="nd"><rect class="sh" x="110" y="{y + 8}" width="{bw}" height="28" rx="6"/></g>')
    P.append(f'<text class="sm" x="{110 + bw + 10}" y="{y + 26}">{ms:.2f} ms</text>')
S.append(slide("Part 7 &middot; Understanding frame budgets (section 21)", "Time between refresh opportunities", f"""  <div class="body">
    {svg('0 0 1100 160', 'Refresh intervals: 60 Hz 16.67 ms, 90 Hz 11.11 ms, 120 Hz 8.33 ms', 'fb', P, 'max-height:170px')}
    <p class="small muted" style="margin:6px 0 0">1000 / 60 = 16.67 ms &middot; 1000 / 120 = 8.33 ms: theoretical intervals at fixed refresh rates.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Missed deadlines", ul("Too much work in a critical update", "Frames miss presentation &rarr; visible hitches"))}</div>
      <div class="warn step" data-label="Nuance">{ul("Not a CPU budget for your code alone", "Layout, rendering, GPU, scheduling share it")}</div>
    </div>
  </div>""", notes(('SAY', 'A display refreshing at 60 hertz has about 16.67 milliseconds between refresh opportunities: a thousand divided by sixty. At 120 hertz, 8.33. The text&rsquo;s chart includes 90 hertz, 11.11. These are reference intervals, not guaranteed CPU budgets for your SwiftUI code.'),
                  ('SAY', 'Click: if the application does too much work during a critical update, frames miss their presentation deadlines and the user sees hitches: our quarter-second gap on the last slide is about fifteen 60-hertz intervals.'),
                  ('SAY', 'Click: the nuance: SwiftUI layout, rendering, GPU work and display scheduling involve multiple systems. You cannot assume the entire interval is available exclusively for your code.'),
                  ('CONNECT', 'Putting it together: diagnosis.'))))

# ================================================================== Part 8 (23, 25 + integration)
divider(8, "Diagnosis and NPay", "Choose the fix that matches the cause", 'Four symptoms, four causes.', 'The diagnosis table.')
DX = [("History is slow to open: 50,000 rows in a <code>VStack</code>", "Eager layout builds every row", "Use a lazy container (List, LazyVStack)"),
      ("Rows flicker, lose state, re-animate on every update", "Unstable ids (<code>UUID()</code> per access)", "Store a stable id in the model"),
      ("Typing in search feels heavy with 50,000 records", "Sort/filter re-run on every keystroke", "Move or cache the work; debounce (later)"),
      ("UI freezes after tapping Load", "Synchronous work on the main actor", "Move CPU-bound work off it (concurrency)")]
S.append(slide("Part 8 &middot; Choose the correct fix (section 23)", "Symptom, cause, fix", f"""  <div class="body">
    {tbl(["Symptom", "Cause", "Fix"], DX, 'tbl')}
    <p class="small muted" style="margin:6px 0 0">Scenario 1 is the text&rsquo;s; scenarios 2&ndash;4 are ours, drawn from this lesson&rsquo;s sections.</p>
    <div class="gap"></div>
    <div class="rule step" data-label="Wrong fixes">{ul("More animation, new UUIDs, a different container for a main-actor freeze: none touch the cause")}</div>
  </div>""", notes(('SAY', 'The text&rsquo;s diagnosis exercise. Scenario one: History takes a long time to open with fifty thousand rows in a VStack. The options were a lazy collection container, more animations, or new UUIDs; the fix is the lazy container, as we measured.'),
                  ('SAY', 'Only the first of the text&rsquo;s four scenarios was shared, so the other three rows are ours, each from today&rsquo;s sections: unstable ids, fixed by a stored id; heavy search typing, fixed by moving or caching the work and later debouncing; a freeze after Load, fixed by moving work off the main actor.'),
                  ('SAY', 'Click: and the wrong fixes: adding animation, generating new UUIDs, or swapping containers to cure a main-actor freeze: none of them touches the cause. Diagnose first.'),
                  ('CONNECT', 'What changed in NPay today.'))))

CH = [("HistoryScreen", "<code>@State searchText</code>, <code>filteredTransactions</code>, <code>.searchable</code> (section 13)"),
      ("HistoryScreen", "Stays a <code>List</code>: lazy, selection, accessibility"),
      ("Transaction", "Unchanged: stored, stable <code>id</code>"),
      ("Lab only", "HistoryPerformanceLab, makeDemoTransactions: not in the app")]
S.append(slide("Part 8 &middot; NPay after Lesson 3.11 (section 25, integration authored)", "Searchable History; measured choices", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) 170px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Where", "Change"], CH, 'tbl')}
        <div class="step">{card("Not yet", ul("Debounced search: with Swift concurrency", "Pagination and persistence: Units 5 and 6"))}</div>
        <div class="step">{card("Unit 3 progress (from the text)", ul("11 of 12 lessons; next: 3.12 integration &amp; architecture review"))}</div>
      </div>
      {PHONE("img/history.png", "History search", 170)}
    </div>
  </div>""", notes(('SAY', 'Our integration, flagged as ours: the real History screen gets the Section 13 search: searchText, filteredTransactions and searchable. It stays a List, which is lazy and keeps selection and the accessibility work from 3.10. Transaction already has a stored, stable id. The lab code stays out of the app.'),
                  ('SAY', 'Click: not yet: debounced search, which needs Swift concurrency, and pagination and persistence, Units 5 and 6. Click: the text&rsquo;s status: eleven of twelve Unit 3 lessons; Lesson 3.12 consolidates everything we built and reviews NPay&rsquo;s architecture before Unit 4.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.11', (), [("diff", "Lazy views, not lazy data", "VStack built 10,000 rows; LazyVStack 15; List 9"),
                      ("key", "Stable ids, narrow reads, light bodies", "no UUID() per access; no big sort per keystroke"),
                      ("clock", "Measure, and free the main actor", "0 frames while it was busy; observe &rarr; measure &rarr; change one thing")],
          'Three things to remember. Lazy containers create views for the visible region: an eager VStack built all ten thousand rows, LazyVStack fifteen and List nine; but the data itself is still all in memory, which pagination solves later. Keep identity stable and work out of body: a computed UUID made every row new, and a sort in body ran on every keystroke. And measure: counts, Instruments, one change at a time, remembering that a busy main actor delivers no frames however lazy the list is.')

review_divider(10)
review([("db", "Question", "Does LazyVStack automatically paginate backend data?",
         "Does <code>LazyVStack</code> automatically paginate backend data?", "No",
         "It defers view creation; our 10,000 records were all in memory.",
         "Confusing lazy layout with lazy data.", "Some say yes.", None),
        ("layers", "Question", "Does every body evaluation mean a full pixel redraw?",
         "Does every <code>body</code> evaluation mean a full pixel redraw?", "No",
         "Evaluation, layout and rendering are different stages.",
         "Treating body counts as redraw counts.", "Some say yes.", None),
        ("eye", "Choose one", "What is the main purpose of Instruments?",
         "What is the main purpose of Instruments?<br>A. Measure application behavior<br>B. Generate SwiftUI views<br>C. Replace the compiler", "A",
         "CPU, main thread, allocations, hitches, view updates.",
         "Optimizing without measuring.", "Most pick A.", None),
        ("key", "Question", "Can unstable IDs harm collection performance?",
         "Can unstable IDs harm collection performance?", "Yes",
         "A computed UUID made every visible row appear again on an unrelated change.",
         "Thinking any unique id is fine.", "Most say yes.", None),
        ("clock", "Question", "Can synchronous CPU work block UI responsiveness?",
         "Can synchronous CPU work block UI responsiveness?", "Yes",
         "Zero display frames while the action ran on the main actor.",
         "Expecting a lazy list to prevent freezes.", "Most say yes.", None),
        ("decision", "Question", "Should we optimize before measuring?",
         "Should we optimize before measuring?", "No",
         "Observe, measure, identify, change one thing, measure again.",
         "Rewriting code on a hunch.", "Most say no.", None),
        ("diff", "Predict the result", "10,000 rows in ScrollView + VStack: rows built on open?",
         "10,000 records in <code>ScrollView</code> + <code>VStack</code> + <code>ForEach</code>. How many row bodies are evaluated when it opens?<br>A. About a screenful<br>B. 10,000<br>C. None until scrolling", "B",
         "Eager: our run evaluated all 10,000; LazyVStack evaluated 15.",
         "Assuming ScrollView makes content lazy.", "Some pick A.", None),
        ("code", "Predict the result", "Search typed 4 characters, sort in body: how many sorts?",
         "<code>body</code> sorts 50,000 records and the user types 4 characters into a search field the body reads. How many sorts?<br>A. 1<br>B. 4<br>C. 0", "B",
         "One sort per body evaluation: 4 in our run.",
         "Thinking computed work is cached.", "Some pick A.", None),
        ("db", "Choose one", "Append a transaction: which bodies run?",
         "<code>BalanceView</code> reads only <code>balancePaise</code>; <code>HistoryView</code> reads only <code>transactions</code> of the same <code>@Observable</code> store. Append a transaction. Which bodies run?<br>A. Both<br>B. Only HistoryView<br>C. Only BalanceView", "B",
         "Observation tracked the reads: balance 0, history 1.",
         "Expecting object-wide invalidation.", "Some pick A.", None),
        ("key", "Question", "From 3.10: does VoiceOver speak accessibilityIdentifier?",
         "From Lesson 3.10: does VoiceOver speak an <code>accessibilityIdentifier</code>?", "No",
         "It's for UI automation; the localized label is spoken.",
         "Using identifiers as labels.", "Most say no.", "Spaced review from Lesson 3.10.")])

S.append(next_slide('3.11', [("3.12", "Unit 3 integration &amp; architecture review", "the complete NPay, including searchable History"),
                             ("Unit 4", "MVVM &amp; application architecture", "sorting and filtering move out of views"),
                             ("Units 5&ndash;6", "Networking; persistence", "pagination and fetched data: lazy data"),
                             ("Concurrency", "Swift concurrency", "debounced search; work off the main actor")],
                    'Lesson 3.12 consolidates all of Unit 3. Unit 4 gives sorting and filtering a proper home outside the views. Units 5 and 6 bring the data kind of laziness: pagination and fetched data. And Swift concurrency gives us debounced search and a way to move heavy work off the main actor.'))

S.append(lab_slide('3.11', "Measure, then change one thing", "Build the lab; count; profile.",
                   ["Build HistoryPerformanceLab (section 19).",
                    "Count row bodies on open for each container.",
                    "Scroll to the end; count again.",
                    "Give Transaction a computed id; watch onAppear.",
                    "Sort in body over 50,000; type in a search field.",
                    "Profile one change in Instruments, on a device."],
                   "", 'Expected, as in our run: VStack builds every row while the lazy containers build a screenful, plus a few dozen after scrolling; a computed id makes rows appear again on unrelated updates; a sort in body runs per keystroke. Instruments on a device adds the timings we chose not to claim.',
                   side=f'<div>{card("You hand in", ul("Your counts table for the three containers", "One before/after Instruments trace", "A one-line diagnosis: symptom, cause, fix"))}</div>'))

end_slide('3.11', 'SwiftUI Performance<br>&amp; Lazy Loading', 'Lesson 3.12 &mdash; Complete Unit 3 NPay Integration &amp; Architecture Review',
          'You can now separate the stages of SwiftUI&rsquo;s update work, choose between eager and lazy containers, tell lazy views from lazy data, keep identity stable and bodies light, recognise main-actor blocking, and measure before optimizing.',
          'Next, Lesson 3.12: the complete Unit 3 NPay integration and architecture review, before Unit 4, MVVM.')

write_deck(OUT311, '3.11', 'SwiftUI Performance &amp; Lazy Loading', 'SwiftUI Performance &amp; Lazy Loading')
