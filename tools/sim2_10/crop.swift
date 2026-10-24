// Crops a simulator screenshot to its content: full width, the rows below the status bar that hold
// non-white pixels, plus a margin. Usage: swift crop.swift in.png out.png [margin]
import AppKit

let args = CommandLine.arguments
let margin = args.count > 3 ? Int(args[3])! : 120
guard let src = NSImage(contentsOfFile: args[1]), let cg = src.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fatalError("cannot read \(args[1])") }
let w = cg.width, h = cg.height
let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
let px = ctx.data!.bindMemory(to: UInt8.self, capacity: w * h * 4)
let statusBar = h / 15
var top = h, bottom = 0
for y in statusBar..<h {               // row 0 is the top of the image
    for x in stride(from: 0, to: w, by: 2) {
        let i = (y * w + x) * 4
        if px[i] < 235 || px[i + 1] < 235 || px[i + 2] < 235 { top = min(top, y); bottom = max(bottom, y); break }
    }
}
let y0 = max(statusBar, top - margin), y1 = min(h, bottom + margin)
let out = cg.cropping(to: CGRect(x: 0, y: y0, width: w, height: y1 - y0))!
let rep = NSBitmapImageRep(cgImage: out)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[2]))
print("\(args[2]): rows \(y0)–\(y1)")
