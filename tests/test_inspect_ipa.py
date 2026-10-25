import importlib.util
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'inspect_ipa.py'
spec = importlib.util.spec_from_file_location('inspect_ipa', SCRIPT)
ipa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ipa)


class InspectIPATest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'youtube.ipa'
        self.info = {'CFBundleIdentifier': 'com.google.ios.youtube',
                     'CFBundleShortVersionString': '21.29.3',
                     'CFBundleVersion': '123456789',
                     'CFBundleExecutable': 'YouTube'}

    def write_ipa(self, fmt=plistlib.FMT_BINARY, executable=True):
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('Payload/Renamed.app/Info.plist', plistlib.dumps(self.info, fmt=fmt))
            if executable:
                archive.writestr('Payload/Renamed.app/YouTube', b'fixture')

    def test_xml_and_binary_plists_with_renamed_app(self):
        for fmt in (plistlib.FMT_BINARY, plistlib.FMT_XML):
            with self.subTest(fmt=fmt):
                self.write_ipa(fmt)
                self.assertEqual(ipa.inspect(self.path), '21.29.3')

    def test_environment_output(self):
        self.write_ipa()
        env_file = Path(self.temp.name) / 'github-env'
        subprocess.run([sys.executable, str(SCRIPT), str(self.path)],
                       check=True, capture_output=True,
                       env={**os.environ, 'GITHUB_ENV': str(env_file)})
        self.assertEqual(env_file.read_text(), 'YT_VERSION=21.29.3\n')

    def test_other_app_rejected(self):
        self.info['CFBundleIdentifier'] = 'example.other'
        self.write_ipa()
        with self.assertRaises(ValueError):
            ipa.inspect(self.path)

    def test_version_cannot_inject_environment_lines(self):
        self.info['CFBundleShortVersionString'] = '21.29.3\nOTHER=value'
        self.write_ipa()
        with self.assertRaises(ValueError):
            ipa.inspect(self.path)

    def test_missing_executable_rejected(self):
        self.write_ipa(executable=False)
        with self.assertRaises(ValueError):
            ipa.inspect(self.path)

    def test_webpage_instead_of_ipa_rejected(self):
        self.path.write_text('<html>download page</html>')
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.path)], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'Invalid IPA', result.stderr)

    def test_multiple_apps_rejected(self):
        self.write_ipa()
        with zipfile.ZipFile(self.path, 'a') as archive:
            archive.writestr('Payload/Other.app/Info.plist', plistlib.dumps(self.info))
        with self.assertRaises(ValueError):
            ipa.inspect(self.path)


if __name__ == '__main__':
    unittest.main()
