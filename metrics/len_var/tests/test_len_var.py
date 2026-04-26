from metrics.len_var.scorer import score

def test_constant_length():
    s = "word " * 10
    assert score(s) < 0.05

def test_varied_length():
    s = "a a a a a " + "this sentence is considerably longer "
    assert score(s) > 0.2
