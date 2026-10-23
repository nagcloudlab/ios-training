"""Generates decks/unit-1/lesson-1.7/index.html from the Lesson 1.7 text (PocketBank -> NPay).
The text's 14 sections (Part A generics, Part B errors) are grouped into 8 Parts (see the lesson's "Deck changes")."""
import html, os, re, sys
OUT17 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'
tbl = lambda head_, rows, cls='tbl compact': f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head_) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'

title_slide('1.7', 'Generics &amp;<br>Error Handling',
            'One function for <b>many types</b>, without losing type safety. And what Swift does when an operation <b>fails</b>.',
            'In Lesson 1.6, protocols described common capabilities. Today two questions. How can one function work with different data types without giving up type safety? And how should Swift handle an operation that might fail? The answers are generics and error handling, both essential in production iOS code. We stay with NPay.')
outcomes_slide('1.7', [("layers", "Write <b>generic</b> functions and types"),
                       ("diff", "Why generics beat <code>Any</code>"),
                       ("link", "<b>Constraints</b> and <b>associated types</b>"),
                       ("cross", "Define errors and <b>throw</b> them"),
                       ("check", "<code>do</code>/<code>try</code>/<code>catch</code>, <code>try?</code>, <code>try!</code>, <code>Result</code>"),
                       ("globe", "A generic, throwing <b>API client</b>, and who handles 401")])
where_slide('1.7', 'Today: generics and errors', (),
            'Lesson 1.6: protocols are contracts; any and some; a protocol-typed service you can inject.',
            'Generic code that keeps types, and errors that say exactly what went wrong.',
            'Last lesson we saw some View hiding a long generic type and protocols describing capabilities. Today we look at the generics underneath, then at the other half of production code: what happens when an operation fails.',
            'Start with code we keep copying.')

# ================================================================== Part 1 (A1-2)
divider(1, "Generic functions", "Write it once, for any type", 'Same logic, different types. Why write it twice?', 'Look at the copies.')
DUP = """func firstTransaction(_ values: [Int]) -> Int? {
    values.first
}
func firstCustomer(_ values: [String]) -> String? {
    values.first
}"""
GEN = """func firstElement<T>(_ values: [T]) -> T? {
    values.first
}"""
SUB = [("<code>[10, 20, 30]</code>", "<code>Int</code>", "<code>Optional(10)</code>"),
       ("<code>[\"Ravi\", \"Meena\"]</code>", "<code>String</code>", "<code>Optional(\"Ravi\")</code>"),
       ("<code>[true, false]</code>", "<code>Bool</code>", "<code>Optional(true)</code>")]
S.append(slide("Part 1 &middot; The problem (section A1)", "Same logic, written once", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Copies.swift", DUP, "font-size:14px")}
        <p class="small muted" style="margin:8px 0 0">Identical logic; only the type changes.</p></div>
      <div class="step">{code("Generic.swift", GEN, "font-size:15px")}
        <div class="gap"></div>
        {tbl(["Called with", "T becomes", "Returns"], SUB)}</div>
    </div>
    <div class="gap"></div>
    <div class="takeaway step"><code>T</code> is a <b>type parameter</b>. The compiler picks the real type at each call, and keeps it.</div>
  </div>""", notes(('SAY', 'NPay needs the first element of an array: once for transaction ids, once for customer names. Two functions, identical logic, only the type differs.'),
                  ('SAY', 'Click: one generic function. The angle brackets declare T, a generic type parameter. Called with an array of Int, T becomes Int and it returns Optional(10). With strings, T becomes String. With Bools, Bool. Those are the real outputs.'),
                  ('SAY', 'Click: the compiler determines the concrete type at each call, and keeps it: the result of firstElement(["Ravi"]) is typed Optional of String, not something vaguer.'),
                  ('CONNECT', 'Why not just use Any?'))))

ANY = """func addOne(_ value: Any) -> Any {
    value + 1                  // error
}"""
ID = """func identity<T>(_ value: T) -> T {
    value
}

let amount: Int = identity(100)
let name: String = identity("Ravi")"""
S.append(slide("Part 1 &middot; Not Any (section A2)", "Any forgets the type; generics keep it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("AnyValue.swift", ANY, "font-size:15px")}
        <div style="margin-top:12px">{card("Any", ul("Holds <b>any</b> value, but the compiler forgets what it was", "Type-specific work needs casts (<code>as?</code>)") + '<p style="margin:8px 0 0">' + err("cannot convert value of type &lsquo;Any&rsquo; to expected argument type &lsquo;Int&rsquo;") + '</p>')}</div></div>
      <div class="step">{code("Identity.swift", ID, "font-size:15px")}
        <div style="margin-top:12px">{card("Generic", ul("Return type <b>matches</b> the input type", "No casts; checked at compile time"))}</div></div>
    </div>
    <div class="gap"></div>
    <div class="takeaway step"><code>Any</code> <b>erases</b> the type. Generics <b>preserve</b> the relationship between types.</div>
  </div>""", notes(('SAY', 'Any can hold any value. But then the compiler knows less about it: adding one to an Any is rejected, cannot convert value of type Any to expected argument type Int. You would need runtime casts with as?.'),
                  ('SAY', 'Click: the generic identity function returns exactly the type it received. identity(100) is an Int; identity("Ravi") is a String. No casts, all checked at compile time.'),
                  ('SAY', 'Click: Any provides type erasure; generics preserve type relationships.'),
                  ('CONNECT', 'Generics work for types too, not just functions.'))))

# ================================================================== Part 2 (A3-4)
divider(2, "Generic types and constraints", "Reusable types, and what T must be able to do", 'A response wrapper for any model, and a comparison that needs equality.', 'First the wrapper.')
RESP = """struct APIResponse<T> {
    let data: T
    let statusCode: Int
}

struct Customer { let name: String }
struct Account { let balanceMinor: Int64 }

let a = APIResponse(data: Customer(name: "Ravi"),
                    statusCode: 200)     // APIResponse<Customer>
let b = APIResponse(data: Account(balanceMinor: 2_500_000),
                    statusCode: 200)     // APIResponse<Account>"""
EQ = """func areEqual<T: Equatable>(_ a: T, _ b: T) -> Bool {
    a == b
}

print(areEqual(5, 5))             // true
print(areEqual("Ravi", "Meena"))  // false"""
S.append(slide("Part 2 &middot; Types and constraints (sections A3&ndash;A4)", "One wrapper; a constraint that unlocks ==", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("APIResponse.swift", RESP, "font-size:13px")}
        <div style="margin-top:12px">{card("Generic type", ul("One definition: <code>APIResponse&lt;T&gt;</code>", "Many concrete types: <code>&lt;Customer&gt;</code>, <code>&lt;Account&gt;</code>"))}</div></div>
      <div class="step">{code("AreEqual.swift", EQ, "font-size:14px")}
        <div style="margin-top:12px">{card("T: Equatable", ul("Not every type supports <code>==</code>", "The constraint promises it") + '<p style="margin:8px 0 0">Without it: ' + err("binary operator &lsquo;==&rsquo; cannot be applied to two &lsquo;T&rsquo; operands") + '</p>')}</div></div>
    </div>
  </div>""", notes(('SAY', 'Generic types: APIResponse of T wraps any model with a status code. One definition; the concrete types are APIResponse of Customer and APIResponse of Account. Account holds paise in Int64, as before.'),
                  ('SAY', 'Click: constraints. areEqual compares two values, but Swift cannot assume every type supports equality. Without a constraint the compiler says: binary operator == cannot be applied to two T operands. T: Equatable requires T to conform to the Equatable protocol, and that makes == available.'),
                  ('SAY', 'This is where protocols and generics meet: protocols describe capabilities; constraints say which capabilities a type must have.'),
                  ('CONNECT', 'Protocols can have type placeholders of their own.'))))

# ================================================================== Part 3 (A5)
divider(3, "Associated types", "A protocol with a type placeholder", 'One repository contract for customers, transactions, anything.', 'associatedtype.')
REPO = """protocol Repository {
    associatedtype Item
    func fetchAll() async throws -> [Item]
}

struct CustomerRepository: Repository {
    func fetchAll() async throws -> [Customer] {   // Item = Customer
        [Customer(name: "Ravi"), Customer(name: "Meena")]
    }
}"""
P = [box(160, 0, 300, 56, 'Repository', 'associatedtype Item', None, 'lit', 'link'),
     wire('M250 60L130 96' + head(130, 96, 'd'), None, 'dash'), wire('M370 60L490 96' + head(490, 96, 'd'), None, 'dash'),
     box(0, 102, 290, 56, 'CustomerRepository', 'Item = Customer', None, '', 'user'),
     box(330, 102, 290, 56, 'TransactionRepository', 'Item = Transaction', None, '', 'file')]
S.append(slide("Part 3 &middot; Associated types (section A5)", "Each conformer decides the type", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.15fr .85fr;gap:24px;align-items:start">
      {code("Repository.swift", REPO, "font-size:14px")}
      <div>{svg('0 0 620 158', 'Repository has an associated type Item; CustomerRepository sets it to Customer, TransactionRepository to Transaction', 'repo', P, 'max-height:200px')}
        <div class="gap"></div>
        {card("associatedtype", ul("A placeholder <b>inside</b> a protocol", "Inferred from the conformer: <code>Item = Customer</code>", "Used across the standard library and SwiftUI"), 'step')}</div>
    </div>
  </div>""", notes(('SAY', 'Different repositories return different records: customers, transactions. We want one contract. associatedtype Item declares a type placeholder that each conforming type fills in.'),
                  ('SAY', 'CustomerRepository returns an array of Customer, so Swift infers Item = Customer. A TransactionRepository would set Item = Transaction. The contract stays the same.'),
                  ('SAY', 'Click: associated types let protocols relate types without hard-coding one model. The standard library uses them everywhere, for example a collection&rsquo;s Element, and so does SwiftUI.'),
                  ('CONNECT', 'Now the second half: things that go wrong.'))))

# ================================================================== Part 4 (B6-7)
divider(4, "Errors and throwing", "Name the failure, throw it", 'A customer transfers ₹10,000. What can go wrong?', 'Plenty.')
ERR = """enum TransferError: Error {
    case invalidAmount
    case insufficientFunds
    case accountInactive
}"""
VAL = """func validateTransfer(amountMinor: Int64,
                      balanceMinor: Int64,
                      isActive: Bool) throws {
    guard isActive else { throw TransferError.accountInactive }
    guard amountMinor > 0 else { throw TransferError.invalidAmount }
    guard amountMinor <= balanceMinor else {
        throw TransferError.insufficientFunds
    }
}"""
S.append(slide("Part 4 &middot; Throwing (sections B6&ndash;B7)", "Errors are values; throw stops the function", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:.8fr 1.2fr;gap:24px;align-items:start">
      <div>{card("What can fail", ul("Invalid amount", "Insufficient funds", "Inactive account", "Network failure", "Backend rejects it"))}
        <div class="gap"></div>
        {code("TransferError.swift", ERR, "font-size:14px")}</div>
      <div class="step">{code("Validate.swift", VAL, "font-size:13px")}
        <div style="margin-top:12px">{card("throws", ul("Either <b>completes normally</b>, or <b>exits by throwing</b>", "Client-side checks only: the <b>server</b> authorizes transfers"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'A transfer of ₹10,000 can fail in several ways: an invalid amount, insufficient funds, an inactive account, a network failure, or the backend rejecting it. Swift represents failures with types that conform to the Error protocol. An enum is a natural fit: TransferError with three cases.'),
                  ('SAY', 'Click: a function that can fail is marked throws. validateTransfer checks the account is active, the amount is positive, and the balance covers it; each failed guard throws a specific error. A throwing function either completes normally or exits by throwing. Amounts are paise, as always.'),
                  ('SAY', 'These are client-side checks for a good user experience. Real transfers are authorized and processed by the server.'),
                  ('CONNECT', 'How does the caller deal with a throw?'))))

# ================================================================== Part 5 (B8-9)
divider(5, "Handling errors", "do, try, catch; try? and try!", 'The caller decides how to respond.', 'Four transfers, four outcomes.')
DO = """do {
    try validateTransfer(amountMinor: amount,
                         balanceMinor: 2_500_000,
                         isActive: active)
    print("Validation successful")
} catch TransferError.invalidAmount {
    print("Invalid transfer amount")
} catch TransferError.insufficientFunds {
    print("Insufficient funds")
} catch {
    print("Unexpected error: \\(error)")
}"""
CASES = [("&#8377;10,000", "Validation successful"), ("&#8377;0", "Invalid transfer amount"),
         ("&#8377;30,000", "Insufficient funds"), ("inactive", "Unexpected error: accountInactive")]
KW = [("<code>throws</code> / <code>throw</code>", "can throw / throws one"), ("<code>try</code>", "marks a call that may throw"),
      ("<code>do</code> / <code>catch</code>", "scope / handles matching errors")]
S.append(slide("Part 5 &middot; do / try / catch (section B8)", "Catch what you can handle", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Handle.swift", DO, "font-size:13px")}
        <div class="gap"></div>
        {tbl(["Keyword", "Meaning"], KW)}</div>
      <div class="step"><p class="small muted" style="margin:0 0 6px">Balance &#8377;25,000. Real output:</p>
        {tbl(["Transfer", "Prints"], [(a, f'<code>{b}</code>') for a, b in CASES])}
        <div class="gap"></div>
        <div class="tip" data-label="Notice">{ul("No <code>catch</code> for <code>accountInactive</code>: the general <code>catch</code> takes it")}</div></div>
    </div>
  </div>""", notes(('SAY', 'do opens a scope for throwing calls; try marks the call that may throw; each catch handles matching errors, most specific first, and a final catch with no pattern handles the rest, with the error available as error.'),
                  ('SAY', 'Click: we ran four transfers against a ₹25,000 balance. ₹10,000 from an active account: Validation successful. ₹0: Invalid transfer amount. ₹30,000: Insufficient funds. ₹10,000 from an inactive account: Unexpected error, accountInactive, because there is no specific catch for it, so the general catch takes it.'),
                  ('SAY', 'And try is not optional decoration: call a throwing function without it and the compiler says call can throw but is not marked with try. The failure path is always visible in the code.'),
                  ('CONNECT', 'Two shortcuts, one useful and one dangerous.'))))

TRYS = [("<code>try</code>", "handle it, or propagate it to the caller", "the error reaches someone who decides"),
        ("<code>try?</code>", "turn failure into <code>nil</code>", "the reason is <b>discarded</b> (Lesson 1.3)"),
        ("<code>try!</code>", "assert it cannot fail", "if it does: <b>the app traps</b>")]
S.append(slide("Part 5 &middot; try? and try! (section B9)", "Three ways to call a throwing function", f"""  <div class="body">
    {tbl(["Form", "Means", "On failure"], TRYS, 'tbl')}
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px;align-items:start">
      {card("try! that fails, run for real", mono("Fatal error: &lsquo;try!&rsquo; expression unexpectedly<br>raised an error: TransferError.invalidAmount", 14))}
      <div class="warn" data-label="Rule">{ul("<code>try!</code> only when failure is <b>impossible</b> by a justified invariant", "Never to skip error handling")}</div>
    </div>
  </div>""", notes(('SAY', 'Three forms. Plain try: the error must be handled in a do/catch or propagated from a throwing function. try?: failure becomes nil and the error details are discarded, as we saw with decoding in Lesson 1.3. try!: you assert the call cannot fail.'),
                  ('SAY', 'Click: if a try! call does fail, the app traps. Real message: Fatal error, try! expression unexpectedly raised an error, invalidAmount. In an app, that is a crash.'),
                  ('SAY', 'Use try! only when failure is genuinely impossible under a justified invariant, never to avoid writing error-handling code.'),
                  ('CONNECT', 'Errors can also travel upward, or be stored as values.'))))

# ================================================================== Part 6 (B10-11)
divider(6, "Propagation and Result", "Who handles it, and errors as values", 'Not every function should handle its own errors.', 'Let them travel up.')
PROP = """func performTransfer() throws {
    try validateTransfer(amountMinor: 1_000_000,
                         balanceMinor: 2_500_000, isActive: true)
    print("Transfer validation completed")
}"""
RES = """func validate(amountMinor: Int64)
    -> Result<String, TransferError> {
    guard amountMinor > 0 else {
        return .failure(.invalidAmount)
    }
    return .success("Valid transfer")
}
// 0 → failure(invalidAmount)
// 5 → success("Valid transfer")"""
P = [box(0, 0, 250, 52, 'View', 'shows a message', None, '', 'phone'), wire('M254 26H286' + head(286, 26, 'r')),
     box(292, 0, 250, 52, 'ViewModel', 'decides what to show', None, 'lit', 'layout'), wire('M546 26H578' + head(578, 26, 'r')),
     box(584, 0, 250, 52, 'Service', 'throws an error', None, '', 'link'),
     wire('M709 56V74H417V60' + head(417, 60, 'u'), None, 'dash'), '<text class="sm" x="563" y="90" text-anchor="middle">error travels up</text>']
S.append(slide("Part 6 &middot; Propagation and Result (sections B10&ndash;B11)", "Let errors travel; or return them as values", f"""  <div class="body">
    {svg('0 0 834 92', 'The view calls the ViewModel, which calls the service; the service throws and the error travels up to the ViewModel', 'prop', P, 'max-height:100px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Propagate.swift", PROP, "font-size:13px")}
        <div style="margin-top:12px">{card("throws, without catch", ul("<code>performTransfer</code> passes the error <b>up</b>", "Each layer handles what it understands"))}</div></div>
      <div class="step">{code("Result.swift", RES, "font-size:13px")}
        <div style="margin-top:12px">{card("Result&lt;Success, Failure&gt;", ul("<code>.success(value)</code> or <code>.failure(error)</code>", "A <b>value</b>: store it, return it, pass it on"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'performTransfer is marked throws but does not catch: if validation throws, the error simply continues to performTransfer&rsquo;s caller. That is propagation.'),
                  ('SAY', 'The picture shows why it matters in NPay: the view calls the ViewModel, the ViewModel calls the service, the service throws. The networking service knows an HTTP request failed; the ViewModel decides what message the user sees. A good architecture decides which layer handles which errors.'),
                  ('SAY', 'Click: Result is the other style. validate returns Result of String and TransferError: either success with a value or failure with an error, as an ordinary value you can store and pass around. Real output: failure(invalidAmount) for 0, success for 5. throws expresses failure through control flow; Result through a value. Both are useful, depending on the API.'),
                  ('CONNECT', 'Now add async.'))))

# ================================================================== Part 7 (B12-13)
divider(7, "Async, throwing and generic", "Put it all together", 'Networking can both wait and fail.', 'async throws.')
ASYNC = """func fetchBalance() async throws -> Int64 {
    try await Task.sleep(for: .seconds(1))   // illustrative wait
    return 2_500_000
}

do {
    let balanceMinor = try await fetchBalance()
    print(balanceMinor)
} catch {
    print("Failed: \\(error)")
}"""
S.append(slide("Part 7 &middot; async throws (section B12)", "try for failure, await for waiting", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:start">
      {code("FetchBalance.swift", ASYNC, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("async", ul("Can <b>suspend</b> while it waits", "<code>await</code> marks the suspension point"))}
        {card("throws", ul("Can <b>fail</b>", "<code>try</code> acknowledges it"))}
        <div class="step">{card("try await", ul("Two different concerns, one call", "Order is always <code>try await</code>"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'fetchBalance is both async, it can suspend while it waits, and throws, it can fail. The sleep stands in for a network call.'),
                  ('SAY', 'Calling it needs both keywords: try acknowledges possible failure, await marks a potential suspension point. Different concerns, one call: try await. Prints 2500000.'),
                  ('SAY', 'Click: as Lesson 0.5 showed, await does not block the thread while it waits; Lesson 1.9 explains how.'),
                  ('CONNECT', 'Now generics and errors together: NPay&rsquo;s API client.'))))

CLIENT = """struct APIClient {
    func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T {
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(T.self, from: data)
    }
}"""
USE = """struct Balance: Decodable { let balanceMinor: Int64 }
struct Customer: Decodable { let name: String }

let balance = try await client.fetch(Balance.self, from: balanceURL)
let customer = try await client.fetch(Customer.self, from: profileURL)"""
S.append(slide("Part 7 &middot; Generic API client (section B13)", "One fetch for every model", f"""  <div class="body">
    {code("APIClient.swift", CLIENT, "font-size:13px")}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:start">
      <div class="step">{code("Callers.swift", USE, "font-size:13px")}</div>
      <div class="step">{card("Why it works", ul("<code>T: Decodable</code>: any model that can be decoded", "Throws on a bad status <b>or</b> bad JSON", "The pattern of real Swift networking layers"))}</div>
    </div>
  </div>""", notes(('SAY', 'One method, generic over T, constrained to Decodable. It awaits URLSession, checks for a 2xx status, throwing badServerResponse otherwise, then decodes the data as T, which can also throw. Everything from today in nine lines: a generic function, a constraint, async, and throws. The status check uses 200..<300, as in Lesson 0.8.'),
                  ('SAY', 'Click: the same method decodes a Balance, in paise, and a Customer. Each caller gets back exactly the type it asked for.'),
                  ('SAY', 'Click: T: Decodable guarantees the type can be decoded; the function throws on a bad status or bad JSON. This is the core of real Swift networking layers; Lesson 5.4 builds the full version.'),
                  ('CONNECT', 'One last question: when that client gets a 401, who reacts?'))))

# ================================================================== Part 8 (B14)
divider(8, "Errors across layers", "Who handles a 401?", 'The API answers 401 Unauthorized. Should the networking code open the login screen?', 'Usually not.')
LAYER = """enum APIError: Error {
    case unauthorized              // 401
    case server(status: Int)
    case decoding
}"""
P = [box(0, 0, 250, 64, 'APIClient', 'throws APIError.unauthorized', '1', '', 'globe'), wire('M254 32H294' + head(294, 32, 'r'), '2'),
     box(300, 0, 260, 64, 'Session coordinator', 'decides: sign in again?', '2', '', 'key'), wire('M564 32H604' + head(604, 32, 'r'), '3+'),
     box(610, 0, 250, 64, 'UI', 'presents the login screen', '3+', '', 'phone')]
S.append(slide("Part 8 &middot; Design (section B14)", "Report, decide, present", f"""  <div class="body">
    {svg('0 0 860 64', 'The API client reports unauthorized; a session coordinator decides to reauthenticate; the UI presents the login screen', 'layers', P, 'max-height:80px')}
    {cues(3)}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("APIError.swift", LAYER, "font-size:15px")}
      <div class="step">{card("Why separate", ul("The client <b>reports</b>; it doesn&rsquo;t navigate", "Each layer is testable on its own", "Token refresh and sessions: 5.5, Unit 07"))}</div>
    </div>
  </div>""", notes(('SAY', 'The API returns 401 Unauthorized. Should the generic networking service jump straight to the login screen? Usually not.'),
                  ('SAY', 'Click: the networking layer reports a meaningful error, APIError.unauthorized, instead of a raw status code. Click: a higher-level session or app coordinator decides whether to reauthenticate, perhaps refreshing a token first. Click: only then does the UI present the login screen.'),
                  ('SAY', 'Click: the client reports, it does not navigate. That keeps each layer simple and testable on its own. Lesson 5.5 covers token refresh; Unit 07 covers sessions; Lesson 4.8 maps errors across layers.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.7', (), [("layers", "Generics keep the type", "&lt;T&gt;, constraints, associated types"),
                     ("cross", "Errors are typed values", "throw, try, catch; try? drops the reason"),
                     ("globe", "Layers own their errors", "report low, decide high, show at the top")],
         'Three things to remember. Generics write logic once and keep the concrete type, unlike Any; constraints like T: Equatable say what T must be able to do, and associated types give protocols their own placeholders. Errors are typed values: throw them, mark calls with try, catch what you can handle; try? throws away the reason and try! crashes on failure. And layers own their errors: the client reports, a coordinator decides, the UI shows.')

review_divider(8)
review([("layers", "Choose one", "What does T become in firstElement([\"Ravi\"])?",
         "In <code>firstElement([\"Ravi\", \"Meena\"])</code>, what does <code>T</code> become?<br>A. <code>Any</code><br>B. <code>String</code><br>C. <code>[String]</code><br>D. <code>Optional&lt;String&gt;</code>", "B",
         "<code>T</code> is the element type, <code>String</code>. The return type is <code>T?</code>, so the result is <code>Optional&lt;String&gt;</code>.",
         "Confusing T with the array or the return type.", "Some pick C or D.", None),
        ("link", "Choose one", "Why does areEqual need T: Equatable?",
         "Why does <code>func areEqual&lt;T: Equatable&gt;</code> need the constraint?<br>A. To make it faster<br>B. Because not every type supports <code>==</code><br>C. Because generics only work with structs<br>D. It doesn&rsquo;t; it&rsquo;s optional style", "B",
         "Without it: &ldquo;binary operator &lsquo;==&rsquo; cannot be applied to two &lsquo;T&rsquo; operands&rdquo;.",
         "Thinking constraints are optional decoration.", "Some pick D.", None),
        ("code", "Predict the output", "What does the do/catch print for a transfer of ₹0?",
         "<code>validateTransfer</code> with amount <code>0</code> inside the do/catch from Part 5. What prints?", "Invalid transfer amount",
         "The amount guard throws <code>.invalidAmount</code>, and its specific <code>catch</code> handles it.",
         "Expecting the general catch.", "Most get it.", None),
        ("cross", "Question", "Does a failing try! crash the app?",
         "If a call marked <code>try!</code> throws, does the app crash?", "Yes",
         "It traps: &ldquo;Fatal error: &lsquo;try!&rsquo; expression unexpectedly raised an error&rdquo;.",
         "Thinking try! returns nil like try?.", "Some say it returns nil.", None),
        ("diff", "Choose one", "How is Result different from throws?",
         "How is <code>Result</code> different from <code>throws</code>?<br>A. Result is only for networking<br>B. Result is a value you can store and pass around<br>C. Result cannot carry an error<br>D. There is no difference", "B",
         "<code>throws</code> uses control flow; <code>Result</code> holds <code>.success</code> or <code>.failure</code> as an ordinary value.",
         "Treating Result as a networking-only type.", "Some pick D.", None),
        ("globe", "Question", "Should the generic networking layer navigate to login on a 401?",
         "The API returns 401. Should the generic networking layer open the login screen itself?", "No",
         "It reports <code>.unauthorized</code>; a session coordinator decides; the UI presents.",
         "Putting navigation inside networking code.", "Some say yes, for speed.", None),
        ("check", "Predict the output", "What is r for try? on a failing call?",
         "<code>let r = try? validateTransfer(amountMinor: 0,</code><br><code>&nbsp;&nbsp;balanceMinor: 1, isActive: true)</code><br>What is <code>r</code>?", "nil",
         "<code>try?</code> turns the thrown error into <code>nil</code>; the reason is lost.",
         "Expecting the error value.", "Some expect invalidAmount.", None),
        ("decision", "Question", "Can a some Repository function return different repository types?",
         "<code>func makeRepository() -&gt; some Repository</code> returns <code>CustomerRepository()</code>. Can it return <code>TransactionRepository()</code> on another path?", "No",
         "<code>some</code> means one exact type; mixed return types do not compile.",
         "Treating some like any.", "Some say yes.", "Spaced review from Lesson 1.6.")])

S.append(next_slide('1.7', [("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "what <code>async</code> and <code>await</code> really do"),
                            ("1.10", "NPay domain model, actor ledger &amp; tests", "typed errors in the domain"),
                            ("4.8", "Error mapping across layers", "service, ViewModel and UI errors"),
                            ("5.4", "Generic async API client", "the full <code>APIClient</code>"),
                            ("5.5", "Auth headers &amp; token refresh", "what happens after a 401")],
                    'Generics and errors return throughout the course. 1.9 explains async and await properly; 1.10 uses typed errors in NPay&rsquo;s domain model; 4.8 maps errors across layers; 5.4 builds the full generic API client; and 5.5 handles the 401 with token refresh.'))

LAB = """enum TransferError: Error {
    case invalidAmount, insufficientFunds, accountInactive
}
// 1. validateTransfer(amountMinor:balanceMinor:isActive:) throws
// 2. do/catch for ₹10,000 · ₹0 · ₹30,000 · inactive
// 3. the same check returning Result<String, TransferError>
// 4. func decode<T: Decodable>(_ type: T.Type, from json: String) throws -> T"""
S.append(lab_slide('1.7', "Validate and decode", "Errors and generics on NPay data, Swift only.",
                   ["Write <code>validateTransfer</code> with three guards.",
                    "Run four transfers through one do/catch; add a catch for <code>accountInactive</code>.",
                    "Write the <code>Result</code> version; print both outcomes.",
                    "Write a generic <code>decode</code>; decode <code>Balance</code>, then break the JSON key."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab. Expected with balance 2,500,000: 1,000,000 active → Validation successful; 0 → Invalid transfer amount; 3,000,000 → Insufficient funds; inactive → Unexpected error: accountInactive until they add a specific catch. Result version prints failure(...invalidAmount) and success("Valid transfer"). decode&lt;T: Decodable&gt;(_ type: T.Type, from json: String) throws -&gt; T { try JSONDecoder().decode(T.self, from: Data(json.utf8)) } (import Foundation): {"balanceMinor": 2500000} decodes; {"amount": 1} throws a DecodingError (keyNotFound).',
                   side=f'<div>{code("lab.swift", LAB, "font-size:13px")}<div class="gap"></div>{card("You hand in", ul("Four transfer outputs", "Result output", "The decoding error you got"))}</div>'))

end_slide('1.7', 'Generics &amp; Error Handling', 'Lesson 1.8 &mdash; ARC, Ownership &amp; Memory Management',
          'You can now write generic functions and types, explain why generics beat Any, use constraints and associated types, define and throw errors, handle them with do, try and catch, choose between try, try? and try!, use Result, combine async and throws, and decide which layer handles an error.',
          'Next, Lesson 1.8: ARC, ownership and memory management, going deeper than Lesson 0.6 into references, capture lists and ownership.')

write_deck(OUT17, '1.7', 'Generics &amp; Error Handling', 'Generics &amp; Error Handling')
