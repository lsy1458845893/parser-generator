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
            return self.itemsets[items_list.index(target.items)]
        else:
            self.itemsets.append(target)
            return target

    def __str__(self):
        return "\n".join([str(i) for i in self.itemsets])


table = Table([0])
print(table)

stream = ['1', '*', '0', '+', '1']
cursor = 0

def next():
    global cursor, stream
    if cursor < len(stream):
        tok = stream[cursor]
        cursor += 1
        return tok
    else:
        return 'EOF'


def apply(target, itemset):
    global cursor, stream
    stack = [next()]
    state = [itemset]
    while True:
        stack_top = stack[len(stack) - 1]
        state_top = state[len(state) - 1]
        if stack_top == target:
            break
        if stack_top not in state_top.transition:
            raise Exception(" %s not in %s" %
                            (stack_top, str(list(state_top.transition))))

        itemset = state_top.transition[stack_top]
        if not itemset.transition:  # reduce only
            print('reduce', [s.index for s in state], stack, stream[cursor:])
            items = itemset.items
            item = items[0]
            assert(len(items) == 1)
            assert(len(rules[item[0]]) == item[1] + 1)
            size = len(rules[item[0]]) - 2
            for i in range(size):
                stack.pop()
                state.pop()
            stack.pop()
            stack.append(rules[item[0]][0])
        else:  # shift , may have reduce but ignore it
            print('shift', [s.index for s in state], stack, stream[cursor:])
            stack.append(next())
            state.append(state_top.transition[stack_top])
    print(stack)

apply('S', table.itemsets[0])
