"""Generates decks/unit-1/lesson-1.3/index.html from the Lesson 1.3 text (PocketBank -> NPay)."""
import html, os, re, sys
OUT13 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers

title_slide('1.3', 'Swift Optionals:<br>nil, ?, ! and Safe Unwrapping',
            '&ldquo;An optional is just another way to handle null.&rdquo; <b>Partly.</b> Swift makes a missing value part of the <b>type</b>.',
            'Today: one of Swift&rsquo;s most important language features, optionals. With your background you might think an optional is just another way to handle null. That is partly correct, but Swift goes further: the possibility of a missing value becomes part of the type system, and the compiler holds you to it. Our NPay story continues.')
outcomes_slide('1.3', [("decision", "What <code>String?</code> means, and why it is a <b>type</b>"),
                       ("check", "Unwrap safely with <code>if let</code> and <code>guard let</code>"),
                       ("diff", "Fall back with <code>??</code>, and when <b>not</b> to"),
                       ("link", "Follow optional chains with <code>?.</code>"),
                       ("cross", "Why <code>!</code> traps, and when it is acceptable"),
                       ("globe", "Optionals in <b>API models</b> and <code>try?</code>")])
where_slide('1.3', 'Today: modelling absence', ('lang',),
            'Lesson 1.2: types are fixed at build time, and a dictionary lookup handed us an optional.',
            'What that optional is, and every safe way to get the value out.',
            'Last lesson ended with <code>balances["Asha"]</code> returning nil, typed as an optional Int. Today we open that box: what an optional is, why the compiler will not let you use one directly, and the tools Swift gives you to unwrap it safely.',
            'Start with a real NPay record.')

# ================================================================== 1
divider(1, "What if the data doesn&rsquo;t exist?", "Required versus optional", 'NPay stores customer details. Some fields are always there; one is often missing.', 'Here is the record.')
FIELDS = [("Customer name", "Ravi", ""), ("Account number", "NP1001", ""), ("Email", "ravi@example.com", ""), ("Middle name", "<i>not provided</i>", ' class="hl"')]
trs = ''.join(f'<tr{c}><td>{a}</td><td>{b}</td></tr>' for a, b, c in FIELDS)
REQ = """let customerName: String = "Ravi"

let middleName: String = nil     // error
let middleName2: String? = nil   // valid"""
S.append(slide("Part 1 &middot; The problem", "A field that may be missing", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:32px;align-items:start">
      <div><table class="tbl"><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{trs}</tbody></table>
        <div class="gap"></div>
        {card("Other languages", ul("Java <code>null</code> &middot; Python <code>None</code>", "JavaScript <code>null</code> or <code>undefined</code>", "Swift <code>nil</code>, <b>only where the type allows it</b>"))}</div>
      <div>{code("MiddleName.swift", REQ, "font-size:17px")}
        <p class="step" style="margin:12px 0 0">{err("&lsquo;nil&rsquo; cannot initialize specified type &lsquo;String&rsquo;")}</p>
        <div class="gap"></div>
        <div class="cols step" style="gap:16px">{card("String", ul("A value is <b>required</b>"))}{card("String?", ul("A value <b>may be absent</b>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Ravi&rsquo;s record: name, account number NP1001, email, and no middle name. How should Swift represent the missing middle name? Java would use null, Python None, JavaScript null or undefined. Swift uses nil, but only where the type allows absence.'),
                  ('SAY', 'Click: a plain String cannot hold nil. The real error: nil cannot initialize specified type String. Add a question mark and it is valid.'),
                  ('SAY', 'Click: String means a value is required. String? means a value may exist, or may be absent. One character changes the contract.'),
                  ('CONNECT', 'So what is a String? really?'))))

# ================================================================== 2
divider(2, "An Optional is a box", "Two cases, one type", 'Picture a sealed box: it either holds a value, or it is empty.', 'Open it.')
ENUM = """enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

// String?  is shorthand for  Optional<String>"""
P = ['<text class="mono" x="276" y="16" text-anchor="middle">String?  =  Optional&lt;String&gt;</text>',
     wire('M0 30V24H552V30', None, 'faint'),
     tall(0, 40, 266, 140, 'check', '.some("Ravi")', 'the box holds a String', '0'),
     tall(286, 40, 266, 140, 'cross', '.none', 'the box is empty: nil', '1+')]
S.append(slide("Part 2 &middot; The box", "Optional is an enum with two cases", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:32px;align-items:center">
      {svg('0 0 552 180', 'String optional: case some holding Ravi, or case none', 'box', P, 'max-height:230px')}
      {code("Optional.swift", ENUM, "font-size:17px")}
    </div>
    {cues(1)}
    <div class="gap"></div>
    <div class="rule step" data-label="Not a null pointer">{ul("A <b>type</b> for presence or absence of a wrapped value", "Works for <b>any</b> type: <code>Int?</code>, <code>Balance?</code>, <code>[String]?</code>")}</div>
  </div>""", notes(('SAY', 'Conceptually an optional has two cases: none, or some with a wrapped value. This is a simplified version of the standard library&rsquo;s Optional enum. String? is just shorthand for Optional of String.'),
                  ('SAY', 'Right now the box holds some("Ravi"). Click: set it to nil and the box is empty, the none case.'),
                  ('SAY', 'Click: an optional is not a special pointer that might be null. It is an ordinary enum type that represents presence or absence, and it works for any wrapped type, including structs like Balance and collections.'),
                  ('CONNECT', 'If it is a box, you cannot use the contents without opening it.'))))

# ================================================================== 3
divider(3, "Why not use it directly?", "The compiler insists on a check", 'We have a middle name. Why can&rsquo;t we just ask for its length?', 'Try it.')
COUNT = """let middleName: String? = "Kumar"

print(middleName.count)   // error"""
P = [box(0, 0, 300, 60, 'middleName', 'String?', None, 'lit', 'decision'),
     wire('M300 30H350' + head(350, 30, 'r')),
     box(356, 0, 280, 60, 'Does a value exist?', 'unwrapping', None, '', 'eye'),
     wire('M636 30H680V-14H720' + head(720, -14, 'r')), wire('M680 30V74H720' + head(720, 74, 'r')),
     box(726, -44, 410, 60, '.some: use the String', '', None, '', 'check'),
     box(726, 44, 410, 60, '.none: handle the missing value', '', None, '', 'cross')]
S.append(slide("Part 3 &middot; Unwrapping", "A String? is not a String", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:.9fr 1.1fr;gap:28px;align-items:start">
      {code("Count.swift", COUNT, "font-size:17px")}
      <p style="margin:0">{err("value of optional type &lsquo;String?&rsquo; must be unwrapped to refer to member &lsquo;count&rsquo; of wrapped base type &lsquo;String&rsquo;")}</p>
    </div>
    <div class="gap-lg"></div>
    <div class="step">{svg('-2 -46 1140 154', 'An optional is checked: some means use the String, none means handle the missing value', 'unwrap', P, 'max-height:170px')}</div>
  </div>""", notes(('SAY', 'middleName holds "Kumar", but its type is String?, not String. So .count is rejected, with a precise message: the optional must be unwrapped to reach count on the wrapped String.'),
                  ('SAY', 'Click: the compiler requires you to handle both possibilities. Check whether a value exists: if some, use the String; if none, handle the missing value. That check is called unwrapping, and the next four parts are four ways to do it.'),
                  ('CONNECT', 'The safest common way first.'))))

# ================================================================== 4
divider(4, "Optional binding: if let", "The safest common way", 'Bind the value to a new name only if it exists.', 'Here is the code.')
IFLET = """let middleName: String? = "Kumar"

if let name = middleName {
    print("Middle name: \\(name)")
} else {
    print("No middle name")
}"""
P = [box(0, 0, 260, 56, '"Kumar"', 'case 1: .some', '0-1', '', 'check'), box(300, 0, 260, 56, 'nil', 'case 2: .none', '2+', '', 'cross'),
     wire('M130 60L240 106' + head(240, 106, 'd'), '0-1'), wire('M430 60L320 106' + head(320, 106, 'd'), '2+'),
     box(130, 112, 300, 56, 'if let name = middleName', '', None, '', 'decision'),
     wire('M230 172L140 216' + head(140, 216, 'd'), '1'), wire('M330 172L420 216' + head(420, 216, 'd'), '2+'),
     box(0, 222, 260, 64, 'if branch', 'Middle name: Kumar', '1', '', 'check'),
     box(300, 222, 260, 64, 'else branch', 'No middle name', '2+', '', 'cross')]
S.append(slide("Part 4 &middot; if let", "Bind it if it is there", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("IfLet.swift", IFLET, "font-size:16px")}
      {svg('0 0 560 286', 'if let: Kumar takes the if branch, nil takes the else branch', 'iflet', P, 'max-height:320px')}
    </div>
    {cues(2)}
    <div class="gap"></div>
    <div class="tip step" data-label="Swift 5.7 shorthand">{ul("<code>if let middleName { &hellip; }</code> unwraps under the <b>same name</b>", "Same for <code>guard let</code>")}</div>
  </div>""", notes(('SAY', 'Optional binding with if let. The middle name is "Kumar".'),
                  ('SAY', 'Click: the optional contains some("Kumar"), so Swift binds the unwrapped value to name, and inside the if branch name is a plain String: Middle name: Kumar. Click: if it is nil, the none case, nothing is bound and the else branch runs.'),
                  ('SAY', 'This is why you cannot accidentally use a missing value as if it existed: the unwrapped name only exists where the value does.'),
                  ('SAY', 'Click: since Swift 5.7 you can write if let middleName, without repeating the name, and the same for guard let. You will see both styles in real code.'),
                  ('CONNECT', 'Sometimes a missing value means: stop here.'))))

# ================================================================== 5
divider(5, "guard let: early exit", "Stop when data is missing", 'NPay sends a notification. Without an email there is nothing to do.', 'Exit early.')
GUARD = """func sendNotification(email: String?) {
    guard let email = email else {
        print("Email unavailable")
        return
    }
    print("Sending notification to \\(email)")
}"""
S.append(slide("Part 5 &middot; guard let", "Exit early, keep the happy path flat", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Notify.swift", GUARD, "font-size:16px")}
        <div class="warn step" data-label="else must exit" style="margin-top:14px">{ul("<code>return</code>, <code>throw</code>, <code>break</code> or <code>continue</code>", "Otherwise: &lsquo;guard&rsquo; body must not <b>fall through</b>")}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("if let", ul("Run code <b>only if</b> the value exists", "Binding lives <b>inside</b> the branch"))}
        {card("guard let", ul("Missing data means <b>exit early</b>", "Binding lives <b>after</b> the guard"))}
      </div>
    </div>
  </div>""", notes(('SAY', 'guard let unwraps or leaves. If the email is missing we print Email unavailable and return; otherwise the function continues, and email is now a plain String for the rest of the function. The successful path stays flat instead of nested inside an if.'),
                  ('SAY', 'Compare the two: if let when some logic should run only if a value exists, with the binding scoped to that branch; guard let when missing data should cause an early exit, with the binding available after the guard.'),
                  ('SAY', 'Click: the else branch must leave the scope: return, throw, break or continue. If it falls through, a full build fails with: guard body must not fall through. That check happens in SIL, the stage from Lesson 1.1, so a type-check-only run does not show it.'),
                  ('CONNECT', 'What if you just want a sensible default?'))))

# ================================================================== 6
divider(6, "Nil coalescing: ??", "A fallback value", 'NPay shows a nickname, or &ldquo;Customer&rdquo; if there is none.', 'Two question marks.')
COAL = """let nickname: String? = nil

let displayName = nickname ?? "Customer"
print(displayName)"""
CT = [('<code>"Ravi"</code>', 'Ravi'), ('<code>nil</code>', 'Customer')]
trs = ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td></tr>' for a, b in CT)
BAD = """let balanceMinor: Int64? = nil      // not loaded
let shown = balanceMinor ?? 0        // shows ₹0"""
S.append(slide("Part 6 &middot; ??", "Use the value, or a fallback", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("DisplayName.swift", COAL, "font-size:17px")}
        <table class="tbl" style="margin-top:14px"><thead><tr><th><code>nickname</code></th><th><code>nickname ?? "Customer"</code></th></tr></thead><tbody>{trs}</tbody></table></div>
      <div class="step">{code("Balance.swift", BAD, "font-size:16px")}
        <div class="warn" data-label="Hidden absence" style="margin-top:14px">{ul("A missing balance is <b>not</b> &#8377;0", "Show &ldquo;Balance unavailable&rdquo; instead")}</div></div>
    </div>
    <div class="gap"></div>
    <div class="tip" data-label="Good for">{ul("Default labels, optional settings, fallback text")}</div>
  </div>""", notes(('SAY', 'Two question marks: use the wrapped value if present, otherwise the fallback. With a nickname of "Ravi" we show Ravi; with nil we show Customer.'),
                  ('SAY', 'That is great for default labels, optional configuration values and fallback text.'),
                  ('SAY', 'Click: but be careful. A silent default can hide missing data when absence should be treated as an error. If NPay has not loaded the balance, balance ?? 0 shows ₹0, which is simply wrong and alarming. Show that the balance is unavailable instead; Unit 04 builds proper loading and error states.'),
                  ('CONNECT', 'Optionals can also sit inside other types.'))))

# ================================================================== 7
divider(7, "Optional chaining: ?.", "Absence flows through", 'A customer may have no address. How do we ask for the city?', 'Chain it.')
CHAIN = """struct Address { let city: String }
struct Customer {
    let name: String
    let address: Address?
}

let customer = Customer(name: "Ravi",
                        address: nil)
let city = customer.address?.city   // String?"""
P = [box(0, 0, 560, 56, 'customer', 'Customer', None, '', 'user'), wire('M280 60V86' + head(280, 86, 'd')),
     box(0, 92, 560, 56, '.address?', 'Address?: may be nil', None, '', 'decision'),
     wire('M200 152L135 194' + head(135, 194, 'd'), '1'), wire('M360 152L425 194' + head(425, 194, 'd'), '2+'),
     box(0, 200, 270, 70, 'address is nil', 'chain stops: city = nil', '1', '', 'cross'),
     box(290, 200, 270, 70, 'address in Pune', 'city = Optional("Pune")', '2+', '', 'check')]
S.append(slide("Part 7 &middot; Chaining", "The result is always optional", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("Chain.swift", CHAIN, "font-size:16px")}
      {svg('0 0 560 270', 'customer.address?.city: if address is nil the chain stops and returns nil; otherwise it returns the city', 'chain', P, 'max-height:300px')}
    </div>
    {cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="Type of city">{ul("<code>String?</code>, because any link may be missing", "A nil link <b>propagates</b> absence; nothing throws or crashes")}</div>
  </div>""", notes(('SAY', 'Customer has an optional Address, and Address has a city. Ravi has no address. customer.address?.city asks: if there is an address, give me its city.'),
                  ('SAY', 'Click: address is nil, so the chain stops and city is nil. Click: with an address in Pune, Swift reaches the city: Optional("Pune").'),
                  ('SAY', 'Click: so the type of city is String?, not String, because any link may be missing. Optional chaining does not throw an error when an intermediate value is nil; it propagates absence through the chain.'),
                  ('CONNECT', 'Now the dangerous one.'))))

# ================================================================== 8
divider(8, "Force unwrapping: !", "A promise the compiler cannot check", 'The exclamation mark says: trust me, there is a value.', 'What if there is not?')
FORCE = """let nickname: String? = nil

print(nickname!)"""
S.append(slide("Part 8 &middot; Force unwrap", "! traps when the box is empty", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Force.swift", FORCE, "font-size:18px")}
        <div class="card accent step" style="margin-top:14px;padding:16px 22px"><span class="label">Running it</span><p style="font-family:var(--mono);margin:4px 0 0;font-size:15px;line-height:1.5">Fatal error: Unexpectedly found nil while unwrapping an Optional value</p></div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Acceptable only when", ul("A <b>reliable invariant</b> guarantees a value", "Test fixtures, tightly controlled setup"))}</div>
        <div class="rule step" data-label="Default">{ul("Prefer <code>if let</code>, <code>guard let</code>, <code>??</code>", "Never reach for <code>!</code> as the easy way")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The exclamation mark tells Swift: assume this optional contains a value and extract it. With "Ravi" inside, print(nickname!) prints Ravi.'),
                  ('SAY', 'Click: with nil inside, the program stops. This is the real message from running it: Fatal error, unexpectedly found nil while unwrapping an Optional value. In an app, that is a crash in the customer&rsquo;s hand.'),
                  ('SAY', 'Click: when is it acceptable? Only when you can establish a reliable invariant that the value cannot be missing at that point: certain test fixtures, or tightly controlled initialization paths.'),
                  ('SAY', 'Click: in ordinary application logic, prefer safe unwrapping. The exclamation mark is never the easy default.'),
                  ('CONNECT', 'You will also meet a cousin of !, mostly in UIKit.'))))

# ================================================================== 9
divider(9, "Implicitly unwrapped optionals", "String! in older code", 'A type ending in an exclamation mark. Where does it come from?', 'Interface Builder.')
IUO = """import UIKit

final class BalanceViewController: UIViewController {
    @IBOutlet weak var titleLabel: UILabel!
}"""
S.append(slide("Part 9 &middot; IUO", "Optional underneath, unwrapped on use", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("BalanceViewController.swift", IUO, "font-size:16px")}
        <div class="tip step" data-label="In new code" style="margin-top:14px">{ul("Prefer ordinary optionals and <b>explicit initialization</b>")}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("What it is", ul("An optional that is <b>unwrapped automatically</b> when used", "Absent at first, expected <b>later</b>"))}
        {card("Why outlets use it", ul("Connected while the interface <b>loads</b>"), 'step')}
        <div class="warn step" data-label="Risk">{ul("Used <b>before</b> it is connected: trap")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'You will meet this in UIKit code: an IBOutlet declared as UILabel with an exclamation mark. That is an implicitly unwrapped optional. Underneath it is an ordinary optional, but Swift unwraps it automatically wherever you use it as a non-optional.'),
                  ('SAY', 'Click: Interface Builder outlets historically use this because they are absent when the object is created and connected while the interface loads.'),
                  ('SAY', 'Click: the risk is the same as force unwrapping: touch the outlet before it is connected and the app traps.'),
                  ('SAY', 'Click: in modern Swift code, prefer ordinary optionals and explicit initialization when practical. Unit 10 covers UIKit in depth.'),
                  ('CONNECT', 'Optionals matter most where data comes from outside: the network.'))))

# ================================================================== 10
divider(10, "Optionals in API responses", "Allowed to be absent is not the same as broken", 'NPay&rsquo;s backend returns a customer. Which fields may be missing?', 'Model only what the API allows.')
JSON = """{
  "customerId": "C1001",
  "name": "Ravi",
  "email": null
}"""
MODEL = """struct CustomerResponse: Decodable {
    let customerId: String     // required
    let name: String           // required
    let email: String?         // may be null or absent
}"""
CASES = [('<code>"email": null</code>', '<code>email == nil</code>', 'decodes'),
         ('no <code>"email"</code> key', '<code>email == nil</code>', 'decodes'),
         ('no <code>"customerId"</code> key', '<code>DecodingError.keyNotFound</code>', '<b>fails</b>')]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in CASES)
S.append(slide("Part 10 &middot; API models", "Optional means allowed to be absent", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:.7fr 1.3fr;gap:28px;align-items:start">
      {code("response.json", JSON, "font-size:16px")}
      {code("CustomerResponse.swift", MODEL, "font-size:16px")}
    </div>
    <div class="gap"></div>
    <div class="step"><table class="tbl"><thead><tr><th>Response</th><th>Result</th><th>Decoding</th></tr></thead><tbody>{trs}</tbody></table></div>
    <div class="gap"></div>
    <div class="takeaway step">An optional does <b>not</b> mean &ldquo;ignore data errors&rdquo;. It means <b>this</b> value may be absent.</div>
  </div>""", notes(('SAY', 'The backend returns a customer with an id, a name, and an email that may be null. The model makes email optional, because the API allows it to be null or absent. customerId and name are required.'),
                  ('SAY', 'Click: we decoded three responses. Email null: decodes, email is nil. Email key missing: also decodes, email is nil. customerId missing: decoding fails with DecodingError.keyNotFound, because the model says the id is required. Same if it had the wrong type.'),
                  ('SAY', 'Click: an optional does not mean ignore all data errors. It means a particular value is allowed to be absent. Lesson 5.3 goes deeper into Codable and custom decoding.'),
                  ('CONNECT', 'There is a shortcut that turns any error into nil.'))))

# ================================================================== 11
divider(11, "try?: errors into optionals", "Convenient, and lossy", 'A throwing call can be turned into an optional result.', 'Compare it with do/catch.')
TRYQ = """let customer = try? JSONDecoder().decode(
    CustomerResponse.self, from: data)

// success → CustomerResponse?   failure → nil"""
DOCATCH = """do {
    let customer = try JSONDecoder().decode(
        CustomerResponse.self, from: data)
    print(customer.name)
} catch {
    print(error)   // keyNotFound "customerId"
}"""
S.append(slide("Part 11 &middot; try?", "try? keeps the result, drops the reason", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("TryOptional.swift", TRYQ, "font-size:16px")}
        <div class="gap"></div>
        {card("try?", ul("Success: the value", "Failure: <code>nil</code>, <b>no reason</b>", "Fine when any failure means &ldquo;skip it&rdquo;"))}</div>
      <div class="step">{code("DoCatch.swift", DOCATCH, "font-size:16px")}
        <div class="gap"></div>
        {card("do / catch", ul("Keeps the <b>error</b>: malformed data vs other failures", "What NPay&rsquo;s networking needs"))}</div>
    </div>
  </div>""", notes(('SAY', 'try? converts a throwing operation into an optional. If decoding succeeds, customer holds the value; if it throws, the expression is simply nil.'),
                  ('SAY', 'That is convenient, but it discards the error details. You know it failed, not why.'),
                  ('SAY', 'Click: with do/catch you keep the error. For the response without a customerId we get keyNotFound for customerId, so NPay can tell malformed data from a network failure and react differently. In production networking that distinction usually matters. Lesson 1.7 covers error handling properly.'),
                  ('CONNECT', 'Five mistakes to avoid.'))))

# ================================================================== 12
divider(12, "Common optional mistakes", "And the better approach", 'Most optional bugs come from five habits.', 'Here they are.')
MIS = [("Force unwrap every optional", "Use <code>if let</code> or <code>guard let</code>"),
       ("Replace a missing balance with zero", "Represent unavailable data <b>explicitly</b>"),
       ("Make every property <code>String?</code>", "Model the <b>actual</b> domain requirements"),
       ("Ignore decoding failures with <code>try?</code>", "Handle errors when <b>details matter</b>"),
       ("Assume <code>?.</code> returns a non-optional", "The chain&rsquo;s result is <b>optional</b>")]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in MIS)
S.append(slide("Part 12 &middot; Mistakes", "Five habits to break", f"""  <div class="body">
    <table class="tbl"><thead><tr><th>Mistake</th><th>Better approach</th></tr></thead><tbody>{trs}</tbody></table>
  </div>""", notes(('SAY', 'Five common mistakes. Force unwrapping every optional: use if let or guard let. Replacing a missing balance with zero: represent unavailable data explicitly. Making every property optional: model what the domain actually requires, as we did with customerId. Ignoring decoding failures with try?: handle the error when the details matter. And assuming optional chaining returns a non-optional: its result is always optional.'),
                  ('CONNECT', 'Now combine everything in one NPay example.'))))

# ================================================================== 13
divider(13, "NPay practical example", "Required and optional, side by side", 'One model, one function, three unwrapping tools.', 'Here it is.')
EX = """struct Customer {
    let id: String
    let name: String
    let email: String?
    let nickname: String?
}

func displayCustomer(_ customer: Customer) {
    let displayName = customer.nickname ?? customer.name
    print("Welcome, \\(displayName)")
    if let email = customer.email { print("Email: \\(email)") }
    else { print("Email not provided") }
}"""
S.append(slide("Part 13 &middot; Example", "A model that says what is required", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.25fr .75fr;gap:28px;align-items:start">
      {code("Customer.swift", EX, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Called with", '<p style="font-family:var(--mono);margin:4px 0 0;font-size:14px;line-height:1.5">Customer(id: "C1001",<br>&nbsp;name: "Ravi Kumar",<br>&nbsp;email: nil,<br>&nbsp;nickname: "Ravi")</p>')}
        <div class="step">{card("Prints", '<p style="font-family:var(--mono);margin:4px 0 0;font-size:15px;line-height:1.6">Welcome, Ravi<br>Email not provided</p>')}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'id and name are required; email and nickname are optional. displayCustomer uses the nickname if there is one, otherwise the name, with nil coalescing; then if let for the email.'),
                  ('ASK', 'Before the click: what does it print for Ravi Kumar with nickname Ravi and no email?'),
                  ('SAY', 'Click: Welcome, Ravi, then Email not provided. The model states clearly which data is required and which is optional, and that is the foundation of reliable Swift application design.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.3', ('lang',), [("decision", "Absence is in the type", "String? is Optional&lt;String&gt;"),
                            ("check", "Unwrap safely", "if let, guard let, ??, ?."),
                            ("cross", "! is a promise", "break it and the app traps")],
         'Three things to remember. Absence is part of the type: String? is Optional of String, an enum with some and none, and the compiler will not let you use it as a plain String. Unwrap safely with if let, guard let, nil coalescing and optional chaining, and do not let a default hide data that should be there. And the exclamation mark is a promise: break it and the app traps.')

review_divider(8)
review([("decision", "Choose one", "What does String? represent?",
         "What does <code>String?</code> represent?<br>A. A String that may be empty<br>B. A String value, or no value<br>C. A pointer to a String<br>D. A String loaded lazily", "B",
         "<code>String?</code> is <code>Optional&lt;String&gt;</code>: either <code>.some(String)</code> or <code>.none</code>. An empty string is still a value.",
         "Confusing nil with the empty string &ldquo;&rdquo;.", "Some pick A.", None),
        ("cross", "Choose one", "What happens when force unwrapping nil?",
         "What happens at run time when you force unwrap <code>nil</code>?<br>A. It returns an empty value<br>B. It returns nil<br>C. The program traps with a fatal error<br>D. Nothing; the compiler prevents it", "C",
         "&ldquo;Fatal error: Unexpectedly found nil while unwrapping an Optional value.&rdquo; The compiler cannot check it for you.",
         "Thinking the compiler catches it.", "Some pick D.", None),
        ("diff", "Predict the output", "What does nickname ?? Customer print when nickname is Ravi?",
         "What does this print?<br><code>let nickname: String? = \"Ravi\"</code><br><code>print(nickname ?? \"Customer\")</code>", "Ravi",
         "<code>??</code> uses the wrapped value when it exists; the fallback is only for <code>nil</code>.",
         "Expecting Optional(\"Ravi\").", "A few say Optional(\"Ravi\").", None),
        ("link", "Choose one", "What does optional chaining return when an intermediate value is nil?",
         "<code>customer.address?.city</code> when <code>address</code> is <code>nil</code>:<br>A. An empty String<br>B. <code>nil</code>, typed <code>String?</code><br>C. A runtime trap<br>D. A thrown error", "B",
         "The chain stops at the first nil and the whole expression is <code>nil</code>. Its type is always optional.",
         "Expecting a crash, like force unwrapping.", "Some pick C.", None),
        ("globe", "Question", "Should every property in an API model be optional?",
         "Should every property in an API model be optional, just to be safe?", "No",
         "Make optional only what the API allows to be absent. A required field that is missing should <b>fail</b> decoding, not become nil.",
         "Hiding broken data behind optionals.", "Some say yes, for safety.", None),
        ("check", "Question", "Can a guard else branch simply continue execution?",
         "Can the <code>else</code> branch of a <code>guard</code> simply continue to the next line?", "No",
         "It must leave the scope with <code>return</code>, <code>throw</code>, <code>break</code> or <code>continue</code>. Otherwise the build fails.",
         "Treating guard like an if without a body.", "Many are unsure.", None),
        ("code", "Predict the output", "What does try? return when customerId is missing?",
         "The JSON has no <code>customerId</code>. What is <code>customer</code>?<br><code>let customer = try? JSONDecoder()</code><br><code>&nbsp;&nbsp;.decode(CustomerResponse.self, from: data)</code>", "nil",
         "Decoding throws <code>keyNotFound</code>, and <code>try?</code> turns that into <code>nil</code>. The reason is lost.",
         "Expecting a customer with a nil id.", "Some expect a partial customer.", None),
        ("layers", "Predict the type", "What type is balances[\"Asha\"]?",
         "<code>let balances = [\"Ravi\": 25000]</code><br>What is the type of <code>balances[\"Asha\"]</code>?", "Int?",
         "A dictionary lookup returns an optional, <code>Optional&lt;Int&gt;</code>, because the key may not exist. Here it is <code>nil</code>.",
         "Expecting Int, or a crash.", "Some say Int.", "Spaced review from Lesson 1.2.")])

S.append(next_slide('1.3', [("1.6", "Protocols, extensions &amp; protocol-oriented design", "optional protocol requirements, <code>Optional</code> extensions"),
                            ("1.7", "Generics &amp; error handling", "<code>throws</code>, <code>do/catch</code> beyond <code>try?</code>"),
                            ("4.6", "Loading/error/success UI state", "&ldquo;balance unavailable&rdquo;, not &#8377;0"),
                            ("5.3", "Codable, dates &amp; custom decoding", "optional and required API fields"),
                            ("10.1", "UIKit lifecycle &amp; responder chain", "outlets and <code>UILabel!</code>")],
                    'Optionals run through the whole course. Lesson 1.7 handles errors properly instead of try?. Unit 04 builds loading, error and success states so a missing balance never shows as zero. Lesson 5.3 decodes real API responses with optional and required fields. And Unit 10 returns to UIKit outlets.'))

LAB = """struct CustomerResponse: Decodable {
    let customerId: String
    let name: String
    let email: String?
    let nickname: String?
}
// decode [CustomerResponse] from the JSON in the notes
// for each: print nickname ?? name, and the email or "no email\""""
S.append(lab_slide('1.3', "Decode NPay customers", "Decode a small customer list, then break it on purpose.",
                   ["Decode the two-customer JSON; print each display name and email.",
                    "Use <code>??</code> for the name, <code>if let</code> or <code>guard let</code> for the email.",
                    "Remove <code>customerId</code> from one customer.",
                    "Decode with <code>try?</code>, then with <code>do/catch</code>; compare what you learn.",
                    "Replace any <code>!</code> you used with safe unwrapping."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab. JSON: [{"customerId": "C1001", "name": "Ravi Kumar", "email": null, "nickname": "Ravi"}, {"customerId": "C1002", "name": "Meena", "email": "meena@example.com"}]. Decode with try JSONDecoder().decode([CustomerResponse].self, from: Data(json.utf8)) (import Foundation). Expected: "Ravi no email" and "Meena meena@example.com" (the second customer has no nickname key, which is fine because nickname is optional). With customerId removed: try? gives nil and no reason; do/catch with catch DecodingError.keyNotFound(let key, _) prints the missing key, customerId. Note that one bad element fails the whole array.',
                   side=f'<div>{code("lab.swift", LAB, "font-size:15px")}<div class="gap"></div>{card("You hand in", ul("Your output for both customers", "What <code>try?</code> told you vs <code>do/catch</code>"))}</div>'))

end_slide('1.3', 'Swift Optionals:<br>nil, ?, ! and Safe Unwrapping', 'Lesson 1.4 &mdash; Functions, Parameters &amp; Closures',
          'You can now explain what String? represents, unwrap with if let and guard let, fall back with nil coalescing and know when not to, follow optional chains, explain why force unwrapping traps, and model API data so that only truly optional values are optional.',
          'Next, Lesson 1.4: functions, parameters and closures, including the closures you will pass to almost every iOS API.')

write_deck(OUT13, '1.3', 'Swift Optionals', 'Swift Optionals')
