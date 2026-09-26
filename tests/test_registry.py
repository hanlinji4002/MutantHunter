"""Tests for mutant_hunter.registry."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from mutant_hunter.registry import (
    REPO_ROOT,
    TARGET_ROOT,
    VENV_PYTHON,
    Module,
    all_modules,
    get_module,
    modules_by_set,
    suite_test_paths,
)


class TestRepoRoot:
    def test_repo_root_is_absolute(self):
        assert REPO_ROOT.is_absolute()

    def test_repo_root_contains_modules_csv(self):
        assert (REPO_ROOT / "dataset" / "modules.csv").exists()

    def test_target_root_derived(self):
        assert TARGET_ROOT == REPO_ROOT / "targets" / "validators"

    def test_venv_python_path(self):
        import os
        if os.name == "nt":
            expected = TARGET_ROOT / ".venv" / "Scripts" / "python.exe"
        else:
            expected = TARGET_ROOT / ".venv" / "bin" / "python"
        assert VENV_PYTHON == expected
        assert VENV_PYTHON.exists(), f"venv python not found at {VENV_PYTHON}"

    def test_repo_root_independent_of_cwd(self, tmp_path, monkeypatch):
        """Repo root must be found regardless of the current working directory."""
        monkeypatch.chdir(tmp_path)
        # Re-import to trigger _repo_root() in a different cwd
        import importlib
        import mutant_hunter.registry as reg
        importlib.reload(reg)
        assert reg.REPO_ROOT.is_absolute()
        assert (reg.REPO_ROOT / "dataset" / "modules.csv").exists()


class TestModuleLoading:
    def test_all_modules_count(self):
        mods = all_modules()
        assert len(mods) == 24

    def test_slugs_correct(self):
        for m in all_modules():
            expected = m.module.replace("/", "__")
            assert m.slug == expected

    def test_source_paths_absolute(self):
        for m in all_modules():
            assert m.source_path.is_absolute()

    def test_test_paths_absolute(self):
        for m in all_modules():
            assert m.test_path.is_absolute()

    def test_ref_mutants_positive(self):
        for m in all_modules():
            assert m.ref_mutants > 0, f"{m.module} has ref_mutants=0"

    def test_url_module(self):
        m = get_module("url")
        assert m.module == "url"
        assert m.slug == "url"
        assert m.set == "main"
        assert m.ref_mutants == 58
        assert m.ref_killed == 35

    def test_i18n_slug(self):
        m = get_module("i18n/fi")
        assert m.slug == "i18n__fi"

    def test_get_module_unknown_raises(self):
        with pytest.raises(KeyError):
            get_module("nonexistent_module_xyz")


class TestModulesBySet:
    def test_main_count(self):
        mods = modules_by_set("main")
        assert len(mods) == 10

    def test_extra_count(self):
        mods = modules_by_set("extra")
        assert len(mods) == 2

    def test_reference_count(self):
        mods = modules_by_set("reference")
        assert len(mods) == 12

    def test_all_count(self):
        mods = modules_by_set("all")
        assert len(mods) == 24

    def test_comma_separated(self):
        mods = modules_by_set("url,uuid")
        assert len(mods) == 2
        assert {m.module for m in mods} == {"url", "uuid"}

    def test_unknown_name_raises(self):
        with pytest.raises(KeyError):
            modules_by_set("nonexistent_xyz")


class TestSuiteTestPaths:
    def test_human_suite(self):
        m = get_module("url")
        paths = suite_test_paths(m, "human")
        assert len(paths) == 1
        assert paths[0].is_absolute()
        assert paths[0].name == "test_url.py"

    def test_human_mh_missing_warns(self, tmp_path):
        """human+mh should warn if mh dir is missing but still return human path."""
        m = get_module("url")
        # Use a tmp target root where the mh sub-directory does not exist
        fake_root = tmp_path / "validators"
        fake_tests = fake_root / "tests"
        fake_test_url = fake_tests / "test_url.py"
        fake_test_url.parent.mkdir(parents=True)
        fake_test_url.write_text("# fake", encoding="utf-8")
        with pytest.warns(UserWarning, match="missing or empty"):
            paths = suite_test_paths(m, "human+mh", target_root=fake_root)
        assert len(paths) == 1  # falls back to human only

    def test_human_b1_missing_warns(self, tmp_path):
        m = get_module("url")
        fake_root = tmp_path / "validators"
        fake_tests = fake_root / "tests"
        fake_test_url = fake_tests / "test_url.py"
        fake_test_url.parent.mkdir(parents=True)
        fake_test_url.write_text("# fake", encoding="utf-8")
        with pytest.warns(UserWarning, match="missing or empty"):
            paths = suite_test_paths(m, "human+b1", target_root=fake_root)
        assert len(paths) == 1

    def test_unknown_suite_raises(self):
        m = get_module("url")
        with pytest.raises(ValueError, match="Unknown suite"):
            suite_test_paths(m, "unknown_suite")

    def test_custom_target_root(self, tmp_path):
        """suite_test_paths should use the provided target_root."""
        m = get_module("url")
        # Construct a fake target root mirroring the real structure
        fake_root = tmp_path / "validators"
        fake_tests = fake_root / "tests"
        fake_tests.mkdir(parents=True)
        fake_test_url = fake_tests / "test_url.py"
        fake_test_url.write_text("# fake", encoding="utf-8")

        paths = suite_test_paths(m, "human", target_root=fake_root)
        assert paths[0] == fake_test_url
