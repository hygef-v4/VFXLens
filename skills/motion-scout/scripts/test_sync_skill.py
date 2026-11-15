import os
import tempfile
import unittest
from pathlib import Path

from sync_skill import synchronize


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="motion-scout-link-test-")
        self.root = Path(self.temp.name).resolve()
        (self.root / "AGENTS.md").write_text("test", encoding="utf-8")
        (self.root / "studio").mkdir()
        (self.root / "studio/package.json").write_text("{}", encoding="utf-8")
        self.source = self.root / "skills/motion-scout"
        self.sources = {"motion-scout": self.source}
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("---\nname: motion-scout\ndescription: test\n---\n", encoding="utf-8")

    def tearDown(self):
        for name, source in self.sources.items():
            for parent in (".agents", ".claude"):
                path = self.root / parent / "skills" / name
                if path != source and os.path.lexists(path) and path.resolve() == source:
                    if os.name == "nt":
                        os.rmdir(path)  # Remove the verified junction itself, never its target.
                    else:
                        path.unlink()
        self.temp.cleanup()

    def test_check_is_read_only(self):
        self.assertFalse(synchronize(self.root, check=True)["ok"])
        self.assertFalse((self.root / ".agents").exists())
        self.assertFalse((self.root / ".claude").exists())

    def test_shared_content_and_repeat_setup(self):
        self.assertTrue(synchronize(self.root)["ok"])
        self.assertTrue(synchronize(self.root)["ok"])
        content = "---\nname: motion-scout\ndescription: changed\n---\n"
        (self.source / "SKILL.md").write_text(content, encoding="utf-8")
        for parent in (".agents", ".claude"):
            self.assertEqual((self.root / parent / "skills/motion-scout/SKILL.md").read_text(encoding="utf-8"), content)
        self.assertTrue(synchronize(self.root, check=True)["ok"])

    def test_conflict_preserves_existing_and_creates_nothing(self):
        other = self.root / ".claude/skills/motion-scout"
        other.mkdir(parents=True)
        (other / "keep.txt").write_text("other agent", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "left untouched"):
            synchronize(self.root)
        self.assertEqual((other / "keep.txt").read_text(encoding="utf-8"), "other agent")
        self.assertFalse((self.root / ".agents").exists())

    def test_director_keeps_canonical_codex_source_and_links_claude(self):
        source = self.root / ".agents/skills/remotion-3d-director"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("---\nname: remotion-3d-director\ndescription: test\n---\n", encoding="utf-8")
        self.sources["remotion-3d-director"] = source
        result = synchronize(self.root, skill="remotion-3d-director")
        self.assertTrue(result["ok"])
        self.assertFalse(result["clients"][0]["created"])
        self.assertEqual((self.root / ".claude/skills/remotion-3d-director").resolve(), source)

    def test_vfxlens_is_shared_by_both_project_clients(self):
        source = self.root / "skills/vfxlens"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("---\nname: vfxlens\ndescription: test\n---\n", encoding="utf-8")
        self.sources["vfxlens"] = source
        self.assertTrue(synchronize(self.root, skill="vfxlens")["ok"])
        self.assertTrue(synchronize(self.root, check=True, skill="vfxlens")["ok"])


if __name__ == "__main__":
    unittest.main()
