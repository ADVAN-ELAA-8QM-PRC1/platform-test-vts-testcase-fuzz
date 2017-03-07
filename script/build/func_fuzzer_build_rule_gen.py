#
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys

from importlib import import_module


class FuncFuzzerBuildRuleGen(object):
    """Build rule generator for test/vts-testcase/fuzz.

    Attributes:
        _android_build_top: string, equal to environment variable ANDROID_BUILD_TOP.
        _project_path: string, path to test/vts-testcase/fuzz.
        _func_fuzzer_dir: string, path to test/vts-testcase/fuzz/func_fuzzer.
        _func_fuzzer_build_template: string, path to fuzzer build template file.
        _utils: test/vts-testcase/hal/script/build/build_rule_gen_utils module.
        _vts_spec_parser: tools that generates and parses vts spec with hidl-gen.
        _warning_header: string, warning header for every generated file.
    """
    def __init__(self, warning_header):
        """BuildRuleGen constructor.

        Args:
            warning_header: string, warning header for every generated file.
        """
        self._android_build_top = os.environ.get('ANDROID_BUILD_TOP')
        if not self._android_build_top:
            print 'Run "lunch" command first.'
            sys.exit(1)
        self._project_path = os.path.join(self._android_build_top, 'test',
                                          'vts-testcase', 'fuzz')
        self._func_fuzzer_dir = os.path.join(self._project_path, 'func_fuzzer')
        self._func_fuzzer_build_template = os.path.join(
            self._project_path, 'script', 'build', 'template',
            'func_fuzzer_build_template.bp')

        sys.path.append(
            os.path.join(self._android_build_top, 'test', 'vts-testcase', 'hal',
                         'script', 'build'))
        vts_spec_parser = import_module('vts_spec_parser')
        self._utils = import_module('build_rule_gen_utils')
        self._vts_spec_parser = vts_spec_parser.VtsSpecParser()
        self._warning_header = warning_header

    def UpdateBuildRule(self):
        """Updates build rules under test/vts-testcase/fuzz."""
        hal_list = self._vts_spec_parser.HalNamesAndVersions()
        self.UpdateTopLevelBuildRule()
        self.UpdateSecondLevelBuildRule(hal_list)
        self.UpdateHalDirBuildRule(hal_list)

    def UpdateTopLevelBuildRule(self):
        """Updates test/vts-testcase/fuzz/Android.bp"""
        self._utils.WriteBuildRule(
            os.path.join(self._func_fuzzer_dir, 'Android.bp'),
            self._utils.OnlySubdirsBpRule(self._warning_header, ['*']))

    def UpdateSecondLevelBuildRule(self, hal_list):
        """Updates test/vts-testcase/fuzz/<hal_name>/Android.bp"""
        top_level_dirs = dict()
        for target in hal_list:
            hal_dir = os.path.join(
                self._utils.HalNameDir(target[0]),
                self._utils.HalVerDir(target[1]))
            top_dir = hal_dir.split('/', 1)[0]
            top_level_dirs.setdefault(
                top_dir, []).append(os.path.relpath(hal_dir, top_dir))

        for k, v in top_level_dirs.items():
            file_path = os.path.join(self._func_fuzzer_dir, k, 'Android.bp')
            self._utils.WriteBuildRule(
                file_path,
                self._utils.OnlySubdirsBpRule(self._warning_header, sorted(v)))

    def UpdateHalDirBuildRule(self, hal_list):
        """Updates build rules for function fuzzers.

        Updates func_fuzzer build rules for each pair of
        (hal_name, hal_version) in hal_list.

        Args:
            hal_list: list of tuple of strings. For example,
                [('vibrator', '1.3'), ('sensors', '1.7')]
        """
        for target in hal_list:
            hal_name = target[0]
            hal_version = target[1]

            file_path = os.path.join(
                self._func_fuzzer_dir, self._utils.HalNameDir(hal_name),
                self._utils.HalVerDir(hal_version), 'Android.bp')

            self._utils.WriteBuildRule(
                file_path, self._FuncFuzzerBuildRuleFromTemplate(
                    hal_name, hal_version, self._func_fuzzer_build_template))

    def _FuncFuzzerBuildRuleFromTemplate(self, hal_name, hal_version,
                                         template_path):
        """Returns build rules in string form by filling out a template.

        Reads template from given path and fills it out.

        Args:
            template_path: string, path to build rule template file.
            hal_name: string, name of the hal, e.g. 'vibrator'.
            hal_version: string, version of the hal, e.g '7.4'

        Returns:
            string, complete build rules in string form
        """
        with open(template_path) as template_file:
            build_template = str(template_file.read())

        vts_spec_names = self._vts_spec_parser.VtsSpecNames(hal_name,
                                                            hal_version)

        result = self._warning_header
        for vts_spec in vts_spec_names:
            hal_iface_name = vts_spec.replace('.vts', '')
            if not self._IsFuzzable(hal_iface_name):
                continue
            result += self._FillOutBuildRuleTemplate(
                hal_name, hal_version, hal_iface_name, build_template)

        return result

    def _FillOutBuildRuleTemplate(self, hal_name, hal_version, hal_iface_name,
                                  template):
        """Returns build rules in string form by filling out given template.

        Args:
            hal_name: string, name of the hal, e.g. 'vibrator'.
            hal_version: string, version of the hal, e.g '7.4'
            hal_iface_name: string, name of a hal interface, e.g 'Vibrator'
            template: string, build rule template to fill out.

        Returns:
            string, complete build rule in string form.
        """
        build_rule = template
        build_rule = build_rule.replace('{HAL_NAME}', hal_name)
        build_rule = build_rule.replace('{HAL_NAME_DIR}',
                                        self._utils.HalNameDir(hal_name))
        build_rule = build_rule.replace('{HAL_VERSION}', hal_version)
        build_rule = build_rule.replace('{HAL_IFACE_NAME}', hal_iface_name)
        return build_rule

    def _IsFuzzable(self, component_name):
        """Checks if component is fuzzable.

        Args:
            component_name: string, name of component, e.g. 'types, 'Vibrator'

        Returns:
            True iff can generate a func_fuzzer for component_name.
        """
        if component_name == 'types':
            return False
        elif component_name.endswith('Callback'):
            return False
        else:
            return True