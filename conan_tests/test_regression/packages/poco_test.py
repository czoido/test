from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, conan_create_command


class PocoTest(BaseExeTest):

    libref = "Poco/1.9.0@pocoproject/stable"
    librepo = "https://github.com/pocoproject/conan-poco.git"
    branch = "release/1.9.0"

    def setUp(self):
        super(PocoTest, self).setUp()
        run("conan remove %s -f" % self.libref, ignore_error=True)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run(conan_create_command("conan/testing"))

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
