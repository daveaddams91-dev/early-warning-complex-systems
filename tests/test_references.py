import os
import re
import pytest

def test_references_completeness_and_validity():
    ref_path = os.path.join(os.path.dirname(__file__), "..", "REFERENCES.md")
    assert os.path.exists(ref_path), "REFERENCES.md must exist"

    with open(ref_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify no hallucinated/dead DOIs or spliced authors exist
    assert "10.1038/s41598-021-94269-w" not in content, "Dead DOI must not be in REFERENCES.md"
    assert "10.1007/s12080-013-0186-x" not in content, "Dead DOI must not be in REFERENCES.md"
    assert "10.1063/1.4962700" not in content, "Mismatched radar DOI must not be in REFERENCES.md"
    assert "Sloan, C." not in content, "Invented author Sloan, C. must not be in REFERENCES.md"
    assert "Früh, M." not in content, "Invented co-author Früh, M. must not be in REFERENCES.md"
    assert "Zou, H." not in content, "Invented co-author Zou, H. must not be in REFERENCES.md"

    # Verify verified entries are present
    assert "10.1098/rsif.2019.0629" in content, "Weinans et al. 2019 DOI must be present"
    assert "10.1038/s41598-021-87839-y" in content, "Weinans et al. 2021 DOI must be present"
    assert "10.1073/pnas.2106140118" in content, "Bury et al. 2021 DOI must be present"
    assert "Deep learning for early warning signals of tipping points" in content, "Bury et al. 2021 real title must be present"
    assert "10.1063/1.4963012" in content, "Ritchie & Sieber 2016 verified DOI must be present"
    assert "10.1007/s12080-013-0192-6" in content, "Boettiger et al. 2013 verified DOI must be present"
    assert "10.1007/s10236-002-0023-6" in content, "Kleinen et al. 2003 DOI must be present"
    assert "10.1098/rsta.2011.0304" in content, "Lenton et al. 2012 DOI must be present"

    # Verify 24 numbered entries exist
    numbered_entries = re.findall(r'^\d+\.\s+\*\*', content, re.MULTILINE)
    assert len(numbered_entries) == 24, f"Expected exactly 24 numbered references, found {len(numbered_entries)}"
