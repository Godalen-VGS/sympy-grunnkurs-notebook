"""Automatisk retting av 14-sympy-grunnkurs.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1a', 'svar_1a skal være (2x - 3)² multiplisert ut', "svar_1a == S('4*x**2 - 12*x + 9')"),
    ('1b', 'svar_1b skal være x² - 5x + 6 faktorisert', "svar_1b == S('(x - 2)*(x - 3)')"),
    ('1c', 'svar_1c skal være (x² - 9)/(x + 3) forenklet', "svar_1c == S('x - 3')"),
    ('1d', 'svar_1d skal være den eksakte verdien (en brøk) av x³ - 2x for x = 1/2', "svar_1d == S('-7/8')"),
    ('2a', 'losning_2a skal være løsningene av x² - 2x - 15 = 0', 'lik(losning_2a, [-3, 5])'),
    ('2b', 'losning_2b skal være løsningene av 3/x + 1 = x/2', "lik(losning_2b, [S('1 - sqrt(7)'), S('1 + sqrt(7)')])"),
    ('2c', 'losning_2c skal være løsningene av x³ - 6x² + 11x - 6 = 0', 'lik(losning_2c, [1, 2, 3])'),
    ('3', 'losning_3 skal være løsningen av likningssettet i oppgave 3', "lik(losning_3, {'x': 3, 'y': 2})"),
    ('4_to', 'los_andregrad(1, -5, 6) skal gi [2, 3]', 'lik(los_andregrad(1, -5, 6), [2, 3])'),
    ('4_en', 'los_andregrad(1, -4, 4) skal gi [2]', 'lik(los_andregrad(1, -4, 4), [2])'),
    ('4_ingen', 'los_andregrad(1, 2, 5) skal gi [] (ingen reelle løsninger)', 'los_andregrad(1, 2, 5) == []'),
    ('4_eksakt', 'los_andregrad(2, 0, -1) skal gi de eksakte løsningene ±√2/2', "lik(los_andregrad(2, 0, -1), [S('-sqrt(2)/2'), S('sqrt(2)/2')])"),
    ('5', 'voksen og barn skal være prisene på billettene', 'lik(voksen, 160) and lik(barn, 100)'),
    ('6', 'losning_6 skal være skjæringspunktene mellom sirkelen og linjen', 'lik(losning_6, [(3, 4), (-4, -3)])'),
    ('7', 'k_verdier skal være verdiene av k som gir nøyaktig én løsning', 'lik(k_verdier, [-6, 6])'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
