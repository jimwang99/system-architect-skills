#!/usr/bin/env python3
import json, os, shutil, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "..", "execute-milestone", "scripts", "review_gate.py")
STUBS = os.path.join(HERE, "..", "fixtures", "review-stubs")


def run_gate(stub, timeout="1"):
    tmp = tempfile.mkdtemp()
    tmp = os.path.realpath(tmp)
    dst = os.path.join(tmp, "workflow-review")
    shutil.copy(os.path.join(STUBS, stub), dst)
    os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC)
    env = {**os.environ,
           "PATH": tmp + os.pathsep + os.environ["PATH"],
           "WORKFLOW_REVIEW_TIMEOUT": timeout,
           "STUB_STATE": tmp}
    return subprocess.run([sys.executable, GATE, "aaa1111", "bbb2222"],
                          capture_output=True, text=True, env=env)


class TestVerdicts(unittest.TestCase):
    def test_success_exits_0_and_echoes_json(self):
        r = run_gate("success")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["verdict"], "approve")

    def test_advisory_findings_exit_0(self):
        r = run_gate("findings-advisory")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_blocking_findings_exit_1(self):
        r = run_gate("findings-blocking")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["findings"][0]["severity"], "blocking")

    def test_reject_exit_1(self):
        r = run_gate("reject")
        self.assertEqual(r.returncode, 1)


class TestTransport(unittest.TestCase):
    def test_timeout_twice_exits_3(self):
        r = run_gate("timeout-always")
        self.assertEqual(r.returncode, 3)
        self.assertIn("transport", r.stderr)

    def test_timeout_once_then_success_exits_0(self):
        r = run_gate("timeout-once")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_authfail_twice_exits_3(self):
        r = run_gate("authfail-always")
        self.assertEqual(r.returncode, 3)

    def test_authfail_once_then_success_exits_0(self):
        r = run_gate("authfail-once")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_malformed_twice_exits_3(self):
        r = run_gate("malformed-always")
        self.assertEqual(r.returncode, 3)


class TestUsage(unittest.TestCase):
    def test_missing_args_exit_2(self):
        r = subprocess.run([sys.executable, GATE], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
