"""Sprint 303: report-pack PDF source validation and integrity.""" 
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from reportlab.pdfgen import canvas

from reports.professional_report_pack import ProfessionalReportPackPDFReport, REPORT_ORDER


def _pdf(path: Path, text: str = "valid report") -> None:
    document = canvas.Canvas(str(path))
    document.drawString(72, 720, text)
    document.save()


def _suite(directory: Path) -> dict[str, Path]:
    sources = {}
    for key in REPORT_ORDER:
        path = directory / f"{key}.pdf"
        _pdf(path, key)
        sources[key] = path
    return sources


class Sprint303ReportPackSourceIntegrityTests(unittest.TestCase):
    def test_valid_sources_compose_into_pack_and_source_bytes_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = _suite(root)
            originals = {key: path.read_bytes() for key, path in sources.items()}
            output = root / "pack.pdf"
            result = ProfessionalReportPackPDFReport().create(sources, output)
            self.assertEqual(result, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 0)
            self.assertEqual({key: path.read_bytes() for key, path in sources.items()}, originals)

    def test_empty_pdf_source_rejected_and_existing_pack_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = _suite(root)
            sources["health_check"].write_bytes(b"")
            output = root / "pack.pdf"
            output.write_bytes(b"previous pack")
            with self.assertRaisesRegex(ValueError, "empty"):
                ProfessionalReportPackPDFReport().create(sources, output, overwrite=True)
            self.assertEqual(output.read_bytes(), b"previous pack")
            self.assertFalse((root / ".pack.pdf.tmp").exists())

    def test_non_pdf_content_rejected_and_existing_pack_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = _suite(root)
            sources["recommendation"].write_text("not a pdf", encoding="utf-8")
            output = root / "pack.pdf"
            output.write_bytes(b"previous pack")
            with self.assertRaisesRegex(ValueError, "invalid or unreadable"):
                ProfessionalReportPackPDFReport().create(sources, output, overwrite=True)
            self.assertEqual(output.read_bytes(), b"previous pack")
            self.assertFalse((root / ".pack.pdf.tmp").exists())

    def test_truncated_pdf_rejected_and_existing_pack_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = _suite(root)
            good = sources["scenario_projection"].read_bytes()
            sources["scenario_projection"].write_bytes(good[:80])
            output = root / "pack.pdf"
            output.write_bytes(b"previous pack")
            with self.assertRaises(ValueError):
                ProfessionalReportPackPDFReport().create(sources, output, overwrite=True)
            self.assertEqual(output.read_bytes(), b"previous pack")
            self.assertFalse((root / ".pack.pdf.tmp").exists())


if __name__ == "__main__":
    unittest.main()
