//
//  HFSTGenerator.swift
//  Sanaporakone iOS
//
//  Swift wrapper for HFST morphology generator
//

import Foundation

/// Result from HFST lookup
struct HFSTLookupResult: Codable {
    let output: String
    let weight: Float
}

/// Errors that can occur during HFST operations
enum HFSTError: Error {
    case fileNotFound(String)
    case loadFailed(String)
    case lookupFailed(String)
    case invalidResult
}

/// Swift wrapper for HFST generator
class HFSTGenerator {
    private var generator: OpaquePointer?
    private let bufferSize = 1024 * 100  // 100KB buffer for results

    /// Initialize with path to .hfst file
    init(hfstPath: String) throws {
        guard FileManager.default.fileExists(atPath: hfstPath) else {
            throw HFSTError.fileNotFound(hfstPath)
        }

        generator = hfst_generator_create(hfstPath)

        if generator == nil {
            let errorMsg = String(cString: hfst_get_last_error() ?? "Unknown error")
            throw HFSTError.loadFailed(errorMsg)
        }
    }

    deinit {
        if let gen = generator {
            hfst_generator_destroy(gen)
        }
    }

    /// Perform lookup in the FST
    /// - Parameter input: Input string (e.g., "[WORD_ID=sanoa][UPOS=VERB][VOICE=ACT][MOOD=INDV][TENSE=PRESENT][PERS=SG3]")
    /// - Returns: Array of results, sorted by weight
    func lookup(_ input: String) throws -> [HFSTLookupResult] {
        guard let gen = generator else {
            throw HFSTError.lookupFailed("Generator not initialized")
        }

        let buffer = UnsafeMutablePointer<CChar>.allocate(capacity: bufferSize)
        defer { buffer.deallocate() }

        let count = hfst_generator_lookup(gen, input, buffer, bufferSize)

        if count < 0 {
            let errorMsg = String(cString: hfst_get_last_error() ?? "Unknown error")
            throw HFSTError.lookupFailed(errorMsg)
        }

        if count == 0 {
            return []
        }

        // Parse JSON results
        let jsonString = String(cString: buffer)
        guard let jsonData = jsonString.data(using: .utf8) else {
            throw HFSTError.invalidResult
        }

        do {
            let results = try JSONDecoder().decode([HFSTLookupResult].self, from: jsonData)
            // Sort by weight (lower is better in HFST)
            return results.sorted { $0.weight < $1.weight }
        } catch {
            throw HFSTError.invalidResult
        }
    }
}

// Example usage:
/*

 do {
     let bundlePath = Bundle.main.path(forResource: "omorfi.generate", ofType: "hfst")!
     let generator = try HFSTGenerator(hfstPath: bundlePath)

     // Generate "sanoo" (he/she says)
     let input = "[WORD_ID=sanoa][UPOS=VERB][VOICE=ACT][MOOD=INDV][TENSE=PRESENT][PERS=SG3]"
     let results = try generator.lookup(input)

     if let best = results.first {
         print("Generated form: \(best.output)")
     }
 } catch {
     print("Error: \(error)")
 }

 */
