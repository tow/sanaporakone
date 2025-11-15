//
//  HFSTWrapper.cpp
//  HFST C++ to C bridge for iOS
//
//  This file wraps the HFST C++ API in a C interface
//  so it can be called from Swift via a bridging header
//

#include "HFST-Bridging-Header.h"
#include <hfst/HfstTransducer.h>
#include <hfst/HfstInputStream.h>
#include <string>
#include <sstream>
#include <exception>

using namespace hfst;

// Thread-local error storage
static thread_local std::string last_error;

// Internal structure
struct HFSTGenerator {
    HfstTransducer* transducer;

    HFSTGenerator() : transducer(nullptr) {}
    ~HFSTGenerator() {
        delete transducer;
    }
};

extern "C" {

HFSTGenerator* hfst_generator_create(const char* filepath) {
    last_error.clear();

    try {
        HFSTGenerator* gen = new HFSTGenerator();

        // Open the HFST file
        HfstInputStream his(filepath);

        // Read the transducer
        gen->transducer = new HfstTransducer(his);

        return gen;
    } catch (const std::exception& e) {
        last_error = std::string("Failed to load HFST file: ") + e.what();
        return nullptr;
    } catch (...) {
        last_error = "Unknown error loading HFST file";
        return nullptr;
    }
}

int hfst_generator_lookup(HFSTGenerator* generator,
                          const char* input,
                          char* output_buffer,
                          size_t buffer_size) {
    last_error.clear();

    if (!generator || !generator->transducer) {
        last_error = "Invalid generator";
        return -1;
    }

    if (!input || !output_buffer || buffer_size == 0) {
        last_error = "Invalid parameters";
        return -1;
    }

    try {
        // Perform lookup
        HfstOneLevelPaths* results = generator->transducer->lookup(input);

        if (!results) {
            output_buffer[0] = '\0';
            return 0;
        }

        // Format results as JSON array for easy parsing in Swift
        std::ostringstream oss;
        oss << "[";

        bool first = true;
        for (auto it = results->begin(); it != results->end(); ++it) {
            if (!first) {
                oss << ",";
            }
            first = false;

            // Get the output string (first element of path)
            std::string output_str = it->second;

            // Get weight
            float weight = it->first;

            // Create JSON object
            oss << "{\"output\":\"" << output_str << "\",\"weight\":" << weight << "}";
        }

        oss << "]";

        std::string result = oss.str();
        int count = results->size();

        delete results;

        // Copy to output buffer
        if (result.length() >= buffer_size) {
            last_error = "Output buffer too small";
            return -1;
        }

        strcpy(output_buffer, result.c_str());
        return count;

    } catch (const std::exception& e) {
        last_error = std::string("Lookup failed: ") + e.what();
        return -1;
    } catch (...) {
        last_error = "Unknown error during lookup";
        return -1;
    }
}

void hfst_generator_destroy(HFSTGenerator* generator) {
    delete generator;
}

const char* hfst_get_last_error(void) {
    return last_error.empty() ? nullptr : last_error.c_str();
}

} // extern "C"
