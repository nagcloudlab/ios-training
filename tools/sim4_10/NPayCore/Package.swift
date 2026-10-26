// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "NPayCore",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)   // ours: lets swift build and swift test run on the Mac
    ],
    products: [
        .library(
            name: "NPayDomain",
            targets: ["NPayDomain"]
        ),
        .library(
            name: "NPayData",
            targets: ["NPayData"]
        )
    ],
    targets: [
        .target(
            name: "NPayDomain"
        ),
        .target(
            name: "NPayData",
            dependencies: ["NPayDomain"]
        ),
        .testTarget(
            name: "NPayDomainTests",
            dependencies: ["NPayDomain"]
        ),
        .testTarget(   // Lesson 4.9 (ours): repository, use-case and integration tests need NPayData too
            name: "NPayDataTests",
            dependencies: ["NPayDomain", "NPayData"]
        )
    ]
)
