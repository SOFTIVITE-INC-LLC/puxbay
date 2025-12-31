// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "PuxbaySDK",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15),
        .tvOS(.v13),
        .watchOS(.v6)
    ],
    products: [
        .library(
            name: "PuxbaySDK",
            targets: ["PuxbaySDK"]),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "PuxbaySDK",
            dependencies: []),
        .testTarget(
            name: "PuxbaySDKTests",
            dependencies: ["PuxbaySDK"]),
    ]
)
