"""Module for generating pdfs."""

from collections.abc import Sequence, Callable
from dataclasses import dataclass
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from src.product_management.seed.allergens import ALLERGENS


TEXTS = {
    "en": { "title": "Allergen Matrix",
           "footer": "Page ",
    },
    "nl": { "title": "Allergenen Lijst",
           "footer": "Pagina "
    }}


@dataclass
class ItemAllergenView:
    name: str
    allergens: list[str]


class AllergenMatrixPDF(FPDF):
    def set_language(self, language: str) -> None:
        if language not in {"nl", "en"}:
            raise ValueError("language must be 'nl' or 'en'")
        self.language = language
        self.texts = TEXTS[language]

    def get_allergen_labels(self, language: str) -> dict[str, dict[str, str]]:
        language = self.language
        return {
            code: {
            "label": data[language],
            "icon": data["icon"],
            }
            for code, data in ALLERGENS.items()
        }


    # ---------- Page setup ----------
# ---------- Page setup ----------
    def start_new_page(
        self,
        allergen_codes: list[str],
        allergen_labels: dict[str, dict],
        item_col_width: int,
        allergen_col_width: int,
        row_height: int,
        item_label: str,
    ) -> None:
        self.add_page()

        # Title
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, f"{self.texts["title"]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(3)

        # Icon header row
        self.set_font("helvetica", "B", 8)
        self.cell(item_col_width, row_height, "", border=1)

        for code in allergen_codes:
            x = self.get_x()
            y = self.get_y()

            self.cell(allergen_col_width, row_height, "", border=1)

            icon_size = 7
            icon_path = allergen_labels[code]["icon"]

            self.image(
                str(icon_path),
                x + (allergen_col_width - icon_size) / 2,
                y + (row_height - icon_size) / 2,
                w=icon_size,
                h=icon_size,
            )

        self.ln()

        # Label header row
        self.cell(item_col_width, row_height, item_label, border=1)

        for code in allergen_codes:
            label = allergen_labels[code]["label"]
            self.cell(allergen_col_width, row_height, label, border=1, align="C")

        self.ln()

        # Reset font for rows
        self.set_font("helvetica", size=8)

    # ---------- Page break helper ----------
    def check_page_break(
        self,
        next_row_height: int,
        start_page: Callable[[], None],
    ) -> None:
        if self.get_y() + next_row_height > self.h - self.b_margin:
            start_page()

    # ---------- Footer ----------
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"{self.texts["footer"]} {self.page_no()} / {{nb}}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # ---------- Main generator ----------
    def generate_allergen_matrix_pdf(
        self,
        data: Sequence["ItemAllergenView"],
        output_path: str,
        language: str,
        item_label: str,
    ) -> None:
        allergen_labels = self.get_allergen_labels(language)
        allergen_codes = list(allergen_labels.keys())


        # Layout constants
        item_col_width = 30
        allergen_col_width = 18
        row_height = 10

        self.alias_nb_pages()

        # First page
        self.start_new_page(
            allergen_codes,
            allergen_labels,
            item_col_width,
            allergen_col_width,
            row_height,
            item_label,
        )

        fill = False
        for item in data:
            self.check_page_break(
                row_height,
                lambda: self.start_new_page(
                    allergen_codes,
                    allergen_labels,
                    item_col_width,
                    allergen_col_width,
                    row_height,
                    item_label,
                ),
            )

            self.set_fill_color(235, 235, 235 if fill else 255)
            fill = not fill

            self.cell(
                item_col_width,
                row_height,
                item.name,
                border=1,
                fill=True,
            )

            for code in allergen_codes:
                sorted(code)
                if code in item.allergens:
                    self.set_font('ZapfDingbats', '', 12)
                else:
                    self.set_font('helvetica', '', 8)

                mark = "4" if code in item.allergens else ""
                self.cell(
                    allergen_col_width,
                    row_height,
                    mark,
                    border=1,
                    align="C",
                    fill=True,
                )
            self.set_font('helvetica', '', 8)


            self.ln()

        self.output(output_path)