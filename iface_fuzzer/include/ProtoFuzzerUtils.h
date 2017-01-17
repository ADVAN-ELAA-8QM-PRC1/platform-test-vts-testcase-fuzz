/*
 * Copyright 2016 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef __VTS_PROTO_FUZZER_UTILS_H__
#define __VTS_PROTO_FUZZER_UTILS_H__

#include <iostream>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

#include "fuzz_tester/FuzzerBase.h"
#include "test/vts-testcase/fuzz/iface_fuzzer/proto/ExecutionSpecificationMessage.pb.h"
#include "test/vts/proto/ComponentSpecificationMessage.pb.h"

using std::cout;
using std::cerr;
using std::string;
using std::unordered_map;
using std::vector;

namespace android {
namespace vts {

// 64-bit random number generator.
class Random {
 public:
  Random(uint64_t seed) : rand_(seed) {}
  virtual ~Random() {}

  // Generates a 64-bit random number.
  virtual uint64_t Rand() { return rand_(); }
  // Generates a random number in range [0, n).
  virtual uint64_t operator()(uint64_t n) { return n ? Rand() % n : 0; }

 private:
  // Used to generate a 64-bit Mersenne Twister pseudo-ranom number.
  std::mt19937_64 rand_;
};

// Additional non-libfuzzer parameters passed to the fuzzer.
struct ProtoFuzzerParams {
  // Number of function calls per execution (fixed throught fuzzer run).
  size_t exec_size_;
  // VTS specs supplied to the fuzzer.
  vector<ComponentSpecificationMessage> comp_specs_;
};

// Parses command-line flags to create a ProtoFuzzerParams instance.
ProtoFuzzerParams ExtractProtoFuzzerParams(int argc, char **argv);

// Loads VTS HAL driver library.
FuzzerBase *InitHalDriver(const ComponentSpecificationMessage &comp_spec);

// Creates a key, value look-up table with keys being names of predefined types,
// and values being their definitions.
unordered_map<string, VariableSpecificationMessage> ExtractPredefinedTypes(
    const vector<ComponentSpecificationMessage> &specs);

// Call every API from call sequence specified by the
// ExecutionSpecificationMessage.
void Execute(FuzzerBase *hal, const ExecutionSpecificationMessage &exec_spec);

}  // namespace vts
}  // namespace android

#endif  // __VTS_PROTO_FUZZER_UTILS_H__