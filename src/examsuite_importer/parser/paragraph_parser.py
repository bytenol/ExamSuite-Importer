from __future__ import annotations

from xml.etree import ElementTree

from docx.text.paragraph import Paragraph
from omml2latex import convert_omml


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

W_R = f"{{{WORD_NS}}}r"
W_T = f"{{{WORD_NS}}}t"
W_TAB = f"{{{WORD_NS}}}tab"
W_BR = f"{{{WORD_NS}}}br"
W_CR = f"{{{WORD_NS}}}cr"
W_NO_BREAK_HYPHEN = f"{{{WORD_NS}}}noBreakHyphen"

W_RPR = f"{{{WORD_NS}}}rPr"
W_B = f"{{{WORD_NS}}}b"
W_I = f"{{{WORD_NS}}}i"
W_U = f"{{{WORD_NS}}}u"
W_VERT_ALIGN = f"{{{WORD_NS}}}vertAlign"

W_VAL = f"{{{WORD_NS}}}val"

M_OMATH = f"{{{MATH_NS}}}oMath"
M_OMATH_PARA = f"{{{MATH_NS}}}oMathPara"


class ParagraphParser:
    """
    Converts a python-docx Paragraph into a string while preserving
    semantic formatting and equations.
    """

    def __init__(self, paragraph: Paragraph):
        self.paragraph = paragraph

    def parse(self) -> str:
        parts: list[str] = []

        for node in self.paragraph._p:
            parts.append(self._parse_node(node))

        return "".join(parts)

    def _parse_node(self, node) -> str:
        tag = node.tag

        if tag == W_R:
            return self._parse_run(node)

        if tag == M_OMATH:
            return self._parse_equation(node)

        if tag == M_OMATH_PARA:
            return self._parse_equation(node)

        return "".join(
            self._parse_node(child)
            for child in node
        )

    def _parse_run(self, run) -> str:
        text_parts: list[str] = []

        for child in run:
            if child.tag == W_RPR:
                continue

            if child.tag == W_T:
                text_parts.append(child.text or "")

            elif child.tag == W_TAB:
                text_parts.append("\t")

            elif child.tag in (W_BR, W_CR):
                text_parts.append("\n")

            elif child.tag == W_NO_BREAK_HYPHEN:
                text_parts.append("\u2011")

        text = "".join(text_parts)

        if not text:
            return ""

        return self._apply_formatting(run, text)

    def _apply_formatting(self, run, text: str) -> str:
        rpr = run.find(W_RPR)

        if rpr is None:
            return text

        if self._is_enabled(rpr.find(W_B)):
            text = f"<strong>{text}</strong>"

        if self._is_enabled(rpr.find(W_I)):
            text = f"<em>{text}</em>"

        underline = rpr.find(W_U)

        if underline is not None:
            value = underline.get(W_VAL)

            if value != "none":
                text = f"<u>{text}</u>"

        vert_align = rpr.find(W_VERT_ALIGN)

        if vert_align is not None:
            value = vert_align.get(W_VAL)

            if value == "superscript":
                text = f"<sup>{text}</sup>"

            elif value == "subscript":
                text = f"<sub>{text}</sub>"

        return text

    @staticmethod
    def _is_enabled(element) -> bool:
        if element is None:
            return False

        value = element.get(W_VAL)

        if value is None:
            return True

        return value.lower() not in {
            "false",
            "0",
            "off",
            "no",
        }

    @staticmethod
    def _parse_equation(node) -> str:
        try:
            element = ElementTree.fromstring(
                ElementTree.tostring(node)
            )

            return convert_omml(element)

        except Exception as exc:
            raise RuntimeError(
                f"Unable to convert Word equation: {exc}"
            ) from exc

    def get_text(self) -> str:
        return self.parse()
