# Lesson 0.4 — SwiftUI App Lifecycle vs UIKit AppDelegate

*iOS Architecture Mastery · Concept-first learning*

> Lesson text as shared; the deck (`index.html`) uses only this text. The banking app is **NPay**: the code's
> `BankingApp` is renamed `NPayApp` and "Banking Dashboard" is "NPay Dashboard". **Authored for the deck** (flagged):
> the outcomes slide, events 1, 3, 4 and 5 of the "What code runs?" map (the text shows only "scene becomes active"),
> and the answers to the four review questions (the text lists questions only).

We now understand how iOS launches, suspends, resumes and terminates applications. The next question: **how does our Swift code know that these events are happening?** Historically iOS developers used AppDelegate and later SceneDelegate; modern SwiftUI apps usually use the App protocol and scene lifecycle APIs. We'll understand all three.

## 1. Evolution of iOS app architecture

| Approach | Since | Role |
|---|---|---|
| UIKit + AppDelegate | iOS 2+ | App-level lifecycle and application events |
| UIKit + SceneDelegate | iOS 13+ | Scene-specific lifecycle, including multiple windows |
| SwiftUI App lifecycle | iOS 14+ | Declarative app and scene definitions |

These are not completely separate: SwiftUI and UIKit interoperate, and modern apps may combine them.

## 2. Traditional UIKit: AppDelegate

iOS system → *lifecycle callback* → AppDelegate → *coordinate application services* → application code.

```swift
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions:
            [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        print("Application launched")
        return true
    }
}
```

1. `@main` identifies the application entry point. 2. AppDelegate conforms to `UIApplicationDelegate`. 3. UIKit invokes lifecycle-related delegate methods. 4. The developer can initialize application-wide services.

**Analogy:** AppDelegate is like a hotel manager who receives important notifications from the hotel administration. But what about a hotel with several independently managed conference rooms? That brings us to scenes.

## 3. Why Apple introduced SceneDelegate

An iPad app shows two document windows in one process: Document A active, Document B background. If one window becomes inactive, should the whole app become inactive? **No** — another scene may still be active. UIKit's scene architecture gives each scene its own lifecycle.

```swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func sceneDidBecomeActive(_ scene: UIScene) {
        print("Scene became active")
    }

    func sceneWillResignActive(_ scene: UIScene) {
        print("Scene becoming inactive")
    }

    func sceneDidEnterBackground(_ scene: UIScene) {
        print("Scene entered background")
    }
}
```

Scene callbacks only, not the complete configuration a UIKit scene-based project needs.

## 4. Modern SwiftUI approach

```swift
import SwiftUI

@main
struct NPayApp: App {

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

Missing: no explicitly defined AppDelegate, no explicitly defined SceneDelegate, no manual window creation. SwiftUI and the system manage the normal app and scene infrastructure.

```swift
import SwiftUI

struct ContentView: View {

    @Environment(\.scenePhase)
    private var scenePhase

    var body: some View {
        Text("NPay Dashboard")
            .onChange(of: scenePhase) { oldPhase, newPhase in
                switch newPhase {
                case .active:
                    print("Active")
                case .inactive:
                    print("Inactive")
                case .background:
                    print("Background")
                @unknown default:
                    break
                }
            }
    }
}
```

The `scenePhase` environment value lets SwiftUI code respond to scene lifecycle changes.

## 5. Compare the approaches

| Responsibility | UIKit delegates | SwiftUI lifecycle |
|---|---|---|
| App entry | AppDelegate-based entry | `@main` App |
| UI creation | UIKit window/view controllers | WindowGroup and Views |
| Scene events | SceneDelegate callbacks | `scenePhase` |
| UI layout | Auto Layout, frames, constraints | Declarative layout |
| Navigation | UINavigationController | NavigationStack |
| State updates | Explicit updates, observation | State-driven view updates |

AppDelegate and SceneDelegate are lifecycle integration mechanisms, while SwiftUI is also a complete UI framework; they are not direct replacements for every UIKit feature.

## 6. What code runs?

| Event | UIKit | SwiftUI |
|---|---|---|
| *Authored:* App process launches | `application(_:didFinishLaunchingWithOptions:)` | the App is created; its body builds the scenes |
| Scene becomes active | `sceneDidBecomeActive(_:)` | `scenePhase` becomes `.active` — ready for foreground interaction |
| *Authored:* Scene becomes inactive | `sceneWillResignActive(_:)` | `scenePhase` becomes `.inactive` |
| *Authored:* Scene enters background | `sceneDidEnterBackground(_:)` | `scenePhase` becomes `.background` |
| *Authored:* Process terminated under pressure | no callback is guaranteed | no callback is guaranteed |

## 7. Can SwiftUI still use AppDelegate?

Yes, through `UIApplicationDelegateAdaptor`, for existing apps and certain system integrations.

```swift
import SwiftUI
import UIKit

class AppDelegate: NSObject, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions:
            [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        print("Application initialized")
        return true
    }
}

@main
struct NPayApp: App {

    @UIApplicationDelegateAdaptor(AppDelegate.self)
    var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## 8. When should we use which?

- **New application:** start with SwiftUI's App lifecycle unless you have a specific reason not to.
- **Existing UIKit application:** understand and maintain AppDelegate, SceneDelegate and view-controller lifecycle behavior.
- **Hybrid application:** use SwiftUI and UIKit interoperability, with delegate adaptation where required.

## 9. Check your understanding (answers authored)

1. **Is AppDelegate completely obsolete in SwiftUI?** No — SwiftUI apps can use one through `UIApplicationDelegateAdaptor`, and existing UIKit apps depend on it.
2. **Does every SwiftUI View have its own process?** No — views are values inside one app process.
3. **Does `scenePhase` `.background` mean the app has been suspended?** No — background is a scene state; suspension is a process condition that may follow.
4. **Will `applicationWillTerminate` always run before iOS kills an app?** No — a suspended app terminated under memory pressure gets no final callback.

## Summary

You can now explain why modern iOS apps use SwiftUI's declarative lifecycle, why UIKit delegate APIs still matter, and how scene-level events differ from application-process events.

**Next: Lesson 0.5 — iOS Threads, Main Thread, RunLoop and Event Handling.** We trace one button tap from the touchscreen through iOS event delivery, the main thread, SwiftUI state changes and screen rendering.
