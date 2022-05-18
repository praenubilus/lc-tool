""" Unit Tests for data.Problem class
"""
import pytest
from Data import Data, Problem
import config


# pytestmark = pytest.mark.timeout(5)

TEST_DATA_PATH = "test.json"
TEST_QID = 1
TEST_QID_STR = str(TEST_QID).zfill(config.QID_PADDING_SIZE)
TEST_Q_DIFFICULTY = 1
TEST_Q_PREMIUM = False
TEST_Q_TITLE = "Two Sum"
TEST_Q_TITLE_SLUG = "two-sum"
TEST_Q_TITLE_URL = "https://leetcode.com/problems/two-sum"
TEST_Q_TITLE_URL_SOLUTION = "https://leetcode.com/problems/two-sum/solution"


@pytest.fixture(scope="function")
def prob():
    data = Data(TEST_DATA_PATH, preload=True, fetch_rule=False)
    return Problem(qid=TEST_QID, blob=data.data[TEST_QID_STR], auto_parse=False)


#############################################################
##  Tests for Problem Class
#############################################################


def test_problem_init(prob):
    assert TEST_QID_STR == prob.qid
    assert TEST_Q_DIFFICULTY == prob.difficulty
    assert TEST_Q_PREMIUM == prob.is_paid
    assert prob.stat is not None


def test_problem_parse_statistics(prob):
    acs, subs, ac_rate = prob._parse_statistics(prob.stat)
    assert acs > 0
    assert subs > 0
    assert ac_rate > 0


def test_problem_parse_title(prob):
    assert prob._parse_title(prob.stat) == TEST_Q_TITLE


def test_problem_parse_title_slug(prob):
    assert prob._parse_title_slug(prob.stat) == TEST_Q_TITLE_SLUG


def test_problem_parse_url(prob):
    assert prob._parse_url(prob.stat) == TEST_Q_TITLE_URL


def test_problem_parse_url_solution(prob):
    res = prob._parse_url_solution(prob.stat)
    assert res == TEST_Q_TITLE_URL_SOLUTION


def test_scrape_n_render(prob):
    prob.parse(prob.stat)
    r = prob._scrape_n_render()

    assert r.status_code == 200

def test_scrape_problem_topics(prob):
    prob.parse(prob.stat)
    r = prob._scrape_n_render()
    tags = prob._scrape_problem_topics(r.html)

    assert "Array" in tags
    assert "Hash Table" in tags