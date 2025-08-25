from typing import List


def enumerate_terms(terms: List[str], language: str = "de", max_terms: int = -1) -> str:
    if max_terms >= 0:
        terms = terms[:max_terms]
    match language:
        case "en":
            and_ = "and"
            as_well_as = "as well as"

        case _:
            and_ = "und"
            as_well_as = "sowie"

    match len(terms):
        case 0:
            return ""

        case 1:
            return terms[0]

        case 2:
            return f"{terms[0]} {and_} {terms[1]}"

        case 3:
            return f"{terms[0]} {and_} {terms[1]} {as_well_as} {terms[2]}"

        case 4:
            return f"{terms[0]} {and_} {terms[1]} {as_well_as} {terms[2]} {and_} {terms[3]}"

        case _:
            return f"{', '.join(t for t in terms[:-1])} {and_} {terms[-1]}"


def format_value(value: float, decimal_places: int = 1) -> str:
    return f"{value:.{decimal_places}f}".replace(".", ",")


def from_str(string: str) -> float:
    return float(string.replace(",", "."))
