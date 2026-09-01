"""The evaluation harness. Deliberately outside `src/`.

This is the only code permitted to read the ground-truth file, and it runs after
the pipeline has already decided. Keeping it out of the package is what makes
`tests/test_truth_isolation.py` a real guarantee rather than a convention: the
assessment path physically cannot import from here, because here is not part of
the installed package at all.
"""
