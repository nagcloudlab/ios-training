# Lesson 0.8 — iOS Networking Architecture: From App to Server

*iOS Architecture Mastery · Foundation Series*

> Lesson text as shared; the deck (`index.html`) uses only this text. **PocketBank is renamed NPay** and the fictional
> host `api.pocketbank.example` becomes `api.npay.example`. "Trainer" material became speaker notes; the trainer
> questions became the review. **Authored for the deck** (flagged): the outcomes slide; request-journey steps 2–9
> (the text shows only step 1); the four failure states other than "Success"; review answers and traps.
> **Code change:** the ViewModel skeleton gains `import Foundation` (needed for `error.localizedDescription`); it
> still gives an expected "catch block unreachable" warning because the service call is deliberately a comment.

**Question:** When NPay displays your balance, where does it come from, and how does it reach the iPhone?

## 1. The problem
Illustrative NPay screen: available balance ₹25,000, Refresh Balance, recent transaction Coffee Shop −₹250.
Ask: is the balance in the SwiftUI screen, iPhone memory, or the bank's server? **The authoritative balance belongs to the backend; the app may hold a copy.** Responsibilities: server (authoritative data), networking layer (talks to the backend), SwiftUI (displays).

## 2. Big picture
SwiftUI View (user taps Refresh) → ViewModel (loading and screen state) → networking service (builds and performs the request) → URLSession / Foundation → bank API server (authorized requests). Conceptual; URLSession uses lower-level services. SwiftUI does not implement HTTP; MVVM is a code pattern, not an OS requirement.

## 3. A Refresh tap, step by step
1. SwiftUI — user taps Refresh; the action starts an async operation. 2–9 *authored:* ViewModel starts loading → service builds the request → URLSession sends it (task suspends) → TLS protects it → server checks authorization, returns JSON → service validates and decodes → ViewModel updates state → SwiftUI re-renders.

## 4. HTTP request
```
GET /api/accounts/123/balance HTTP/1.1
Host: api.npay.example
Accept: application/json
Authorization: Bearer <token>
```
Method, resource path, headers. The bearer token is sensitive: never log or expose it.

| Method | Typical purpose |
|---|---|
| GET | Retrieve a resource |
| POST | Submit data or initiate an operation |
| PUT | Replace a resource |
| PATCH | Partially update a resource |
| DELETE | Request deletion |

Methods describe intent; the server decides and enforces authorization.

## 5. HTTPS
TLS gives authenticated, encrypted transport and authenticates the server. HTTPS protects the connection only; the app still needs secure authentication, authorization, token handling and backend security.

## 6. URLSession
```swift
import Foundation

func fetchBalance() async throws -> Data {
    let url = URL(string: "https://api.npay.example/balance")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw URLError(.badServerResponse)
    }
    return data
}
```
Create the URL → ask URLSession → suspend at await → receive response or error → validate → return. `await` does not block a thread.

## 7. Codable
```json
{ "accountId": "123", "currency": "INR", "balanceMinor": 2500000 }
```
```swift
struct BalanceResponse: Decodable {
    let accountId: String
    let currency: String
    let balanceMinor: Int64
}
let response = try JSONDecoder().decode(BalanceResponse.self, from: data)
```
2,500,000 paise = ₹25,000. Integer minor units (or a decimal type) avoid floating-point issues.

## 8. MVVM connects networking to SwiftUI
View (balance, loading) → ViewModel (coordinates, observable state) → Service (URLSession, decoding) → Server.
```swift
import Foundation
import Observation

@MainActor
@Observable
final class BalanceViewModel {
    var balanceText = "—"
    var isLoading = false
    var errorMessage: String?

    func loadBalance() async {
        isLoading = true
        defer { isLoading = false }
        do {
            // Call an injected networking service.
            // Decode the response and format the balance.
            balanceText = "₹25,000"
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```
A teaching skeleton; the service is intentionally not implemented.

## 9. When the network fails
Success (₹25,000, valid data). *Authored:* no network (show last known balance, offer retry) · HTTP 401 (sign in again) · timeout (outcome may be unknown) · HTTP 500 (server error, try later). Do not retry every failure automatically: consider semantics, idempotency, authentication, rate limits; retrying a money transfer without idempotency protection is dangerous.

## 10. Networking and background execution
A normal foreground request is not guaranteed to continue after suspension. Background URLSession configurations handle supported uploads and downloads that must survive suspension or termination, under system scheduling. They are not a way to run arbitrary code after suspension.

## 11. Check your understanding
1. Does SwiftUI directly manage HTTP transport? **No.**
2. Does await necessarily block an OS thread? **No.**
3. Is HTTPS sufficient to secure a banking app? **No.**
4. Should every failed money-transfer POST be retried automatically? **No.**

## Final understanding
SwiftUI → ViewModel → Networking Service → URLSession → HTTPS → Server → JSON → Model → ViewModel → SwiftUI. Networking is asynchronous, security is layered, and error handling is part of the architecture.
