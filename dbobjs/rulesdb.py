import os
import re
import string

from constants import RULES_FILE, DATA_DIR

class Rules:
    
    def __init__(self):
        self._rules_file = os.path.join(DATA_DIR, RULES_FILE)
        if not os.path.isdir(DATA_DIR):
            os.mkdir(DATA_DIR)
        if not os.path.exists(self._rules_file):
            with open(self._rules_file, 'w') as f:
                f.write("")
                self._ruletree = None
        else:
            self._ruletree = self.make_rules_tree()

    
    def clear_rules(self):
        with open(self._rules_file, 'w') as f:
            f.write("")
    
    
    def make_rules_tree(self):
        rulees_tree = RTree("root","")
        rule_lines = self._read_in_rules()
        for rule in rule_lines:
            rulenum = rule.split(' ', 1)[0]
            rulees_tree.insert_rule(self._simplify(rulenum), rule)
        return rulees_tree


    def _read_in_rules(self):
        parsed_lines = []
        curr_rule = ""
        rflines = [line for line in open(self._rules_file)]
        for line in rflines:
            if not line.strip():
                if curr_rule:
                    parsed_lines.append(curr_rule)
                    curr_rule = ""
            else:
                curr_rule += line + " "
        return parsed_lines


    def _simplify(self, rulenum):
        rulenum = re.sub(r'[\W\s]', '', re.sub(r' ', '_', rulenum)).lower()
        return ''.join([ch for ch in rulenum if ch not in string.punctuation])


    def retrieve_rule(self, ruleorkw):
        rule = self._ruletree.search_for_rule(self._simplify(ruleorkw))
        return rule.text if rule else "No such rule found"


class Rule:
    
    def __init__(self, rule_text):
        self.rule_text = rule_text
    
    @property
    def text(self):
        return self.rule_text


class RTree:
    '''
        RTree is a "rules tree". It is a tree structure for storing rules. It is
        implemented as a prefix tree, in which each node is composed of the last
        character of its "key" and its matching "value". For example, rule 
        100.1a will be found at node a under 1 -> 0 -> 0 -> 1 (omitting punct) 
        -> a, and it will contain the text for the rule (including the rule 
        number at the beginning). Keywords are stored under the same root node
        in a similar fashion.
    '''
    def __init__(self, rulenum, rule):
        self.key = rulenum
        self.value = rule
        self._children = dict()


    def _get_rule(self):
        return self.value + self._get_next_level()


    def _get_next_level(self):
        children_values = ""
        for child in self._children:
            if not self._children[child].value:
                children_values += self._children[child].get_next_level()
            else:
                children_values += self._children[child].value
        return children_values


    def insert_rule(self, rulenum, rule):
        if not rulenum:
            self.value = rule
        elif rulenum[0] in self._children:
            self._children[rulenum[0]].insert_rule(rulenum[1:], rule)
        else:
            if len(rulenum) == 1:
                self._children[rulenum[0]] = RTree(rulenum[0], rule)
            else:
                self._children[rulenum[0]] = RTree(rulenum[0], "")
                self._children[rulenum[0]].insert_rule(rulenum[1:], rule)


    def search_for_rule(self, rulenum):
        if rulenum[0] in self._children:
            if len(rulenum) == 1:
                return Rule(self._children[rulenum[0]]._get_rule())
            return self._children[rulenum[0]].search_for_rule(rulenum[1:])
        return None