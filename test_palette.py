import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from scripts.palette import SVG, recolor

class PaletteTest(unittest.TestCase):
    def setUp(self):
        self.root=ET.parse(Path(__file__).parent/"examples/sample.svg").getroot()

    def test_marker_is_private(self):
        report=recolor(self.root,{"messages":[{"label":"Accept changes","color":"#112233"}]})
        unchanged,changed=self.root.findall(SVG+"line")
        self.assertEqual(report["messages"],1)
        self.assertEqual(unchanged.get("marker-end"),"url(#tip)")
        self.assertNotEqual(changed.get("marker-end"),unchanged.get("marker-end"))
        self.assertIsNone(self.root.find(".//*[@id='tip']")[0].get("style"))
        self.assertEqual(len(self.root.findall(".//"+SVG+"marker")),2)

    def test_duplicate_label_requires_occurrence(self):
        labels=self.root.findall(SVG+"text")
        labels[1].text=labels[0].text
        with self.assertRaises(ValueError):
            recolor(self.root,{"messages":[{"label":"Send draft","color":"#112233"}]})
        self.assertEqual(recolor(self.root,{"messages":[{"label":"Send draft","occurrence":2,"color":"#112233"}]})["messages"],1)
