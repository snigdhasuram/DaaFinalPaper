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

    def remove_key(self, key):
        if key in self.keys:
            idx = self.keys.index(key)
            self.keys.pop(idx)
            return True
        return False

    def borrow_from_sibling(self, idx):
        if idx > 0 and not self.children[idx - 1].is_min_degree():
            sibling = self.children[idx - 1]
            self.keys.insert(0, sibling.keys.pop())
            if not sibling.is_leaf:
                self.children.insert(0, sibling.children.pop())

        elif idx < len(self.children) - 1 and not self.children[idx + 1].is_min_degree():
            sibling = self.children[idx + 1]
            self.keys.append(sibling.keys.pop(0))
            if not sibling.is_leaf:
                self.children.append(sibling.children.pop(0))

    def merge_with_sibling(self, idx):
        if idx > 0:
            sibling = self.children[idx - 1]
            sibling.keys.extend(self.keys)
            sibling.children.extend(self.children)
            if self.parent:
                self.parent.children.pop(idx)
                self.parent.keys.pop(idx - 1)
        else:
            sibling = self.children[idx + 1]
            self.keys.extend(sibling.keys)
            self.children.extend(sibling.children)
            if self.parent:
                self.parent.children.pop(idx + 1)
                self.parent.keys.pop(idx)

        if self.parent and not self.parent.keys:
            self.parent = None  

    def is_min_degree(self):
        return len(self.keys) >= self.degree - 1


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

    def delete(self, key):
        self._delete(self.root, key)
        if self.root.keys == [] and not self.root.is_leaf:
            self.root = self.root.children[0]  
    def _delete(self, node, key):
        if key in node.keys:
            idx = node.keys.index(key)
            if node.is_leaf:
                node.keys.remove(key)
            else:
                if node.children[idx].keys:
                    predecessor = self._get_predecessor(node.children[idx])
                    node.keys[idx] = predecessor
                    self._delete(node.children[idx], predecessor)
                elif node.children[idx + 1].keys:
                    successor = self._get_successor(node.children[idx + 1])
                    node.keys[idx] = successor
                    self._delete(node.children[idx + 1], successor)
                else:
                    node.merge_with_sibling(idx)
                    self._delete(node.children[idx], key)
        else:
            idx = node.find_insert_index(key)
            if idx < len(node.children):
                if not node.children[idx].is_min_degree():
                    self._delete(node.children[idx], key)
                else:
                    if idx > 0 and not node.children[idx - 1].is_min_degree():
                        node.borrow_from_sibling(idx)
                        self._delete(node.children[idx], key)
                    elif idx < len(node.children) - 1 and not node.children[idx + 1].is_min_degree():
                        node.borrow_from_sibling(idx + 1)
                        self._delete(node.children[idx], key)
                    else:
                        node.merge_with_sibling(idx)
                        self._delete(node.children[idx], key)


    def _get_predecessor(self, node):
        while not node.is_leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _get_successor(self, node):
        while not node.is_leaf:
            node = node.children[0]
        return node.keys[0]

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

    keys_to_insert = [10, 20, 5, 15, 25, 7, 3, 30]
    for key in keys_to_insert:
        btree.insert(key)

    print("B-tree structure after insertion:")
    btree.print_tree()

    if btree.search(25):
        print(f"Key 25 found in the B-tree.")
    else:
        print(f"Key 25 not found in the B-tree.")

    btree.delete(25)
    print("B-tree structure after deletion of 25:")
    btree.print_tree()
