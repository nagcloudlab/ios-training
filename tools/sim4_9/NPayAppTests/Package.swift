// swift-tools-version: 6.0

// Test harness for the app's payment feature (Lesson 4.9): the app's own source files, symlinked from ../NPay, compiled
// as a module so Swift Testing can reach PaymentViewModel the way an Xcode test target's `@testable import NPay` would.
import PackageDescription

let package = Package(
    name: "NPayAppTests",
    platforms: [.iOS(.v17), .macOS(.v14)],
    dependencies: [.package(path: "../NPayCore")],
    targets: [
        .target(
            name: "NPayPayments",
            dependencies: [.product(name: "NPayDomain", package: "NPayCore")]
        ),
        .testTarget(
            name: "NPayPaymentsTests",
            dependencies: [
                "NPayPayments",
                .product(name: "NPayDomain", package: "NPayCore"),
                .product(name: "NPayData", package: "NPayCore")
            ]
        )
    ]
)
