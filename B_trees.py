class BTreeNode:
    def __init__(self, degree, is_leaf=True):
        self.degree = degree
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf
        self.parent = None

    def is_full(self):
        return len(self.keys) == 2 * self.degree - 1

    def insert(self, key):
        if self.is_full():
            new_node = BTreeNode(self.degree, is_leaf=self.is_leaf)
            mid = len(self.keys) // 2
            new_node.keys = self.keys[mid + 1:]
            self.keys = self.keys[:mid]

            if not self.is_leaf:
                new_node.children = self.children[mid + 1:]
                self.children = self.children[:mid + 1]
                for child in new_node.children:
                    child.parent = new_node  

            if self.parent:
                parent = self.parent
                parent.keys.insert(parent.find_insert_index(key), self.keys.pop())
                parent.children.insert(parent.find_insert_index(key) + 1, new_node)
                new_node.parent = parent
                parent.insert(key)  
            else:
                new_root = BTreeNode(self.degree, is_leaf=False)
                new_root.keys.append(self.keys.pop())
                new_root.children = [self, new_node]
                self.parent = new_node.parent = new_root

                if key > new_root.keys[0]:
                    new_root.children[1].insert(key)
                else:
                    new_root.children[0].insert(key)

        else:
            if self.is_leaf:
                self.keys.insert(self.find_insert_index(key), key)
            else:
                idx = self.find_insert_index(key)
                self.children[idx].insert(key)

    def find_insert_index(self, key):
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < key:
            idx += 1
        return idx

    def search(self, key):
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            idx += 1

        if idx < len(self.keys) and key == self.keys[idx]:
            return True
        elif self.is_leaf:
            return False
        else:
            return self.children[idx].search(key)


class BTree:
    def __init__(self, degree):
        self.degree = degree
        self.root = BTreeNode(degree, is_leaf=True)

    def insert(self, key):
        self.root.insert(key)
        if self.root.parent:
            self.root = self.root.parent

    def search(self, key):
        return self.root.search(key)

    def print_tree(self):
        self._print_node(self.root)

    def _print_node(self, node):
        if node:
            if not node.is_leaf:
                for i in range(len(node.children)):
                    self._print_node(node.children[i])
            print("Keys:", node.keys)



if __name__ == "__main__":
    btree = BTree(degree=3)

    keys_to_insert = [10, 20, 5, 25, 7, 3, 30]
    for key in keys_to_insert:
        btree.insert(key)

    print("B-tree structure after insertion:")
    btree.print_tree()


    if btree.search(20):
        print(f"Key 20 found in the B-tree.")
    else:
        print(f"Key 20 not found in the B-tree.")
