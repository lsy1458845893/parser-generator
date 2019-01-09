# terminals = ('a', 'b', '=', '*', 'x')
terminals = 'abcde'

rules = (
    ('A', 'S'),
    ('S', 'aEc'),
    ('S', 'aFd'),
    ('S', 'bFc'),
    ('S', 'bEd'),
    ('E', 'e'),
    ('F', 'e'),
)

first = {}

update = True
while update:
    update = False
    for r in rules:
        if r[0] not in first:
            first[r[0]] = set()
            update = True
        if r[1][0] in terminals:
            # item first is terminal
            if r[1][0] not in first[r[0]]:
                first[r[0]].add(r[1][0])
                update = True
                continue
        # item first is noterminal
        if r[1][0] not in first:
            continue
        nset = first[r[0]].union(first[r[1][0]])
        if nset != first[r[0]]:
            first[r[0]] = nset
            update = True

for i in first:
    first[i] = list(first[i])
    first[i].sort()


class ItemSet:
    def __init__(self, init_itemset):
        self.index = None
        self.items = init_itemset[:]
        i = 0
        while i < len(self.items):
            # expand item
            rule, dot, follow = self.items[i]
            rule = rules[rule]
            if dot == len(rule[1]):
                # example: I -> ab.,c
                i += 1
                continue
            symbol = rule[1][dot]
            if symbol not in terminals:  # symbol may add itemset
                if dot + 1 == len(rule[1]):
                    # example: I -> a.A,b
                    follow = self.items[i][2]
                elif rule[1][dot + 1] in terminals:
                    # example: I -> a.Ab,c
                    follow = rule[1][dot + 1]
                else:
                    # example: I -> a.AB,c
                    follow = first[rule[1][dot + 1]]
                for rid in range(len(rules)):
                    if rules[rid][0] != symbol:
                        continue
                    if (rid, 0, follow) not in self.items:
                        self.items.append((rid, 0, follow))
            i += 1

    def expand(self, table):  # create new itemset and filter already existed itemset push to table
        self.transition = {}
        for rule_id, dot_pos, follow in self.items:
            if dot_pos == len(rules[rule_id][1]):
                # example: I -> ab.,c  reduce
                continue
            # example: I -> a.b,c  shift
            symbol = rules[rule_id][1][dot_pos]
            if symbol in self.transition:
                if (rule_id, dot_pos + 1, follow) not in self.transition[symbol]:
                    self.transition[symbol].append(
                        (rule_id, dot_pos + 1, follow))
            else:
                self.transition[symbol] = [(rule_id, dot_pos + 1, follow)]
        for symbol in self.transition:
            self.transition[symbol] = table.join(
                ItemSet(self.transition[symbol]))


class Table:
    def __init__(self, entry):
        self.itemsets = []  # ItemSet[]
        for rule_id in entry:
            self.itemsets.append(ItemSet([(rule_id, 0, '$')]))

        expand = 0
        while expand < len(self.itemsets):
            itemset = self.itemsets[expand]
            itemset.index = expand
            itemset.expand(self)
            expand += 1

    def join(self, target):
        items_list = [itemset.items for itemset in self.itemsets]
        if target.items in items_list:
            return self.itemsets[items_list.index(target.items)]
        else:
            self.itemsets.append(target)
            return target


table = Table([0])
print "\n\n".join(["\n".join([str(rules[j[0]][0]) + ' -> ' + str(rules[j[0]][1][:j[1]]) + '.' + str(rules[j[0]][1][j[1]:]) + ' ,' + str(j[2]) for j in i.items])
                   for i in table.itemsets])
