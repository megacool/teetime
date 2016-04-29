from teetime import layout as uut


def test_verb_noun_same():
    assert uut('big booty big brain') == ['big booty', 'big brain']


def test_veggies():
    assert uut('eat your veggies') == ['eat your', 'veggies']


def test_conjunction_not_on_single_line():
    text = 'You are an intimidating strong arty woman and I am a fragile baby plant'
    layout = [
        'You are an intimidating',
        'strong',
        'arty woman',
        'and I am a',
        'fragile baby',
        'plant'
    ]
    assert uut(text) == layout
