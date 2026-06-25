# 计算列表平均值函数
def calc_average(num_list):
    if len(num_list) == 0:
        return 0
    total = sum(num_list)
    avg = total / len(num_list)
    return avg

# 测试函数
if __name__ == "__main__":
    test = [2,4,6,8,10]
    print("列表平均值：", calc_average(test))