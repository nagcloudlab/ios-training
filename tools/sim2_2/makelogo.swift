// Draws the demo NPayLogo asset (360 x 360 px, used at 3x = 120 pt). Usage: swift makelogo.swift out.png
import AppKit
let size = 360
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size, bitsPerSample: 8, samplesPerPixel: 4,
                           hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1).setFill()            // navy
NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: size, height: size), xRadius: 80, yRadius: 80).fill()
let attrs: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: 190, weight: .heavy),
                                            .foregroundColor: NSColor(red: 0.05, green: 0.58, blue: 0.53, alpha: 1)]   // teal
let s = NSAttributedString(string: "N", attributes: attrs)
let b = s.size()
s.draw(at: NSPoint(x: (CGFloat(size) - b.width) / 2, y: (CGFloat(size) - b.height) / 2))
NSGraphicsContext.current = nil
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
