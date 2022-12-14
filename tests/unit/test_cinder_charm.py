#!/usr/bin/env python3

# Copyright 2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import charm
import ops_sunbeam.test_utils as test_utils


class _CinderOperatorCharm(charm.CinderOperatorCharm):

    def __init__(self, framework):
        self.seen_events = []
        self.render_calls = []
        super().__init__(framework)

    def _log_event(self, event):
        self.seen_events.append(type(event).__name__)

    def renderer(self, containers, container_configs, template_dir,
                 adapters):
        self.render_calls.append(
            (
                containers,
                container_configs,
                template_dir,
                adapters))

    def configure_charm(self, event):
        super().configure_charm(event)
        self._log_event(event)


class TestCinderOperatorCharm(test_utils.CharmTestCase):

    PATCHES = []

    @mock.patch(
        'charms.observability_libs.v0.kubernetes_service_patch.'
        'KubernetesServicePatch')
    def setUp(self, mock_patch):
        self.container_calls = {
            'push': {},
            'pull': [],
            'remove_path': []}
        super().setUp(charm, self.PATCHES)
        self.harness = test_utils.get_harness(
            _CinderOperatorCharm,
            container_calls=self.container_calls)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_pebble_ready_handler(self):
        self.assertEqual(self.harness.charm.seen_events, [])
        self.harness.container_pebble_ready('cinder-api')
        self.assertEqual(self.harness.charm.seen_events, ['PebbleReadyEvent'])
