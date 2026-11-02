import pytest
from pydantic import ValidationError

from lazarus_sentinel.models import Graph, Node, stable_id


def test_ids_and_strict_envelopes():
    assert stable_id("node", "a", 1) == stable_id("node", "a", 1)
    assert stable_id("node", "a", 1) != stable_id("node", "a", 2)
    with pytest.raises(ValidationError):
        Node(id="n", type="FUNCTION", layer="CODE", name="f", unexpected=True)
    assert Graph(repository={"revision": "r", "root_label": "fixture"}).schema_version == "0.1.0"
