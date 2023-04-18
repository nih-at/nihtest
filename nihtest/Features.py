import re

from nihtest import Utility


class Features:
    def __init__(self, configuration):
        self.feature_files = configuration.feature_files
        self.features = {}
        self.features_read = False

    def has_feature(self, feature):
        if not self.features_read:
            self.read_features()
        return feature in self.features

    def read_features(self):
        pattern = re.compile("#define ([_A-Za-z][_A-Za-z0-9]*)")
        for file in self.feature_files:
            lines = Utility.read_lines(file)

            for line in lines:
                if m := pattern.match(line):
                    self.features[m.group(1)] = 1
