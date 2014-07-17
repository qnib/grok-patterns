#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Grok Pattern Testing

Usage:
  pattern_test.py [options] (-a| <pattern>) 
  pattern_test.py (-h | --help)
  pattern_test.py --version

Options:
  -a                     Test all pattern files within patterns/
  --patdir=<path>        Directory where the patterns could be find [default: /etc/grok/patterns/]
  --testcase-dir=<path>  Directory where the patterns could be find [default: /etc/grok/tests/]
  -h --help              Show this screen.
  --version              Show version.

"""

# load librarys
from docopt import docopt
from pprint import pprint
import os
import sys
from random import randint
import simplejson as json
from ConfigParser import ConfigParser
import envoy

class GrokTest(object):
    """
    Runs a series of grok pattern tests
    """

    def __init__(self, options):
        """
        Init of instance
        """
        self.opt = options
        self.pat_dir = options['--patdir']
        self.test_dir = options['--testcase-dir']
        self.scens = {}
        self.ignore_keys = ['SPACE',]

    def collect_patterns(self):
        """
        does sth
        """
        scen = "flat"
        for dirpath, dnames, fnames in os.walk(self.pat_dir):
            if dirpath != self.pat_dir:
                #TODO: using subdirs for scenarios
                scen = dirpath.split("/")[-1]
                continue
            self.scens[scen] = []
            for fname in fnames:
                self.scens[scen].append("%s/%s" % (dirpath, fname))

    def run(self):
        """
        run scenarios
        """
        for scen, pattern_files in self.scens.items():
            header = self.create_ruby(pattern_files)
            self.run_tests(scen, header)

    def run_tests(self, scen, header):
        """
        iterates over the test files and kicks off every tests
        """
        scen = "flat"
        for dirpath, dnames, fnames in os.walk(self.test_dir):
            if dirpath != self.test_dir:
                #TODO: using subdirs for scenarios
                scen = dirname.split("/")[-1]
                break
            for fname in fnames:
		if not fname.endswith('.test'):
                   continue
                print "### Within %s"  % fname
                fpath = "%s/%s" % (dirpath, fname)
                self.run_test(header, fpath)

    def run_test(self, header, fpath):
        """
        extract test from test_file, and run ruby
        """
        config = ConfigParser()
        config.read(fpath)
        out_width = 50
        out_str = ""
        for test in config.sections():
            out_str = "# Running test '%s'..." % test
            print out_str,
            ruby_lines = [line for line in header]
            ruby_exe = "/tmp/grok_test_%s_pattern" % randint(100000, 999999)
            comp_line = config.get(test, "comp_line")
            inp = config.get(test, "input")
            inp = inp.replace("XXX","")
            ruby_lines.append("grok.compile('%s')" % comp_line)
            ruby_lines.append("p grok.match('%s').captures " % inp)
            filed = open(ruby_exe, "w")
            ruby_content = "\n".join(ruby_lines)
            filed.write(ruby_content)
            filed.close()
            if config.get(test, "result") == 'FAIL':
               res_exp = None
            else:
               res_exp = json.loads(config.get(test, "result"))
            testrun = envoy.run("ruby %s" % ruby_exe)
            if testrun.status_code != 0 and res_exp is not None:
                out_fill = "."*(out_width - len(out_str))
                print "%s %s" % (out_fill, "ERROR")
                print "ruby execution fails! ", testrun.std_err
            elif res_exp is None:
                out_fill = "."*(out_width - len(out_str))
                print "%s %s" % (out_fill, "PASS (expected FAIL)")
            else:
                stdout = testrun.std_out.replace("=>", ":")
                try:
                    res_got = json.loads(stdout)
                except json.scanner.JSONDecodeError, err:
                    out_fill = "."*(out_width - len(out_str))
                    print "%s %s" % (out_fill, "FAIL")
                    print stdout
                    sys.exit(1)
		# clean result
                for key in self.ignore_keys:
                    if key in res_got:
                       del res_got[key]
                if res_got != res_exp:
                    out_fill = "."*(out_width - len(out_str))
                    print "%s %s" % (out_fill, "MISMATCH")
                    print "## exp"
                    pprint(res_exp)
                    print "## got"
                    pprint(res_got)
                    sys.exit(1)
                else:
                    out_fill = "."*(out_width - len(out_str))
                    print "%s %s" % (out_fill, "PASS")
                    os.remove(ruby_exe)

    @staticmethod
    def create_ruby(pattern_files):
        """
        creates ruby script to be executed
        """
        lines = []
        lines.append("require 'grok-pure'")
        lines.append("grok = Grok.new")
        for file_path in pattern_files:
            lines.append("grok.add_patterns_from_file('%s')" % file_path)
        return lines



def main():
    """ main function """
    options = docopt(__doc__,  version='0.1')
    grok_test = GrokTest(options)
    grok_test.collect_patterns()
    grok_test.run()

if __name__ == "__main__":
    main()
