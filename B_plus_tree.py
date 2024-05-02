class BPlusTree:
    def __init__(self, degree):
        self.degree = degree
        self.root = BPlusNode(degree)

    def insert(self, key, value):
        self.root.insert(key, value)
        if len(self.root.keys) > self.degree:
            new_root = BPlusNode(self.degree, is_leaf=False)
            new_root.children.append(self.root)
            self.root.split(new_root)
            self.root = new_root
            self.root.parent = None 

    def search(self, key):
        return self.root.search(key)

    def delete(self, key):
        self.root.delete(key)
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]
            self.root.parent = None

    def print_tree(self):
        self.root.print()


class BPlusNode:
    def __init__(self, degree, is_leaf=True,parent=None):
        self.degree = degree
        self.keys = []
        self.values = [] if is_leaf else None
        self.children = [] if not is_leaf else None
        self.is_leaf = is_leaf
        self.parent = parent 

    def insert(self, key, value):
        if self.is_leaf:
            self._insert_in_leaf(key, value)
        else:
            child_index = self._find_child_index(key)
            if child_index < len(self.children):
                child = self.children[child_index]
                child.insert(key, value)
                if len(child.keys) > self.degree:
                    new_child = BPlusNode(self.degree, is_leaf=child.is_leaf,parent=self)
                    child.split(new_child)
                    self.children.insert(child_index + 1, new_child)
                    self.keys.insert(child_index, new_child.keys[0])
            else:
                new_child = BPlusNode(self.degree, is_leaf=True,parent=self)
                new_child.insert(key, value)
                self.children.append(new_child)
                self.keys.append(new_child.keys[0])

    def _insert_in_leaf(self, key, value):
        index = self._find_insert_index(key)
        self.keys.insert(index, key)
        self.values.insert(index, value)

    def split(self, new_node):
        split_index = len(self.keys) // 2
        new_node.keys = self.keys[split_index:]
        new_node.values = self.values[split_index:]
        self.keys = self.keys[:split_index]
        self.values = self.values[:split_index]

    def search(self, key):
        if self.is_leaf:
            index = self._find_search_index(key)
            if index < len(self.keys) and self.keys[index] == key:
                return self.values[index]
            else:
                return None
        else:
            child_index = self._find_child_index(key)
            if child_index < len(self.children):
                return self.children[child_index].search(key)
            else:
                return None

    def _find_insert_index(self, key):
        for i, k in enumerate(self.keys):
            if key < k:
                return i
        return len(self.keys)

    def _find_search_index(self, key):
        for i, k in enumerate(self.keys):
            if key == k:
                return i
        return len(self.keys)

    def _find_child_index(self, key):
        for i, k in enumerate(self.keys):
            if key < k:
                return i
        return len(self.keys)

    def delete(self, key):
        if self.is_leaf:
            self._delete_from_leaf(key)
        else:
            child_index = self._find_child_index(key)
            if child_index < len(self.children):
                self.children[child_index].delete(key)

        if len(self.keys) < self.degree // 2:
            self._handle_underflow()

    def _delete_from_leaf(self, key):
        index = self._find_search_index(key)
        if index < len(self.keys) and self.keys[index] == key:
            del self.keys[index]
            del self.values[index]

    def _handle_underflow(self):
        if self.is_root():
            return

        left_sibling = self._get_left_sibling()
        if left_sibling and len(left_sibling.keys) > self.degree // 2:
            self._borrow_from_left(left_sibling)
            return

        right_sibling = self._get_right_sibling()
        if right_sibling and len(right_sibling.keys) > self.degree // 2:
            self._borrow_from_right(right_sibling)
            return

        if left_sibling:
            self._merge_with_left(left_sibling)
        else:
            self._merge_with_right(right_sibling)

    def _borrow_from_left(self, left_sibling):
        borrowed_key = left_sibling.keys.pop()
        borrowed_value = left_sibling.values.pop()
        self.keys.insert(0, borrowed_key)
        self.values.insert(0, borrowed_value)

        if not self.is_leaf:
            borrowed_child = left_sibling.children.pop()
            self.children.insert(0, borrowed_child)

    def _borrow_from_right(self, right_sibling):
        borrowed_key = right_sibling.keys.pop(0)
        borrowed_value = right_sibling.values.pop(0)
        self.keys.append(borrowed_key)
        self.values.append(borrowed_value)

        if not self.is_leaf:
            borrowed_child = right_sibling.children.pop(0)
            self.children.append(borrowed_child)

    def _merge_with_left(self, left_sibling):
        left_sibling.keys.extend(self.keys)
        left_sibling.values.extend(self.values)
        if not self.is_leaf:
            left_sibling.children.extend(self.children)
        self.keys = left_sibling.keys
        self.values = left_sibling.values
        self.children = left_sibling.children

    def _merge_with_right(self, right_sibling):
        if right_sibling is not None:
            self.keys.extend(right_sibling.keys)
            self.values.extend(right_sibling.values)
            if not self.is_leaf:
                self.children.extend(right_sibling.children)
                if self.children:  
                    for child in self.children:
                        child.parent = self

    def _get_left_sibling(self):
        if self.is_root() or not self.keys:
            return None

        parent = self._get_parent()
        index = parent.children.index(self)

        if index > 0:
            return parent.children[index - 1]
        else:
            return None

    def _get_right_sibling(self):
        if self.is_root() or not self.keys:
            return None

        parent = self._get_parent()
        index = parent.children.index(self)

        if index < len(parent.children) - 1:
            return parent.children[index + 1]
        else:
            return None

    def is_full(self):
        return len(self.keys) >= self.degree

    def is_root(self):
        return self.parent is None

    def _get_parent(self):
        return self.parent

    def print_tree(self):
        self._print_node(self)

    def _print_node(self, node, depth=0):
        prefix = "  " * depth
        if node.is_leaf:
            print(f"{prefix}Leaf Node: {node.keys}")
        else:
            print(f"{prefix}Internal Node: {node.keys}")
            for child in node.children:
                self._print_node(child, depth + 1)



tree = BPlusTree(degree=3)

tree.insert(10, "A")
tree.insert(20, "B")
tree.insert(5, "C")
tree.insert(30, "D")
tree.insert(15, "E")
tree.insert(40, "F")

print("Tree structure after insertion:")
tree.root.print_tree()

result = tree.search(15)
print("\nSearch result for key 15:", result)

tree.delete(10)
print("\nTree structure after deleting key 10:")
tree.root.print_tree()
