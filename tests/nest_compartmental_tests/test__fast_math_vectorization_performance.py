# -*- coding: utf-8 -*-
#
# test__fast_math_vectorization_performance.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""
Optional diagnostic benchmark for compartmental vectorization performance.

This test is intended for users who expect the compartmental code generator's
vectorized mechanism loops to improve performance, but do not see the expected
speedup in their local build or model setup. It generates comparable
``cm_default`` variants with different fast-math settings, patches the generated
CMake files to request compiler vectorization reports, rebuilds the modules, and
measures simulation time per compartment across a small compartment-count sweep.

Run it explicitly with ``NESTML_RUN_PERFORMANCE_TESTS=1``. The generated report,
plots, build logs, and compiler vectorization diagnostics are written under
``tests/nest_compartmental_tests/target/fast_math_vectorization_performance`` and
can be used to identify which generated loops were vectorized and which compiler
diagnostics explain missed vectorization.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import time
from collections import Counter

import numpy as np
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target


pytestmark = pytest.mark.skipif(
    os.environ.get("NESTML_RUN_PERFORMANCE_TESTS") != "1",
    reason="Compartmental fast-math benchmark is hardware and compiler dependent.",
)


ARTIFACT_ROOT = Path(__file__).resolve().parent / "target" / "fast_math_vectorization_performance"
COMPARTMENT_COUNTS = [1, 2, 4, 8, 16, 32, 64, 128]
SIM_TIME_MS = 1000.0
MIN_WALL_TIME_S = 1.0
MAX_REPEATS = 20
MAX_VECTOR_MISS_REPORT_ENTRIES = 20

SOMA_PARAMS = {
    "C_m": 89.245535,
    "g_C": 0.0,
    "g_L": 8.924572508,
    "e_L": -75.0,
    "v_comp": -75.0,
    "gbar_Na": 4608.698576715,
    "e_Na": 60.0,
    "gbar_K": 956.112772900,
    "e_K": -90.0,
}
DEND_PARAMS = {
    "C_m": 1.929929,
    "g_C": 1.255439494,
    "g_L": 0.192992878,
    "e_L": -75.0,
    "v_comp": -75.0,
    "gbar_Na": 17.203212493,
    "e_Na": 60.0,
    "gbar_K": 11.887347450,
    "e_K": -90.0,
}


def _nest_prefix(nest):
    if hasattr(nest, "build_info"):
        return nest.build_info["prefix"]
    return nest.ll_api.sli_func("statusdict/prefix ::")


def _run_command(command, cwd, log_path):
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("$ " + " ".join(command) + "\n")
        f.write(completed.stdout)
        f.write("\n")

    if completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, command, output=completed.stdout)


def _patch_cmake_with_vectorization_report(cmake_path):
    report_dir = cmake_path.parent / "vectorization_report"
    injection = f"""
set( CM_VECTORIZATION_REPORT_DIR "{report_dir}" )
file( MAKE_DIRECTORY "${{CM_VECTORIZATION_REPORT_DIR}}" )
if ( CMAKE_CXX_COMPILER_ID MATCHES "GNU" )
    set( CM_EXTRA_COMPILE_FLAGS "${{CM_EXTRA_COMPILE_FLAGS}} -fopt-info-vec-all=${{CM_VECTORIZATION_REPORT_DIR}}/all.log" )
elseif ( CMAKE_CXX_COMPILER_ID MATCHES "Clang" )
    set( CM_EXTRA_COMPILE_FLAGS "${{CM_EXTRA_COMPILE_FLAGS}} -Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize" )
endif ()
"""

    marker = "set( CM_EXTRA_COMPILE_FLAGS \"\" )"
    content = cmake_path.read_text(encoding="utf-8")
    if "CM_VECTORIZATION_REPORT_DIR" in content:
        return

    if marker not in content:
        raise AssertionError(f"Cannot find compile flags marker in {cmake_path}")

    cmake_path.write_text(content.replace(marker, marker + injection, 1), encoding="utf-8")


def _build_with_vectorization_report(case, nest):
    cmake_path = case["target_path"] / "CMakeLists.txt"
    _patch_cmake_with_vectorization_report(cmake_path)

    report_dir = case["target_path"] / "vectorization_report"
    report_dir.mkdir(exist_ok=True)
    for report_path in report_dir.glob("*.log"):
        report_path.unlink()

    build_log = case["target_path"] / "vectorization_build.log"
    build_log.write_text("", encoding="utf-8")

    _run_command(
        [
            "cmake",
            "-Dwith-nest=" + str(Path(_nest_prefix(nest)) / "bin" / "nest-config"),
            "-DCMAKE_INSTALL_PREFIX=" + str(case["install_path"]),
            ".",
        ],
        case["target_path"],
        build_log,
    )
    _run_command(["make", "clean"], case["target_path"], build_log)
    _run_command(["make", "-j1", "all"], case["target_path"], build_log)
    _run_command(["make", "install"], case["target_path"], build_log)


def _read_text_if_exists(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _count_vectorization_messages(case):
    report_dir = case["target_path"] / "vectorization_report"
    report_text = _read_text_if_exists(report_dir / "all.log")
    build_text = _read_text_if_exists(case["target_path"] / "vectorization_build.log")

    report_lines = report_text.splitlines()
    clang_remark_lines = [
        line
        for line in build_text.splitlines()
        if "loop-vectorize" in line and "remark:" in line
    ]

    vectorization_lines = report_lines + clang_remark_lines
    generated_lines = [line for line in vectorization_lines if str(case["target_path"]) in line]

    optimized_count = sum(
        1
        for line in vectorization_lines
        if re.search(r"optimized:.*vectorized|remark:.*vectorized", line, re.IGNORECASE)
    )
    missed_count = sum(
        1
        for line in vectorization_lines
        if re.search(r"missed:|not vectorized", line, re.IGNORECASE)
    )
    optimized_generated_count = sum(
        1
        for line in generated_lines
        if re.search(r"optimized:.*vectorized|remark:.*vectorized", line, re.IGNORECASE)
    )
    missed_generated_count = sum(
        1
        for line in generated_lines
        if re.search(r"missed:|not vectorized", line, re.IGNORECASE)
    )

    return {
        "optimized_count": optimized_count,
        "missed_count": missed_count,
        "optimized_generated_count": optimized_generated_count,
        "missed_generated_count": missed_generated_count,
        "gcc_report": str(report_dir / "all.log"),
        "build_log": str(case["target_path"] / "vectorization_build.log"),
    }


def _normalize_generated_name(text):
    text = re.sub(r"(None|SoftFast|Fast)MathVectorizationNestml", "VectorizationNestml", text)
    text = re.sub(r"_(none|soft_fast|fast)_math_vectorization_nestml", "_vectorization_nestml", text)
    return text


def _source_function_name(source_cache, source_path, line_number):
    source_path = Path(source_path)
    if source_path not in source_cache:
        source_cache[source_path] = source_path.read_text(encoding="utf-8", errors="replace").splitlines()

    source_lines = source_cache[source_path]
    start_index = min(line_number - 1, len(source_lines) - 1)
    for index in range(start_index, max(start_index - 120, -1), -1):
        line = source_lines[index].strip()
        if "nest::" not in line or "::" not in line or "(" not in line:
            continue

        signature_parts = [line]
        for following_line in source_lines[index + 1:min(index + 8, len(source_lines))]:
            stripped = following_line.strip()
            if stripped == "{":
                break
            signature_parts.append(stripped)
            if "{" in stripped:
                break

        signature = " ".join(signature_parts)
        signature = signature.split("{", 1)[0].strip()
        signature = re.sub(r"\s+", " ", signature)
        return _normalize_generated_name(signature)

    return "<unknown generated function>"


def _miss_reason(message):
    message = _normalize_generated_name(message)
    if "couldn't vectorize loop" in message:
        return "could not vectorize loop"
    if "control flow in loop" in message:
        return "control flow in loop"
    if "statement clobbers memory" in message:
        function_match = re.search(r"\b([A-Za-z_][\w:]*)\s*\(", message)
        if function_match:
            return "memory-clobbering call: " + function_match.group(1)
        return "statement clobbers memory"
    if "no vectype for stmt" in message:
        return "no vector type for statement"
    if "unsupported" in message:
        return message.split(":", 1)[0]
    return message.split(":", 1)[0]


def _missed_vectorization_summary(case):
    report_dir = case["target_path"] / "vectorization_report"
    report_text = _read_text_if_exists(report_dir / "all.log")
    build_text = _read_text_if_exists(case["target_path"] / "vectorization_build.log")
    source_cache = {}
    misses = Counter()

    diagnostic_lines = report_text.splitlines() + [
        line
        for line in build_text.splitlines()
        if "loop-vectorize" in line and "remark:" in line
    ]

    for line in diagnostic_lines:
        generated_path_start = line.find(str(case["target_path"]))
        if generated_path_start < 0:
            continue
        line = line[generated_path_start:]
        if not re.search(r"missed:|not vectorized", line, re.IGNORECASE):
            continue

        match = re.match(r"(?P<file>.*?):(?P<line>\d+):(?P<column>\d+):\s*(?:missed|remark):\s*(?P<message>.*)", line)
        if not match:
            continue

        source_path = Path(match.group("file"))
        if source_path.suffix != ".cpp":
            continue

        line_number = int(match.group("line"))
        function_name = _source_function_name(source_cache, source_path, line_number)
        reason = _miss_reason(match.group("message"))
        misses[(function_name, reason)] += 1

    by_function = {}
    for (function_name, reason), count in misses.items():
        by_function.setdefault(function_name, Counter())[reason] += count

    return {
        function_name: dict(reasons)
        for function_name, reasons in sorted(by_function.items())
    }


def _write_vectorization_comparison_report(results, output_path):
    lines = [
        "# Fast-Math Vectorization Comparison",
        "",
        "Generated-source missed-vectorization diagnostics that occur more often in each mode than in `fast` mode.",
        "",
        "| mode | compiler flags | optimized generated | missed generated |",
        "| --- | --- | ---: | ---: |",
    ]

    for case_name, case_result in results["cases"].items():
        vectorization = case_result["vectorization"]
        flags = case_result["compile_flags"]
        lines.append(
            f"| `{case_name}` | `{flags or '<none>'}` | "
            f"{vectorization['optimized_generated_count']} | {vectorization['missed_generated_count']} |"
        )

    baseline_summary = results["cases"]["fast"]["vectorization"]["missed_generated_by_function"]
    for case_name, case_result in results["cases"].items():
        if case_name == "fast":
            continue

        comparison_summary = case_result["vectorization"]["missed_generated_by_function"]
        rows = []
        function_names = sorted(set(baseline_summary) | set(comparison_summary))
        for function_name in function_names:
            baseline_reasons = baseline_summary.get(function_name, {})
            comparison_reasons = comparison_summary.get(function_name, {})
            reasons = sorted(set(baseline_reasons) | set(comparison_reasons))
            extra_reasons = []
            extra_count = 0
            for reason in reasons:
                difference = comparison_reasons.get(reason, 0) - baseline_reasons.get(reason, 0)
                if difference > 0:
                    extra_count += difference
                    extra_reasons.append(f"{reason} (+{difference})")

            if extra_count > 0:
                rows.append((extra_count, function_name, extra_reasons))

        rows.sort(reverse=True)

        lines.extend([
            "",
            f"## `{case_name}` Compared To `fast`",
            "",
            "| extra misses | function | reasons |",
            "| ---: | --- | --- |",
        ])

        for extra_count, function_name, extra_reasons in rows[:MAX_VECTOR_MISS_REPORT_ENTRIES]:
            lines.append(f"| {extra_count} | `{function_name}` | {'; '.join(extra_reasons)} |")

        if len(rows) > MAX_VECTOR_MISS_REPORT_ENTRIES:
            lines.append("")
            lines.append(f"Only the top {MAX_VECTOR_MISS_REPORT_ENTRIES} function/reason groups are shown.")

        if not rows:
            lines.append(f"| 0 | none | `{case_name}` had no generated functions with additional misses versus `fast` |")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _compartments(n_compartments):
    compartments = [{"parent_idx": -1, "params": dict(SOMA_PARAMS)}]
    for idx in range(1, n_compartments):
        compartments.append({"parent_idx": idx - 1, "params": dict(DEND_PARAMS)})
    return compartments


def _time_simulation(case, n_compartments, nest):
    nest.ResetKernel()
    nest.SetKernelStatus({"resolution": 0.1, "local_num_threads": 1})
    nest.Install(case["module_path"])

    neuron = nest.Create(case["model_name"])
    neuron.compartments = _compartments(n_compartments)
    neuron.V_th = -50.0

    nest.Simulate(10.0)

    elapsed_times = []
    total_elapsed = 0.0
    while total_elapsed < MIN_WALL_TIME_S and len(elapsed_times) < MAX_REPEATS:
        start = time.perf_counter()
        nest.Simulate(SIM_TIME_MS)
        elapsed = time.perf_counter() - start
        elapsed_times.append(elapsed)
        total_elapsed += elapsed

    median_elapsed = float(np.median(elapsed_times))
    return {
        "compartments": n_compartments,
        "elapsed_times_s": elapsed_times,
        "median_elapsed_s": median_elapsed,
        "time_per_compartment_s": median_elapsed / n_compartments,
    }


def _write_plot(results, output_path):
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for case_name, case_result in results["cases"].items():
        timings = case_result["timings"]
        ax.plot(
            [entry["compartments"] for entry in timings],
            [entry["time_per_compartment_s"] for entry in timings],
            marker="o",
            label=case_name,
        )

    ax.set_xscale("log", base=2)
    ax.set_xlabel("compartments")
    ax.set_ylabel("time per compartment [s]")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


class TestFastMathVectorizationPerformance:
    CASES = {
        "none": {
            "module_name": "cm_none_math_vectorization_module",
            "suffix": "_none_math_vectorization_nestml",
            "model_name": "cm_default_none_math_vectorization_nestml",
            "codegen_opts": {"use_fast_math": "None"},
            "compile_flags": "",
        },
        "soft_fast": {
            "module_name": "cm_soft_fast_math_vectorization_module",
            "suffix": "_soft_fast_math_vectorization_nestml",
            "model_name": "cm_default_soft_fast_math_vectorization_nestml",
            "codegen_opts": {"use_fast_math": "soft-fast"},
            "compile_flags": "-fno-math-errno -fno-trapping-math",
        },
        "fast": {
            "module_name": "cm_fast_math_vectorization_module",
            "suffix": "_fast_math_vectorization_nestml",
            "model_name": "cm_default_fast_math_vectorization_nestml",
            "codegen_opts": {"use_fast_math": "fast"},
            "compile_flags": "-ffast-math",
        },
    }

    @pytest.fixture(scope="class", autouse=True)
    def setup_models(self, request):
        nest = pytest.importorskip("nest")

        tests_path = Path(__file__).resolve().parent
        input_path = tests_path / "resources" / "cm_default.nestml"

        for case_name, case in self.CASES.items():
            target_path = ARTIFACT_ROOT / case_name
            install_path = target_path / "install"
            target_path.mkdir(parents=True, exist_ok=True)
            install_path.mkdir(parents=True, exist_ok=True)

            generate_nest_compartmental_target(
                input_path=str(input_path),
                target_path=str(target_path),
                install_path=str(install_path),
                module_name=case["module_name"],
                suffix=case["suffix"],
                logging_level="WARNING",
                codegen_opts=case["codegen_opts"],
            )

            case["target_path"] = target_path
            case["install_path"] = install_path
            case["module_path"] = str(install_path / (case["module_name"] + ".so"))

            cmake_text = (target_path / "CMakeLists.txt").read_text(encoding="utf-8")
            assert ("-ffast-math" in cmake_text) is (case["codegen_opts"]["use_fast_math"] == "fast")
            assert ("-fno-math-errno" in cmake_text) is (case["codegen_opts"]["use_fast_math"] == "soft-fast")
            assert ("-fno-trapping-math" in cmake_text) is (case["codegen_opts"]["use_fast_math"] == "soft-fast")

            _build_with_vectorization_report(case, nest)

        request.cls.CASES = self.CASES
        request.cls.nest = nest

    def test_fast_math_vectorization_and_performance(self):
        results = {
            "sim_time_ms": SIM_TIME_MS,
            "min_wall_time_s": MIN_WALL_TIME_S,
            "max_repeats": MAX_REPEATS,
            "compartment_counts": COMPARTMENT_COUNTS,
            "cases": {},
        }

        for case_name, case in self.CASES.items():
            vectorization = _count_vectorization_messages(case)
            vectorization["missed_generated_by_function"] = _missed_vectorization_summary(case)
            timings = [_time_simulation(case, n_compartments, self.nest) for n_compartments in COMPARTMENT_COUNTS]

            results["cases"][case_name] = {
                "module_name": case["module_name"],
                "model_name": case["model_name"],
                "use_fast_math": case["codegen_opts"]["use_fast_math"],
                "compile_flags": case["compile_flags"],
                "vectorization": vectorization,
                "timings": timings,
            }

            assert vectorization["optimized_count"] + vectorization["missed_count"] > 0
            assert vectorization["optimized_generated_count"] + vectorization["missed_generated_count"] > 0
            assert all(np.isfinite(entry["time_per_compartment_s"]) for entry in timings)
            assert all(entry["time_per_compartment_s"] > 0.0 for entry in timings)

        ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
        results_path = ARTIFACT_ROOT / "fast_math_vectorization_performance.json"
        plot_path = ARTIFACT_ROOT / "fast_math_vectorization_performance.png"
        report_path = ARTIFACT_ROOT / "fast_math_vectorization_comparison.md"

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        _write_plot(results, plot_path)
        _write_vectorization_comparison_report(results, report_path)

        assert results_path.exists()
        assert plot_path.exists()
        assert report_path.exists()
