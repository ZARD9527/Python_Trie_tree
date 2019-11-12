# -*- encoding:utf-8 -*-

class PrefixTree:
    def __init__(self, locat, timer, tr_id, count=0, level=0):
        self.locat = locat  # 存放location地点
        self.timer = timer  # 存放timestamp时间戳
        self.tr_id = tr_id  # 存放路径tr,数组
        if count == 0:
            self.count = len(self.tr_id)  # 存放count值
        else:
            self.count = count
        self.level = level  # 存放该节点所在的层次
        self.children = {}  # 存放孩子节点，("a",1)：node形式

    def insert(self, tr_id, sequence, height):
        """
        基操，插入一个序列
        :param sequence: 用户轨迹id
        :param sequence: 列表
        :param height: 树高度
        :return:
        """
        cur_node = self
        for item in sequence:
            if item not in cur_node.children:
                # 插入结点
                child = PrefixTree([item[0]], [item[1]], [tr_id], 0, cur_node.level + 1)
                # child = TrieNode(value=item, count=1, parent=cur_node, level=cur_node.level + 1, local_count=1)
                cur_node.children[item] = child
                # cur_node.sonNode.append(child)
                cur_node = child
                if child.level == height:
                    return
            else:
                # 更新结点
                cur_node = cur_node.children[item]
                cur_node.count += 1
                cur_node.tr_id.append(tr_id)
                # cur_node.local_count += 1
                if cur_node.level == height:
                    return

    # 插入孩子节点
    def insertSon(self, locat, timer, tr_id, count, level):
        node = (locat[0], timer[0])
        if self.children.__contains__(node):
            self.children[node].tr_id = tr_id
            self.children[node].count = count
            self.children[node].level = level
        else:
            t = PrefixTree(locat, timer, tr_id, count, level)

            # print(node)
            self.children[node] = t

    # 返回孩子节点列表
    def getSon(self):
        return self.sonNode

    # 返回该节点信息
    def getRootVal(self):
        return self.locat, self.timer, self.tr_id, self.count, self.level


# 前序遍历打印树
def traverse_tree(r):
    # print(r)
    # print(r.getRootVal())
    a = r.children.values()
    for item in a:
        print(item.getRootVal())
        if len(item.children) != 0:
            traverse_tree(item)


# 查找第n层的所有节点
def search_level_nodes(root_node, level, ret_nodes):
    son_nodes = root_node.children.values()

    for son_node in son_nodes:
        # print('--',son_node.getRootVal())
        if level == son_node.level:
            ret_nodes.append(son_node)
        elif level > son_node.level:
            search_level_nodes(son_node, level, ret_nodes)

    return ret_nodes


#
def search_tri(r, height, now_height, search_tri_arr=[("a", 1), ("b", 2), ("c", 3)], level=1, ret_search=[]):
    if level > len(search_tri_arr):
        return
    search_node = search_tri_arr[level - 1]
    for i in range(now_height, height + 1):
        leaf_nodes_i = search_level_nodes(r, i, [])
        for leaf in leaf_nodes_i:
            rootVal = leaf.getRootVal()
            rootLoc = rootVal[0]
            rootTim = rootVal[1]

            if rootLoc[0] == search_node[0] and rootTim[0] == search_node[1]:
                if level == len(search_tri_arr):  # 完全找到该tr
                    ret_search.append([leaf.tr_id, len(leaf.tr_id), leaf.count])
                else:
                    search_tri(leaf, height, leaf.level + 1, search_tri_arr, level + 1, ret_search)
    return ret_search


def output_data(tree, output, filename):
    level1_nodes = search_level_nodes(tree, 1, [])
    i = 1
    for level1_node in level1_nodes:
        level1_node2 = (level1_node.locat[0], level1_node.timer[0])
        level2_nodes = search_level_nodes(level1_node, 2, [])
        for level2_node in level2_nodes:
            ret_arr = []
            level2_node2 = (level2_node.locat[0], level2_node.timer[0])
            ret_arr.append(level1_node2)
            ret_arr.append(level2_node2)

            node_id = 'tr' + str(i)
            i += 1
            output[node_id] = ret_arr

    fileObject = open(filename, 'w')
    for key in output:
        fileObject.write(str(output.get(key)))
        fileObject.write('\n')
    fileObject.close()
