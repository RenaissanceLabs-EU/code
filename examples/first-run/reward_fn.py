"""Execution reward for GRPO (EXPERIMENTAL). Stdlib only.

Runs the model's code plus assert-style tests in a subprocess with a wall-clock timeout, a process-group
kill and (on Linux) rlimits. This is NOT a security sandbox: run the whole training job in a container with
no network and no secrets (see the Docker command in data/snippets.json, docker-hardened-sandbox).
"""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import uuid

try:
    import resource  # POSIX only
except ImportError:  # pragma: no cover
    resource = None

RUNNER = r'''
import json, sys
case = json.load(open(sys.argv[1]))
ns = {"__name__": "solution"}
loaded = True
try:
    exec(compile(case["code"], "<solution>", "exec"), ns)
except BaseException:
    loaded = False
res = []
for t in case["tests"]:
    try:
        if not loaded:
            raise RuntimeError("solution did not load")
        exec(compile(t, "<test>", "exec"), ns)
        res.append(True)
    except BaseException:
        res.append(False)
print(sys.argv[2] + json.dumps(res))
'''

CODE_BLOCK = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.S)


def extract_code(completion):
    """TRL passes a string for standard datasets and a list of message dicts for conversational ones."""
    if isinstance(completion, list):
        completion = completion[-1]["content"]
    m = CODE_BLOCK.search(completion)
    return m.group(1) if m else ""  # no code block means no reward


def _limits(cpu_seconds, mem_bytes):
    def apply():
        os.setsid()  # own process group so the whole tree can be killed on timeout
        if resource is None:
            return
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if sys.platform.startswith("linux"):  # RLIMIT_AS is unreliable on macOS
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    return apply


def run_tests(code, tests, timeout=5.0, mem_mb=512):
    """Return the list of per-test booleans. All False on timeout, crash or missing code."""
    if not code.strip():
        return [False] * len(tests)
    marker = "RESULT-" + uuid.uuid4().hex + ":"
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "runner.py"), "w") as f:
            f.write(RUNNER)
        with open(os.path.join(tmp, "case.json"), "w") as f:
            json.dump({"code": code, "tests": tests}, f)
        proc = subprocess.Popen(
            [sys.executable, "-I", "runner.py", "case.json", marker], cwd=tmp, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"},
            preexec_fn=_limits(int(timeout) + 1, mem_mb << 20),
        )
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()
            return [False] * len(tests)
        for line in reversed(out.splitlines()):
            if line.startswith(marker):
                return json.loads(line[len(marker):])
        return [False] * len(tests)


def unit_test_reward(completions, reward_tests, partial_credit=False, **kwargs):
    """GRPOTrainer reward function: one float per completion.

    `reward_tests` is a dataset column (list of assert strings); TRL passes every dataset column except
    `prompt` as a keyword argument. Binary by default (all tests pass = 1.0). Partial credit tends to be
    gamed by programs that satisfy easy tests, so turn it on only after looking at samples.
    """
    rewards = []
    for completion, tests in zip(completions, reward_tests):
        res = run_tests(extract_code(completion), tests)
        rewards.append(sum(res) / len(res) if partial_credit else float(all(res)))
    return rewards


if __name__ == "__main__":
    tests = ["assert add(2, 3) == 5", "assert add(0, 0) == 0"]
    good = "```python\ndef add(a, b):\n    return a + b\n```"
    assert unit_test_reward([good], [tests]) == [1.0]
    assert unit_test_reward([[{"role": "assistant", "content": good}]], [tests]) == [1.0]
    assert unit_test_reward(["```python\ndef add(a, b):\n    return a * b\n```"], [tests]) == [0.0]
    assert unit_test_reward(["```python\nwhile True:\n    pass\n```"], [tests]) == [0.0]
    assert unit_test_reward(["```python\nimport sys\nsys.exit(0)\n```"], [tests]) == [0.0]
    assert unit_test_reward(["no code here"], [tests]) == [0.0]
    assert unit_test_reward(["```python\ndef add(a, b):\n    return a + b if a != 0 else 1\n```"], [tests],
                            partial_credit=True) == [0.5]
    print("ok: pass=1.0 fail=0.0 timeout=0.0 sys.exit=0.0 no-code=0.0 partial=0.5")
