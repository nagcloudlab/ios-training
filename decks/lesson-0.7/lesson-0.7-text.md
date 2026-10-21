# Lesson 0.7 — iOS Security Architecture

*iOS Architecture Mastery · Foundation Series*

> Lesson text as shared; the deck (`index.html`) uses only this text. **PocketBank is renamed NPay** (the course's
> running app); PhotoGallery and ShopEasy are kept. "Trainer" material became speaker notes; the knowledge check
> became the review. **Authored for the deck** (flagged): the outcomes slide, the "Allow" and "Don't Allow" result
> wording in the camera flow, review answers and traps. The shared text ends after the knowledge check ("next").

**Question:** If thousands of apps run on an iPhone, how does iOS prevent one from stealing another's data?
Apps: NPay (bank data), PhotoGallery (private photos), ShopEasy (orders). Can ShopEasy read NPay's private files? Can NPay secretly activate the camera? Can a malicious app replace another app's executable?

## 1. The security problem
Apps come from many developers and cannot be trusted equally; the OS must provide isolation. **Principle of least privilege:** apps should only access resources they are authorized to use.

## 2. The big picture (conceptual layers, overlapping)
Application security (secure coding, authentication, data handling) · Privacy & permissions (camera, microphone, photos, location) · Sandbox & entitlements (filesystem boundaries, approved capabilities) · Code signing & runtime protections (code integrity, platform enforcement) · Kernel & hardware security (process isolation, memory protection, Secure Enclave).
**Analogy:** an airport — passing one checkpoint does not grant access to everything; a signed app cannot use every device capability.

## 3. The App Sandbox
Restricts what an app process can access; each app has a private container. ShopEasy accessing its own files: normally allowed. NPay's private files directly: blocked. A document shared through an approved system interface: allowed. The sandbox does not mean apps never exchange data — App Groups, extensions, document pickers and system-mediated services allow **authorized** sharing.

## 4. Entitlements
A signed declaration of a capability (e.g. App Groups, certain Apple services): NPay → signed entitlements → system-enforced capabilities. Not a runtime boolean; it must be configured, signed and accepted by the platform.

| Entitlement | Privacy permission |
|---|---|
| Declares an app capability | Authorizes access to privacy-sensitive resources |
| Usually configured at build/signing time | Often involves user choice at runtime |
| Example: App Groups | Example: Camera access |
| Enforced by platform services | Enforced by privacy and system APIs |

Some capabilities also require runtime authorization; the mechanisms work together.

## 5. NPay requests the camera
User taps Scan Cheque → NPay requests camera authorization → system prompt: not determined / Allow / Don't Allow. A real app needs a privacy usage description such as `NSCameraUsageDescription`, and should explain why before the prompt appears.

## 6. Code signing
Developer builds the app → app is signed (signature and metadata protect integrity) → iOS validates execution requirements → app runs under restrictions (signing does not bypass sandbox or privacy controls). A valid signature does **not** guarantee the app has no vulnerabilities: it establishes identity and integrity, not secure logic.

## 7. Keychain
UserDefaults: preferences and lightweight settings (theme, onboarding completed). Keychain: credentials and small secrets (authentication tokens, cryptographic key references). Keychain items have accessibility policies, e.g. WhenUnlocked; choose by security and background-access needs.

## 8. The Secure Enclave
A hardware security subsystem on supported devices: app process → security frameworks (Keychain, LocalAuthentication, CryptoKit, Security APIs) → Secure Enclave (protected key operations). Not every Keychain item is stored in the Secure Enclave; it supports particular operations and key types, not general data.

## 9. Putting it together — NPay login
Open NPay (signed, sandboxed) → authenticate over authenticated HTTPS → backend returns a token, the app validates it → token stored with Keychain accessibility and access controls → later, credentials retrieved when appropriate. Production also needs backend authorization, token lifecycle management, secure sessions, fraud controls, logging policies and threat modeling.

## 10. Check your understanding
1. Can one app directly read another app's private container? **Normally no.**
2. Does code signing mean an app is free of vulnerabilities? **No.**
3. Where should an authentication token generally be stored? **Keychain.**
4. Is every Keychain item stored in the Secure Enclave? **No.**

## Deck changes after the Unit 00 audit

The deck (`index.html`, built by `tools/gen07.py`) now differs from the text above as follows. Items marked *authored* are not in the text.

**Corrections**
- Secure Enclave: Keychain items are **not** stored in the Secure Enclave. The Keychain is an encrypted database; the Secure Enclave protects the keys that encrypt it and can create P-256 private keys that never leave it (Part 8 diagram and rule rewritten; review question 4 answer reworded).
- Camera: a missing `NSCameraUsageDescription` makes iOS terminate the app when it asks for the camera; after Don't Allow the app cannot ask again and can only offer another way and send the user to Settings.

**Cuts and moves**
- Part 9 (secure login, end to end) moved to Lesson 0.8 Part 4 ("Where the token comes from"), where the bearer token is used.

**Consistency**
- The airport analogy is replaced by the course's hotel analogy from Lesson 0.1 (room = sandbox, key = signing/entitlements, in-room safe = Keychain).
- Lesson 0.7 is the one place that teaches "token in UserDefaults?"; Part 7 is now a diagram (UserDefaults as a preferences file inside NPay's container vs the Keychain managed by iOS).

**Visuals**
- Part 4's comparison table became a two-lane diagram (entitlement at build/signing time vs permission at run time).

**Authored additions**
- "Where we are" slide on the NPay architecture map (bridge from Lesson 0.6).
- One-line pointers: widgets/extensions are separate sandboxed processes sharing via App Groups (10.9); privacy manifest (11.8); Keychain accessibility (7.3); Secure Enclave from CryptoKit (7.5); ATS (7.6).
- Recap slide; review expanded to 5 questions (two multiple choice, one spaced item from 0.6); "Where this goes next" (7.1, 7.2, 7.3, 7.5, 7.6, 7.8); lab "Map NPay's threats" (six items: where each lives, what protects it); end slide names Lesson 0.8.
