//
//  HFST-Bridging-Header.h
//  Sanaporakone iOS
//
//  Bridging header to expose HFST C++ API to Swift
//

#ifndef HFST_Bridging_Header_h
#define HFST_Bridging_Header_h

#ifdef __cplusplus
extern "C" {
#endif

// Forward declarations
typedef struct HFSTGenerator HFSTGenerator;
typedef struct HFSTResult HFSTResult;

/**
 * Initialize HFST generator from a file path
 * @param filepath Path to the .hfst file
 * @return Opaque pointer to generator, or NULL on error
 */
HFSTGenerator* hfst_generator_create(const char* filepath);

/**
 * Perform a lookup in the FST
 * @param generator The generator instance
 * @param input Input string to look up
 * @param output_buffer Buffer to store results (caller allocated)
 * @param buffer_size Size of the output buffer
 * @return Number of results found, or -1 on error
 */
int hfst_generator_lookup(HFSTGenerator* generator,
                          const char* input,
                          char* output_buffer,
                          size_t buffer_size);

/**
 * Free the generator
 * @param generator The generator to free
 */
void hfst_generator_destroy(HFSTGenerator* generator);

/**
 * Get error message from last operation
 * @return Error string, or NULL if no error
 */
const char* hfst_get_last_error(void);

#ifdef __cplusplus
}
#endif

#endif /* HFST_Bridging_Header_h */
