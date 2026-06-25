
#!/usr/bin/env python3
"""
英文单词统计函数
完全专注于英文文本，输出简洁明了
"""

import re
from collections import Counter


def count_english_words(file_path):
    """
    统计英文文本文件中每个单词的出现次数
    自动处理大小写（不区分大小写）

    Args:
        file_path: 文本文件路径

    Returns:
        dict: {单词: 次数}

    Example:
        counts = count_english_words("text.txt")
        print(counts)
    """
    # 尝试不同编码读取文件
    encodings = ['utf-8', 'gbk', 'latin-1', 'utf-8-sig']
    text = None

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        raise ValueError(f"无法读取文件 {file_path}")

    # 只匹配英文单词（字母开头，可包含连字符或撇号）
    words = re.findall(r'\b[a-zA-Z][a-zA-Z\-\']*\b', text)

    if not words:
        return {}

    # 统一转为小写（不区分大小写）
    words = [word.lower() for word in words]

    # 统计词频
    return dict(Counter(words))


def print_word_counts(word_counts, limit=None):
    """
    简洁地打印单词统计结果

    Args:
        word_counts: 单词统计字典
        limit: 显示前多少个单词，None表示全部显示

    Example:
        counts = count_english_words("text.txt")
        print_word_counts(counts, limit=10)
    """
    if not word_counts:
        print("No English words found.")
        return

    # 按次数排序（从高到低）
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(word_counts.values())

    # 简洁标题
    print(f"\nEnglish Word Count Analysis")
    print("-" * 40)
    print(f"Total words: {total}")
    print(f"Unique words: {len(word_counts)}")

    # 限制显示数量
    if limit and limit > 0:
        sorted_words = sorted_words[:limit]
        print(f"\nTop {limit} most frequent words:")
    else:
        print("\nAll words:")

    print("-" * 30)

    # 简洁格式：序号. 单词 次数 (百分比)
    for i, (word, count) in enumerate(sorted_words, 1):
        percent = (count / total) * 100
        print(f"{i:2d}. {word:<18} {count:>3d} ({percent:.1f}%)")


def save_results(word_counts, output_file="word_counts.txt"):
    """
    保存统计结果到文件

    Args:
        word_counts: 单词统计字典
        output_file: 输出文件名

    Returns:
        str: 输出文件路径

    Example:
        counts = count_english_words("text.txt")
        save_results(counts, "results.txt")
    """
    if not word_counts:
        return "No words to save"

    # 排序
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(word_counts.values())

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("English Word Count Results\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total words: {total}\n")
        f.write(f"Unique words: {len(word_counts)}\n")

        if sorted_words:
            f.write(f"Most frequent: '{sorted_words[0][0]}' ({sorted_words[0][1]} times)\n\n")

        f.write("Word Frequency List\n")
        f.write("-" * 30 + "\n")

        for i, (word, count) in enumerate(sorted_words, 1):
            percent = (count / total) * 100
            f.write(f"{i:3d}. {word:<20} {count:>4d} ({percent:.1f}%)\n")

    return output_file


# 主函数：测试和使用示例
if __name__ == "__main__":
    # 统计当前文件夹中的 txt.txt 文件
    input_file = "txt.txt"

    try:
        # 统计英文单词
        print(f"Processing file: {input_file}")
        word_counts = count_english_words(input_file)

        if not word_counts:
            print("No English words found in the file.")
        else:
            # 显示前20个最常见的单词
            print_word_counts(word_counts, limit=20)

            # 保存结果
            result_file = save_results(word_counts, "english_word_counts.txt")
            print(f"\nResults saved to: {result_file}")

            # 显示最重要的统计信息
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            print(f"\nKey Statistics:")
            print(f"- Most frequent word: '{sorted_words[0][0]}' ({sorted_words[0][1]} times)")
            print(f"- Average occurrences per word: {sum(word_counts.values())/len(word_counts):.2f}")

    except FileNotFoundError:
        print(f"File not found: {input_file}")
    except Exception as e:
        print(f"Error: {e}")