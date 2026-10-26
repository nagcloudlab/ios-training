"""Generates decks/unit-4/lesson-4.8/index.html from the Lesson 4.8 text (Modular Project Structure & Feature-Based
Architecture; Part 1 Sections 1-7, Part 2 Sections 8-15, a continuation from Section 15 to 24). Evidence: tools/sim4_8 -
NPay's code split into the section 2 folders (31 files, still one module), the text's NPayCore package (NPayDomain,
NPayData) built with SwiftPM for the Mac and the iOS Simulator and linked into the app, and violations.sh (four
boundary violations and the compiler's errors)."""
import html, os, re, sys
OUT48 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.8', 'Modular Project Structure<br>&amp; Feature Architecture',
            'From one long file to <b>feature folders and compiler-enforced modules</b>, without changing what NPay does.',
            'NPay has grown: screens, ViewModels, domain models, use cases, repositories, dependency injection, routing, shared components. How should all this be organized so the app can grow into a multi-team project? We reorganize NPay into feature folders, then extract a real Swift package, NPayCore, with NPayDomain and NPayData modules, link it into the app, and deliberately break the boundaries to see the compiler enforce them.')
outcomes_slide('4.8', [("folder", "Organize an app by feature, with layers inside"),
                       ("diff", "Tell a folder from a Swift module"),
                       ("key", "Choose access levels across modules"),
                       ("layers", "Build a local Swift package with targets"),
                       ("shield", "Keep the dependency graph acyclic and inverted"),
                       ("decision", "Decide how far to modularize, and migrate safely")])
where_slide('4.8', 'Today: where the code lives', (),
            '4.7: PaymentUIState and an honest payment lifecycle.',
            'Feature folders, Swift packages, access control.',
            'The architecture of the last seven lessons now needs a physical shape. Today nothing about NPay&rsquo;s behaviour changes; only where its code lives and which parts are allowed to see which. The text came in three pieces; the third continues from Section 15.',
            'The problem.')

# ================================================================== Part 1 (1, 2)
divider(1, "Organizing by feature", "From a pile of files to a map", 'Layer-first or feature-first.', 'The problem.')
TREE = """NPay/
├── App/            NPayRootView, NPayRouter, NPayFactory, …
├── Features/
│   ├── Home/       HomeScreen
│   ├── Payments/   PaymentsScreen, PaymentViewModel,
│   │               PaymentReviewSheet, PaymentSuccessScreen, …
│   ├── History/    HistoryScreen, TransactionDetailScreen
│   └── Profile/    ProfileScreen, AppearanceSettingsView
├── Domain/         Models (Money, Transaction), PaymentValidator
├── Data/           NPayStore, NPayStoreAccountRepository
└── DesignSystem/   NPayTheme, NPayButton, NPayCard, BalanceCard, …"""
S.append(slide("Part 1 &middot; Our current problem; design the structure (sections 1&ndash;2)", "Feature-first, with layers inside", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.75fr) minmax(0,1.25fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Layer-first", ul("Views/, ViewModels/, Models/, Repositories/", "Grouped by technical role"))}
        {card("Feature-first", ul("Features/Home, Payments, History, Profile", "Grouped by product capability"))}
        <div class="step">{console("Our NPay before today", ["1 file, 1,543 lines of app code"], 12)}</div>
      </div>
      <div class="step">{code("NPay after the reorganization (31 files, ours)", TREE, "font-size:11px")}</div>
    </div>
  </div>""", notes(('SAY', 'Imagine a project with every Swift file in one folder: content view, store, ViewModel, service, repository, balance card, history screen, review sheet, use case, policy, router, and forty more. The compiler copes; developers spend effort finding which file belongs to which feature. Two strategies: layer-first groups by technical responsibility, views, ViewModels, models; feature-first groups by product capability, Home, Payments, History, Profile.'),
                  ('SAY', 'Click: our evidence app was the extreme case: all of NPay in one file, one thousand five hundred and forty-three lines. Click: we split it into the text&rsquo;s structure, feature-first with layers inside: App for composition, Features for user-facing capabilities, Domain for business concepts, Data for data access, DesignSystem for reusable visuals. Thirty-one files. Our Domain folder keeps the app&rsquo;s own Money, Transaction and PaymentValidator; the extracted domain types live in the package we build in Part 4.'),
                  ('CONNECT', 'Did that create modules?'))))

# ================================================================== Part 2 (3, 4, 5)
divider(2, "Folders are not modules", "Organization versus boundaries", 'One app target, one module.', 'The test.')
REF = ["PaymentsScreen (Features/Payments)&ensp;&rarr; <b>NPay</b>.PaymentsScreen", "NPayStore (Data)&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&rarr; <b>NPay</b>.NPayStore",
       "Money (Domain/Models)&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&rarr; <b>NPay</b>.Money", "PaymentAmount (package)&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&rarr; <b>NPayDomain</b>.PaymentAmount",
       "InMemoryAccountRepository&ensp;&ensp;&ensp;&ensp;&rarr; <b>NPayData</b>.InMemoryAccountRepository"]
S.append(slide("Part 2 &middot; Does an Xcode folder create a Swift module? (sections 3, 5)", "String(reflecting:) names the module", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Inside the running app (simulator)", REF, 11)}
        <div class="step">{card("Same module, any folder", ul("No import between files", "Swift imports modules, not .swift files"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Folders", ul("Discoverability", "Organization only"))}</div>
        <div class="step">{card("Modules", ul("Explicit imports", "Compiler-enforced access"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Does moving files into folders create separate Swift modules? No. We asked the running app: String(reflecting:) prints a type&rsquo;s fully qualified name. PaymentsScreen in Features/Payments, NPayStore in Data, Money in Domain/Models: all NPay dot something. Different folders, one module, NPay. Only the types we put in the package report NPayDomain and NPayData.'),
                  ('SAY', 'Click: within one module, a type declared in one file is usable from another without importing anything, subject to access control. Swift imports modules, not individual files: import SwiftUI, never import PaymentAmount.swift. That is Unit 1 knowledge.'),
                  ('SAY', 'Click: folders improve discoverability. Click: modules enforce access boundaries and explicit imports. Related problems, different tools.'),
                  ('CONNECT', 'Reorganize without changing behaviour.'))))

VER = ["payment: Payment Recorded; 2,349,950 paise, 4 transactions", "Home:&ensp;&ensp;&ensp;&ensp;NPay; ₹23,499.50", "Payments: Payments", "History:&ensp;History; Sent to ravi@npay", "Profile:&ensp;Profile"]
S.append(slide("Part 2 &middot; Reorganize without changing behaviour (section 4)", "Move files; build; verify", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("For example", "PaymentViewModel.swift\n  → Features/Payments/PaymentViewModel.swift\nSendPaymentUseCase.swift\n  → Domain/UseCases/SendPaymentUseCase.swift\nInMemoryAccountRepository.swift\n  → Data/Repositories/InMemoryAccountRepository.swift", "font-size:12px")}
        {card("Rules", ul("No business-logic changes while moving", "Build after each small move", "Check target membership"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Reorganized NPay, simulator", VER, 11.5)}</div>
        <div class="step">{card("Removed, not changed", ul("Lesson 4.4&rsquo;s unused services", "Nothing used them since 4.6"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The first lab: create the folders and move each file into place, for example the ViewModel into Features/Payments, the use case into Domain/UseCases, the in-memory repository into Data/Repositories. The rule: don&rsquo;t change business logic while reorganizing, and build after every small move, so structural refactoring stays separate from behavioural change. Depending on your Xcode version, folders are synchronized groups or classic groups; either way check the files are still in the app target, or their declarations vanish from it.'),
                  ('SAY', 'Click: we verified the reorganized app, which also imports the package from Part 4: a payment still ends at 2,349,950 paise with four transactions; all four tabs open with their titles, Home showing ₹23,499.50 and History "Sent to ravi@npay" on top.'),
                  ('SAY', 'Click: one deliberate deletion, flagged: Lesson 4.4&rsquo;s PaymentService, demo and mock services, which nothing has used since 4.6. Removing dead code changes no behaviour, and keeps the new structure honest.'),
                  ('CONNECT', 'Modules matter because of access control.'))))

# ================================================================== Part 3 (6, 7)
divider(3, "Access control and modules", "What other modules may see", 'Six levels; one default.', 'The levels.')
AC = [("private", "Enclosing declaration"), ("fileprivate", "Same source file"), ("<b>internal</b>", "Same module (default)"),
      ("package", "Same Swift package"), ("public", "Other modules can use it"), ("open", "Also subclass / override outside")]
P = []
for i, (ic, t, sub) in enumerate([("code", "Swift sources", "types, protocols, extensions"), ("gear", "Swift compiler", "parse, type-check the module"), ("file", "Module interface", "declarations for importers"),
                                   ("layers", "Compiled code", "for linking"), ("phone", "App linking", "modules + resources")]):
    x = i * 228
    P.append(tall(x, 0, 208, 110, ic, t, sub, f'{i + 2}' if i < 4 else '6+', ''))
    if i < 4:
        P.append(wire(f'M{x + 209} 55H{x + 226}' + head(x + 226, 55, 'r')))
S.append(slide("Part 3 &middot; Access control; module compilation (sections 6&ndash;7)", "internal is the default: invisible outside the module", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      {tbl(["Level", "Visible to"], AC, 'tbl compact')}
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 6", "public struct PaymentAmount {\n    public let paise: Int\n}", "font-size:13px")}
        <div class="step">{card("Not automatic", ul("A public type doesn&rsquo;t make its members public", "Design the public API explicitly"))}</div>
      </div>
    </div>
    <div class="gap"></div>
    {cues(5)}
    {svg('0 0 1120 110', 'Swift sources, compiler, module interface, compiled implementation, app linking', 'build', P, 'max-height:96px')}
  </div>""", notes(('SAY', 'Swift&rsquo;s access levels: private, the enclosing declaration and its extensions in the same file; fileprivate, the source file; internal, the whole module, and the default; package, the whole Swift package; public, usable from other modules; open, which additionally allows subclassing and overriding from other modules for eligible classes.'),
                  ('SAY', 'The text&rsquo;s example makes PaymentAmount and its paise property public, visible to importing modules. Click: but a public type does not make every initializer or member public; the public API must be designed deliberately. We will see the compiler insist on this.'),
                  ('SAY', 'Click through the simplified module build, conceptual: the Swift sources; the compiler parses and type-checks the whole module; it emits a module interface exposing declarations to importers; compiled code for linking; and the app links the modules it needs, with resources. Conceptual: details depend on build settings.'),
                  ('CONNECT', 'Make real modules: a Swift package.'))))

# ================================================================== Part 4 (8, 9, 10)
divider(4, "A Swift package", "NPayCore: NPayDomain and NPayData", 'Built, tested, linked.', 'The graph.')
P = []
P.append(box(330, 0, 400, 56, "NPayApp", "screens, ViewModels, composition root", None, '', 'phone'))
P.append(wire('M450 57L250 104' + head(250, 104, 'd')))
P.append(wire('M610 57L810 104' + head(810, 104, 'd')))
P.append(box(80, 106, 340, 56, "NPayData", "repository implementations", None, '', 'db'))
P.append(box(640, 106, 340, 56, "NPayDesignSystem", "reusable UI (later)", None, 'ghost', 'frame'))
P.append(wire('M250 163L450 210' + head(450, 210, 'd')))
P.append(wire('M530 57V210' + head(530, 210, 'd'), None, 'dash'))
P.append(box(330, 212, 400, 56, "NPayDomain", "models, use cases, repository contracts", '1+', '', 'key'))
MAN = """// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "NPayCore",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(name: "NPayDomain", targets: ["NPayDomain"]),
        .library(name: "NPayData", targets: ["NPayData"])
    ],
    targets: [
        .target(name: "NPayDomain"),
        .target(name: "NPayData",
                dependencies: ["NPayDomain"]),
        .testTarget(name: "NPayDomainTests",
                    dependencies: ["NPayDomain"])
    ]
)"""
S.append(slide("Part 4 &middot; Swift Package Manager and the module graph (sections 8&ndash;10)", "NPayCore&rsquo;s Package.swift", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 1060 270', 'NPayApp depends on NPayData and NPayDomain; NPayData depends on NPayDomain; a design system module later', 'graph', P, 'max-height:270px')}
        <div class="step">{card("Why", ul("NPayDomain needn&rsquo;t import SwiftUI", "Dependencies become explicit"))}</div></div>
      {code("Package.swift (section 10, condensed)", MAN, "font-size:10.5px")}
    </div>
  </div>""", notes(('SAY', 'Swift Package Manager organizes code into targets and products. For NPay the text plans NPayDomain, NPayData and eventually NPayDesignSystem. The graph: the app depends on NPayData and NPayDomain; NPayData depends on NPayDomain; click: the domain, in teal, depends on nothing of ours. A general-purpose design system can stay independent of the domain; it is greyed out because we are not extracting it yet.'),
                  ('SAY', 'Click: why? To make dependencies explicit: NPayDomain should not need SwiftUI, NPayData may use the domain, the app composes both.'),
                  ('SAY', 'The manifest, condensed on the slide: tools version 5.9, an iOS 17 platform, two library products, two targets with NPayData depending on NPayDomain, and a test target for the domain. We built exactly this, with the text&rsquo;s domain and data files, in tools/sim4_8/NPayCore.'),
                  ('CONNECT', 'What happened when we built it.'))))

BLD = ["swift build (Mac), the manifest as written:", "&ensp;error: 'now' is only available in macOS 12 or newer", "&ensp;(InMemoryAccountRepository: createdAt: .now)", "",
       "+ .macOS(.v14) (ours):", "&ensp;Compiling NPayDomain &hellip; then NPayData &hellip; Build complete!", "swift test: 2 tests passed", "",
       "swift build --triple arm64-apple-ios17.0-simulator: Build complete!"]
S.append(slide("Part 4 &middot; Building NPayCore (sections 10, 15)", "Valid for iOS; the Mac needs a platform too", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {console("Our builds", BLD, 11)}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why it failed on the Mac", ul("Only iOS is listed", "macOS falls back to an old default", "<code>swift test</code> runs on the Mac"))}</div>
        <div class="step">{card("Build order", ul("NPayDomain before NPayData: the graph decides", "Independent targets may build in parallel"))}</div>
        <div class="rule step" data-label="A module">{ul("A compile and visibility boundary", "Not a process or a microservice")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'We built the text&rsquo;s package. On the Mac, with the manifest as written, it failed: "now is only available in macOS 12 or newer", from InMemoryAccountRepository&rsquo;s createdAt: .now. Click: the manifest only lists iOS, so a Mac build, which is how swift test runs a package&rsquo;s tests, falls back to an old macOS default. Adding a macOS 14 platform, our flagged change, fixed it.'),
                  ('SAY', 'Then: NPayDomain compiled first, NPayData after it, build complete; swift test passed two domain tests; and the same package cross-built for the iOS Simulator. Click: SwiftPM resolved the graph and ordered the work: NPayDomain must exist before NPayData can import it. Independent targets may compile concurrently; the graph is a logical ordering, not strict sequencing.'),
                  ('SAY', 'Click: and a module is a compilation and visibility boundary. It is not a separate process, container or microservice: everything still links into one app.'),
                  ('CONNECT', 'Cross-module access, in practice.'))))

# ================================================================== Part 5 (11, 12, 17, 18)
divider(5, "Crossing the boundary", "public types, public initializers", 'What the compiler demands.', 'The contract.')
PUB = """public struct PaymentRecord: Identifiable, Sendable {
    public let id: UUID
    public let recipient: String
    public let amountPaise: Int
    public let createdAt: Date

    public init(id: UUID, recipient: String,
                amountPaise: Int, createdAt: Date) {
        self.id = id
        self.recipient = recipient
        self.amountPaise = amountPaise
        self.createdAt = createdAt
    }
}

public protocol AccountRepository: Sendable {
    func fetchSnapshot() async throws -> AccountSnapshot
    func recordPayment(recipient: String, amountPaise: Int)
        async throws -> PaymentRecord
}"""
VIO = ["no explicit public init on PaymentRecord:", "&ensp;NPayData: 'PaymentRecord' initializer is inaccessible", "&ensp;due to 'internal' protection level", "",
       "PaymentRecord not public:", "&ensp;NPayDomain itself: property / initializer / method", "&ensp;cannot be declared public because its type uses", "&ensp;an internal type"]
S.append(slide("Part 5 &middot; Cross-module access control (sections 11&ndash;12, 17&ndash;18)", "The compiler checks the public contract", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:22px;align-items:start">
      {code("NPayDomain/AccountRepository.swift (section 17, condensed)", PUB, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("violations.sh (ours), swift build", VIO, 11)}</div>
        <div class="step">{card("Learned", ul("Memberwise inits stay internal: write public ones", "Public API can&rsquo;t expose internal types"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Once the domain moves into NPayDomain, every type and requirement used across the boundary must be public, and the text adds explicit public initializers. PaymentRecord gets a public init; AccountSnapshot too; the protocol&rsquo;s requirements are public through the protocol. NPayData then imports NPayDomain and declares public actor InMemoryAccountRepository with a public init and public methods.'),
                  ('SAY', 'Click: we broke it on purpose, with a script of ours. Remove PaymentRecord&rsquo;s explicit public init: NPayData fails, "PaymentRecord initializer is inaccessible due to internal protection level": a public struct&rsquo;s synthesized memberwise initializer is not public, the common surprise when extracting code. Remove public from PaymentRecord itself: the text expected the app to fail, but the domain module fails first, because its own public snapshot, protocol and initializer use the now-internal type.'),
                  ('SAY', 'Click: so module boundaries turn architectural intentions into compiler-checked constraints: nobody can reach an internal detail from another module by accident.'),
                  ('CONNECT', 'Which way may modules depend?'))))

# ================================================================== Part 6 (16, 19, 20)
divider(6, "Dependency direction", "Acyclic, and inverted", 'The domain knows no implementation.', 'Cycles.')
DIR = ["NPayDomain imports NPayData (no dependency declared):", "&ensp;error: no such module 'NPayData'", "",
       "NPayDomain depends on NPayData (a cycle):", "&ensp;error: cyclic dependency declaration found:", "&ensp;NPayData -> NPayDomain -> NPayData"]
COMP = """import SwiftUI
import NPayDomain
import NPayData

@MainActor
final class NPayDependencies {
    let repository: any AccountRepository

    init() {
        repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000)
    }
}"""
S.append(slide("Part 6 &middot; Dependency direction across modules (sections 16, 19&ndash;20)", "Contracts in the domain; implementations depend on them", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("violations.sh (ours)", DIR, 11)}
        <div class="step">{card("How to avoid it", ul("AccountRepository in NPayDomain", "InMemoryAccountRepository in NPayData", "The app composes them"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("Section 19: the composition root", COMP, "font-size:11px")}</div>
        <div class="step">{console("From NPay&rsquo;s app module (simulator)", ["NPayDomain use case over NPayData repository:", "recorded 150050; balance 2349950"], 11)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'App to Data to Domain is fine. A cycle, domain depending on data while data depends on domain, is not, and SwiftPM requires an acyclic target graph. We tried both of the text&rsquo;s violations. Importing NPayData inside NPayDomain without declaring the dependency: "no such module NPayData". Declaring the dependency, making a cycle: "cyclic dependency declaration found: NPayData, NPayDomain, NPayData". The package refuses to build.'),
                  ('SAY', 'Click: the way out is dependency inversion across modules: the AccountRepository protocol in NPayDomain, the actor in NPayData conforming to it, and the app composing them. The domain stays independent of infrastructure. Click: Section 19&rsquo;s composition root imports both modules and creates one InMemoryAccountRepository behind the protocol; later, an API-backed repository replaces it while the contract stays.'),
                  ('SAY', 'Click: we ran that composition from inside NPay&rsquo;s app module: the NPayDomain use case, on an NPayData repository: 150,050 paise recorded, balance 2,349,950. NPay&rsquo;s own screens still use our adapter over NPayStore, which now conforms to the imported protocol, so Home and History keep their source of truth.'),
                  ('CONNECT', 'How far should we go?'))))

# ================================================================== Part 7 (13, 14, 21, 22, 23)
divider(7, "How far to modularize", "Solve a real problem; migrate in steps", 'And keep NPay working throughout.', 'Stages.')
STG = [("Current", "One app target, feature folders"), ("Next", "Extract stable domain code: NPayDomain"), ("Later", "Extract data implementations: NPayData"), ("Larger app", "Feature modules where justified")]
S.append(slide("Part 7 &middot; Not 20 packages; feature vs shared modules (sections 13&ndash;14, 21)", "Modularity has a cost", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Stage", "Architecture"], STG, 'tbl compact')}
        <div class="step">{card("Every module costs", ul("Public API decisions", "Dependency and build configuration", "Integration overhead"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Shared vs feature", ul("NPayDesignSystem: NPayButton, NPayCard, NPayTheme", "PaymentReviewSheet stays in Payments"))}</div>
        <div class="rule step" data-label="Principle">{ul("Extract stable, meaningful contracts", "Modularize to solve a real ownership, dependency or build problem")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Why not twenty packages immediately? Every module brings public API decisions, dependency management, build configuration and integration overhead; for a small app, too many modules make development harder. NPay evolves in stages: one target with feature folders now; extract the stable domain; later the data implementations; feature modules only when the app is large enough to justify them. Click: we just felt that cost: one missing platform line, one missing public init.'),
                  ('SAY', 'Click: with several teams owning Payments, History and Profile, feature modules can mark ownership. Shared code goes in shared modules, carefully: a design system with NPayButton, NPayCard and NPayTheme; but a payment-specific PaymentReviewSheet stays in Payments. Don&rsquo;t move code into a shared module just because two files use it.'),
                  ('SAY', 'Click: the text&rsquo;s strategy chooser: a small app, one target with feature folders; growing and multi-team apps, more modules. Modularization should solve a real maintenance, ownership, dependency or build problem; more modules is not better architecture by itself.'),
                  ('CONNECT', 'The migration, step by step.'))))

MIG = [("1", "Reorganize into feature folders", "&#10003; app builds; 31 files"), ("2", "Extract domain models", "&#10003; NPayDomain builds"), ("3", "Extract the repository protocol", "&#10003; the app imports NPayDomain"),
       ("4", "Extract the in-memory repository", "&#10003; NPayData builds"), ("5", "Update the composition root", "&#10003; one repository (adapter) per app"), ("6", "Payment integration test", "&#10003; 2,349,950, History row"),
       ("7", "Verify all four tabs", "&#10003; NPay, Payments, History, Profile")]
S.append(slide("Part 7 &middot; Migrate NPay safely (sections 22&ndash;23)", "One architectural change at a time", f"""  <div class="body">
    {tbl(["Step", "Action", "Verified (ours)"], MIG, 'tbl compact')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Checklist extras", ul("No circular dependencies: SwiftPM enforces it", "Run in the iOS Simulator: done"))}</div>
      <div class="warn step" data-label="Don&rsquo;t">{ul("Rename, move, re-route and rewrite at once")}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s migration plan, and how each step went for us. Reorganize into feature folders: the app builds, thirty-one files. Extract domain models: NPayDomain builds. Extract the repository protocol: the app imports NPayDomain. Extract the in-memory repository: NPayData builds. Update the composition root: one repository for the app, our adapter over NPayStore. The payment test: 2,349,950 paise and the History row. All four tabs: verified.'),
                  ('SAY', 'Click: the checklist&rsquo;s other items: no circular module dependencies, which SwiftPM now enforces for us, and a run in the iOS Simulator, done throughout.'),
                  ('SAY', 'Click: the warning: do not rename every type, move every file, rewrite navigation and change the payment workflow at the same time. One architectural change, then build and test.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.8', (), [("folder", "Folders organize; modules enforce", "31 files, still NPay.*; package types: NPayDomain.*"),
                     ("key", "public is a deliberate contract", "memberwise inits stay internal; public API can&rsquo;t use internal types"),
                     ("shield", "Acyclic and inverted", "SwiftPM rejected the cycle; the domain imports nothing of ours")],
          'Three things to remember. Feature folders make NPay navigable, but every file is still in the NPay module: only a target or package creates a module. Across a module boundary, public is a deliberate contract: the compiler rejected a missing public initializer and a public API built on an internal type. And the module graph must be acyclic, with the domain at the centre: contracts in NPayDomain, implementations in NPayData depending on it, and the app composing both, which SwiftPM enforced when we tried to break it.')

review_divider(10)
review([("folder", "Question", "Does moving a Swift file into an Xcode folder create a new module?",
         "Does moving a Swift file into an Xcode folder create a new module?", "No",
         "Every folder&rsquo;s types reported NPay.*.",
         "Treating folders as boundaries.", "Some say yes.", None),
        ("key", "Choose one", "What does internal mean in Swift?",
         "What does <code>internal</code> mean in Swift?<br>A. Visible only in one function<br>B. Visible to every module<br>C. Visible within the same module", "C",
         "The default; invisible from NPayData unless public.",
         "Confusing internal with private.", "Most pick C.", None),
        ("db", "Choose one", "Why must NPayData import NPayDomain?",
         "Why must NPayData import NPayDomain?<br>A. It uses domain models and repository contracts<br>B. It needs SwiftUI previews<br>C. It creates navigation routes", "A",
         "It conforms to AccountRepository and builds PaymentRecords.",
         "Thinking data owns the contract.", "Most pick A.", None),
        ("shield", "Question", "Should NPayDomain import NPayData?",
         "Should NPayDomain import NPayData?", "No",
         "&ldquo;no such module&rdquo;, or a cycle error.",
         "Letting policy depend on details.", "Most say no.", None),
        ("file", "Question", "Does a public struct automatically get a public memberwise initializer?",
         "Does a public Swift struct automatically have a public memberwise initializer?", "No",
         "&ldquo;initializer is inaccessible due to internal protection level&rdquo;.",
         "Expecting public to cascade.", "Some say yes.", None),
        ("layers", "Question", "Can Swift Package Manager targets have circular dependencies?",
         "Can Swift Package Manager targets have circular dependencies?", "No",
         "&ldquo;cyclic dependency declaration found&rdquo;.",
         "Solving a cycle with another import.", "Most say no.", None),
        ("decision", "Question", "Should every small feature automatically become a separate package?",
         "Should every small feature automatically become a separate package?", "No",
         "Each module costs API design and build configuration.",
         "Equating more modules with better architecture.", "Most say no.", None),
        ("code", "Predict the result", "Remove public from PaymentRecord: where does the build fail first?",
         "In NPayCore, <code>public struct PaymentRecord</code> becomes <code>struct PaymentRecord</code>. Where does the build fail first?<br>A. Only in the app<br>B. In NPayDomain itself<br>C. Nowhere", "B",
         "Its own public API uses the now-internal type.",
         "Expecting errors only at the use site.", "Many pick A.", None),
        ("gear", "Predict the result", "The text's manifest (iOS only): swift build on a Mac?",
         "The section 10 manifest lists only <code>.iOS(.v17)</code>. Running <code>swift build</code> on a Mac&hellip;<br>A. Succeeds<br>B. Fails: <code>.now</code> needs macOS 12<br>C. Builds for iOS instead", "B",
         "macOS falls back to an old default; add .macOS(.v14).",
         "Forgetting where tests run.", "Most pick A.", None),
        ("clock", "Choose one", "From 4.7: a payment task is cancelled after the payment is recorded. The state should be&hellip;",
         "From Lesson 4.7: a payment task is cancelled after the server recorded the payment but before the reply. The honest UI state is&hellip;<br>A. failure<br>B. success<br>C. statusUnknown", "C",
         "Our run said failure while the money had moved.",
         "Treating cancellation as failure.", "Some pick A.", "Spaced review from Lesson 4.7.")])

S.append(next_slide('4.8', [("4.9", "Architecture testing", "Swift Testing on NPayDomain, NPayData and ViewModels"),
                            ("4.10", "Integration lab", "a complete MVVM NPay on these modules"),
                            ("Unit 5", "Networking", "an API repository in a data module"),
                            ("Unit 11", "Build &amp; delivery", "targets, schemes and configurations at scale")],
                    'Lesson 4.9 writes proper tests against these modules, with Swift Testing and XCTest, mocks and async tests. 4.10 consolidates Unit 4 into a complete MVVM NPay. Unit 5 adds an API-backed repository, and Unit 11 deals with builds and delivery at scale.'))

S.append(lab_slide('4.8', "NPay module verification", "Folders first; then a package.",
                   ["Reorganize NPay into feature folders; build.",
                    "Create NPayCore with NPayDomain and NPayData.",
                    "Move the domain types; make the API public.",
                    "Move InMemoryAccountRepository into NPayData.",
                    "Import both; one repository in the composition root.",
                    "Break a boundary on purpose; read the error."],
                   "", 'Expected, as in our run: the app still pays and shows all four tabs; types report their module; a missing public init, a non-public type, a forbidden import and a cycle each fail with a clear error.',
                   side=f'<div>{card("You hand in", ul("Your folder tree and Package.swift", "A payment after the migration", "The four compiler errors"))}</div>'))

end_slide('4.8', 'Modular Project Structure<br>&amp; Feature Architecture', 'Lesson 4.9 &mdash; Architecture Testing',
          'You can now organize an app by feature, tell folders from modules, design a public API across modules, build a local Swift package, and keep the dependency graph acyclic and inverted.',
          'Next, Lesson 4.9: architecture testing with Swift Testing and XCTest.')

write_deck(OUT48, '4.8', 'Modular Project Structure &amp; Feature Architecture', 'Modular Project Structure &amp; Feature Architecture')
