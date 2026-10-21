"""El .exe solo incluye los módulos que se importan de forma visible desde main.py: si uno se carga por
nombre (importlib), PyInstaller lo deja fuera y la app falla solo en la versión compilada."""
import modulefinder
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_todos_los_modulos_se_alcanzan_desde_main():
    finder = modulefinder.ModuleFinder(path=[str(ROOT)], excludes=["numpy", "PIL", "zxingcpp", "pystray",
                                                                     "tkinter", "winreg"])
    finder.run_script(str(ROOT / "main.py"))
    found = set(finder.modules)
    expected = {".".join(p.relative_to(ROOT).with_suffix("").parts).removesuffix(".__init__")
                for p in (ROOT / "clipqr").rglob("*.py")}
    expected -= {"clipqr.__main__"}  # solo para «py -m clipqr»
    missing = sorted(expected - found)
    assert not missing, f"Módulos que el .exe no incluiría: {missing}"


def test_sin_imports_por_nombre():
    offenders = [str(p.relative_to(ROOT)) for p in (ROOT / "clipqr").rglob("*.py")
                 if "import_module(" in p.read_text(encoding="utf-8") or "__import__(" in p.read_text(encoding="utf-8")]
    assert not offenders, offenders
