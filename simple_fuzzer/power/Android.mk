#
# Copyright (C) 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
module_name := IPowerPowerHint_fuzzer
module_src_files := IPowerPowerHint_fuzzer.cpp
module_shared_libraries := android.hardware.power@1.0
include test/vts-testcase/fuzz/simple_fuzzer/common/Android.hal_fuzzer.mk

include $(CLEAR_VARS)
module_name := IPowerSetFeature_fuzzer
module_src_files := IPowerSetFeature_fuzzer.cpp
module_shared_libraries := android.hardware.power@1.0
include test/vts-testcase/fuzz/simple_fuzzer/common/Android.hal_fuzzer.mk

include $(CLEAR_VARS)
LOCAL_MODULE := IPowerFuzzTest
VTS_CONFIG_SRC_DIR := testcases/hal/power/fuzz
include test/vts/tools/build/Android.host_config.mk
