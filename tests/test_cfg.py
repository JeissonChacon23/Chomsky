"""Pruebas: validación, forma de la FNC y equivalencia del lenguaje (RNF07)."""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cfg import Converter, Grammar, build_grammar, check_cnf  # noqa: E402

EXAMPLE = ("S A B", "a b", "S", "S -> A S B | ε\nA -> a A S | a\nB -> S b S | A | b b")


def language(g: Grammar, max_len: int):
    """Cadenas de longitud <= max_len generadas (punto fijo sobre conjuntos de cadenas)."""
    terms = g.terminal_set()
    lang = {v: set() for v in g.variables}
    changed = True
    while changed:
        changed = False
        for lhs, rhs in g.all_productions():
            words = {""}
            for s in rhs:
                options = {s} if s in terms else lang.get(s, set())
                words = {w + o for w in words for o in options if len(w + o) <= max_len}
                if not words:
                    break
            if not words <= lang[lhs]:
                lang[lhs] |= words
                changed = True
    return lang[g.start]


def convert(v, t, s, p):
    g, errors = build_grammar(v, t, s, p)
    assert not errors, errors
    c = Converter(g)
    c.run_all()
    return g, c


class TestValidation(unittest.TestCase):
    def test_errores_de_ejemplo(self):
        _, e = build_grammar("S A", "a", "X", "S -> A D\nA -> c")
        text = "\n".join(e)
        self.assertIn("el símbolo inicial X no pertenece al conjunto de variables", text)
        self.assertIn("la variable D utilizada en la producción S -> A D no fue declarada", text)
        self.assertIn("el símbolo c no fue declarado como terminal", text)

    def test_sin_variables_ni_terminales(self):
        g, e = build_grammar("", "", "", "")
        self.assertIsNone(g)
        self.assertTrue(len(e) >= 3)

    def test_gramatica_valida(self):
        g, e = build_grammar(*EXAMPLE)
        self.assertEqual(e, [])
        self.assertEqual(g.start, "S")


class TestConversion(unittest.TestCase):
    def test_ejemplo_en_fnc(self):
        g, c = convert(*EXAMPLE)
        self.assertEqual(check_cnf(c.current), [])
        self.assertEqual(c.history[-1].status, "ok")

    def test_lenguaje_conservado(self):
        g, c = convert(*EXAMPLE)
        self.assertEqual(language(g, 6), language(c.current, 6))
        self.assertIn("", language(c.current, 6))

    def test_determinista(self):
        _, c1 = convert(*EXAMPLE)
        _, c2 = convert(*EXAMPLE)
        self.assertEqual(c1.current.lines(), c2.current.lines())

    def test_sin_inicial_en_derecha_conserva_epsilon(self):
        g, c = convert("S A", "a", "S", "S -> A A | ε\nA -> a | ε")
        self.assertEqual(check_cnf(c.current), [])
        self.assertEqual(language(g, 4), language(c.current, 4))

    def test_variables_inutiles_e_inalcanzables(self):
        g, c = convert("S A B C", "a b", "S", "S -> a A | b\nA -> a\nB -> b B\nC -> a")
        self.assertNotIn("B", c.current.variables)
        self.assertNotIn("C", c.current.variables)
        self.assertEqual(language(g, 5), language(c.current, 5))

    def test_nombres_auxiliares_no_chocan(self):
        g, c = convert("S X1", "a", "S", "S -> a a a X1\nX1 -> a")
        self.assertEqual(check_cnf(c.current), [])
        self.assertEqual(len(c.current.variables), len(set(c.current.variables)))

    def test_lenguaje_vacio(self):
        g, c = convert("S A", "a", "S", "S -> A\nA -> A a")
        self.assertEqual(language(c.current, 5), set())

    def test_gramaticas_aleatorias(self):
        rnd = random.Random(7)
        vs, ts = ["S", "A", "B", "C"], ["a", "b"]
        for _ in range(300):
            lines = []
            for v in vs:
                alts = []
                for _ in range(rnd.randint(1, 3)):
                    n = rnd.choice([0, 1, 1, 2, 3, 4])
                    alts.append(" ".join(rnd.choice(vs + ts) for _ in range(n)) or "ε")
                lines.append(f"{v} -> " + " | ".join(alts))
            g, errors = build_grammar(" ".join(vs), " ".join(ts), "S", "\n".join(lines))
            self.assertEqual(errors, [])
            c = Converter(g)
            c.run_all()
            self.assertEqual(check_cnf(c.current), [], "\n".join(lines))
            self.assertEqual(language(g, 5), language(c.current, 5), "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
