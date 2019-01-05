terminals = ('+', '*', '0', '1', 'EOF')

rules = (
    ('S', 'E', 'EOF'),
    ('E', 'E', '*', 'B'),
    ('E', 'E', '+', 'B'),
    ('E', 'B'),
    ('B', '0'),
    ('B', '1'),
)

symbols_indexs = {}  # [symbol]:rule_id[]
for i in range(len(rules)):
    symbol = rules[i][0]
    if symbol in symbols_indexs:
        symbols_indexs[symbol].append(i)
    else:
        symbols_indexs[symbol] = [i]


class ItemSet:
    def __init__(self, items):
        self.index = None
        self.items = items[:]  # (rule_id, dot_pos)[]
        expand = 0
        while expand < len(self.items):
            rule_id, dot_pos = self.items[expand]  # 0 <= dot_pos <= len(rule)
            if dot_pos + 1 >= len(rules[rule_id]):  # item end
                expand += 1
                continue
            symbol = rules[rule_id][dot_pos + 1]
            if symbol in terminals:  # terminal no need expand
                expand += 1
                continue
            rule_id_list = symbols_indexs[symbol]
            for i in rule_id_list:
                if (i, 0) not in self.items:
                    self.items.append((i, 0))
            expand += 1
        self.items.sort()

    def __str__(self):
        s = []
        for rule_id, dot_pos in self.items:
            rule = rules[rule_id]
            temp = ["<%s>" % symbol for symbol in rule[1:]]
            temp.insert(dot_pos, '.')
            s.append(rule[0] + " -> " + "".join(temp) + "\n")
        return "".join(s)

    def expand(self, table):  # create new itemset and filter already existed itemset push to table
        self.transition = {}
        for rule_id, dot_pos in self.items:
            if dot_pos + 1 >= len(rules[rule_id]):
                continue
            symbol = rules[rule_id][dot_pos + 1]
            if symbol in self.transition:
                self.transition[symbol].append((rule_id, dot_pos + 1))
            else:
                self.transition[symbol] = [(rule_id, dot_pos + 1)]
        for symbol in self.transition:
            self.transition[symbol] = table.filter(
                ItemSet(self.transition[symbol]))


class Table:
    def __init__(self, entry):  # entry: rule_id[]
        self.itemsets = []  # ItemSet[]
        for rule_id in entry:
            self.itemsets.append(ItemSet([(rule_id, 0)]))

        expand = 0
        while expand < len(self.itemsets):
            itemset = self.itemsets[expand]
            itemset.index = expand
            itemset.expand(self)
            expand += 1

    def filter(self, target):
        items_list = [itemset.items for itemset in self.itemsets]
        if target.items in items_list:
            return items_list.index(target.items)
        else:
            self.itemsets.append(target)
            return target

    def __str__(self):
        return "\n".join([str(i) for i in self.itemsets])


table = Table([0])
print(table)
