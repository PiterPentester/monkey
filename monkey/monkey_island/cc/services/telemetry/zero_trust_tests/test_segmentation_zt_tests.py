import uuid

from common.data.zero_trust_consts import TEST_SEGMENTATION, STATUS_PASSED, STATUS_FAILED, \
    EVENT_TYPE_MONKEY_NETWORK
from monkey_island.cc.models import Monkey
from monkey_island.cc.models.zero_trust.event import Event
from monkey_island.cc.models.zero_trust.finding import Finding
from monkey_island.cc.models.zero_trust.segmentation_finding import SegmentationFinding
from monkey_island.cc.services.telemetry.zero_trust_tests.segmentation import create_or_add_findings_for_all_pairs
from monkey_island.cc.testing.IslandTestCase import IslandTestCase

FIRST_SUBNET = "1.1.1.1"
SECOND_SUBNET = "2.2.2.0/24"
THIRD_SUBNET = "3.3.3.3-3.3.3.200"


class TestSegmentationTests(IslandTestCase):
    def test_create_findings_for_all_done_pairs(self):
        self.fail_if_not_testing_env()
        self.clean_finding_db()

        all_subnets = [FIRST_SUBNET, SECOND_SUBNET, THIRD_SUBNET]

        monkey = Monkey(
            guid=str(uuid.uuid4()),
            ip_addresses=[FIRST_SUBNET])

        # no findings
        self.assertEquals(len(Finding.objects(test=TEST_SEGMENTATION)), 0)

        # This is like the monkey is done and sent done telem
        create_or_add_findings_for_all_pairs(all_subnets, monkey)

        # There are 2 subnets in which the monkey is NOT
        self.assertEquals(len(Finding.objects(test=TEST_SEGMENTATION, status=STATUS_PASSED)), 2)

        # This is a monkey from 2nd subnet communicated with 1st subnet.
        SegmentationFinding.create_or_add_to_existing_finding(
            [FIRST_SUBNET, SECOND_SUBNET],
            STATUS_FAILED,
            Event.create_event(title="sdf", message="asd", event_type=EVENT_TYPE_MONKEY_NETWORK)
        )

        self.assertEquals(len(Finding.objects(test=TEST_SEGMENTATION, status=STATUS_PASSED)), 1)
        self.assertEquals(len(Finding.objects(test=TEST_SEGMENTATION, status=STATUS_FAILED)), 1)
        self.assertEquals(len(Finding.objects(test=TEST_SEGMENTATION)), 2)
