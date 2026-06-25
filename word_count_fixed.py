#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计文本文件中每个单词出现次数的函数 - 修复版
将结果保存到指定文件
"""

import re
import collections
import argparse
import os
import time
import json
from typing import Dict, List, Tuple, Optional


def count_words_in_file(file_path: str, case_sensitive: bool = False) -> Dict[str, int]:
    """
    统计文本文件中每个单词的出现次数

    Args:
        file_path: 文本文件路径
        case_sensitive: 是否区分大小写，默认为False（不区分）

    Returns:
        字典，键为单词，值为出现次数

    Raises:
        FileNotFoundError: 如果文件不存在
        IOError: 如果读取文件出错
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        # 尝试不同的编码读取文件
        encodings = ['utf-8', 'gbk', 'latin-1', 'utf-8-sig']
        content = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise IOError("无法使用支持的编码读取文件。请检查文件编码。")

    except Exception as e:
        raise IOError(f"读取文件时出错: {e}")

    return count_words_in_text(content, case_sensitive)


def count_words_in_text(text: str, case_sensitive: bool = False) -> Dict[str, int]:
    """
    统计文本中每个单词的出现次数

    Args:
        text: 要统计的文本
        case_sensitive: 是否区分大小写

    Returns:
        字典，键为单词，值为出现次数
    """
    if not text or not isinstance(text, str):
        return {}

    # 移除换行符和制表符，统一为空格
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # 使用正则表达式提取单词（改进版：更好地处理撇号）
    # \b 表示单词边界，[a-zA-Z] 匹配字母，[a-zA-Z']* 匹配0个或多个字母或撇号
    # 这样可以匹配 "don't" 作为一个单词
    words = re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", text)

    # 也可以匹配数字单词
    number_words = re.findall(r"\b\d+\b", text)
    words.extend(number_words)

    if not words:
        return {}

    # 如果不区分大小写，将所有单词转换为小写
    if not case_sensitive:
        words = [word.lower() for word in words]

    # 使用Counter统计词频
    word_counts = collections.Counter(words)

    return dict(word_counts)


def save_word_counts(word_counts: Dict[str, int],
                     output_file: Optional[str] = None,
                     results_dir: Optional[str] = None,
                     format_type: str = 'txt') -> str:
    """
    保存单词统计结果到文件

    Args:
        word_counts: 单词统计字典
        output_file: 输出文件名（如果为None则自动生成）
        results_dir: 结果目录（如果为None则使用当前目录）
        format_type: 输出格式，支持 'txt' 或 'json'

    Returns:
        输出文件的完整路径

    Raises:
        ValueError: 如果word_counts为空或格式不支持
    """
    if not word_counts:
        raise ValueError("没有单词统计数据可保存")

    # 确定输出目录
    if results_dir is None:
        results_dir = os.path.dirname(os.path.abspath(__file__))
    elif not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # 确定输出文件名
    if output_file is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        output_file = f"word_counts_{timestamp}.{format_type}"

    # 确保文件后缀正确（不区分大小写）
    if not output_file.lower().endswith(f'.{format_type}'):
        # 移除现有的扩展名（如果有）
        base_name = output_file.rsplit('.', 1)[0] if '.' in output_file else output_file
        output_file = f"{base_name}.{format_type}"

    # 构建完整路径
    output_path = os.path.join(results_dir, output_file)

    # 按词频排序（从高到低）
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    total_occurrences = sum(word_counts.values())

    if format_type.lower() == 'json':
        # 保存为JSON格式
        result_data = {
            "word_counts": word_counts,
            "sorted_words": sorted_words,
            "total_unique_words": len(word_counts),
            "total_occurrences": total_occurrences,
            "most_common_word": sorted_words[0] if sorted_words else None,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

    else:  # 默认保存为文本格式
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入标题和摘要信息
            f.write(f"单词统计结果\n")
            f.write("=" * 60 + "\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            f.write(f"不同单词数: {len(word_counts)}\n")
            f.write(f"总出现次数: {total_occurrences}\n")
            f.write("=" * 60 + "\n\n")

            # 写入每个单词及其出现次数
            f.write("单词出现频率（从高到低）:\n")
            f.write("-" * 40 + "\n")

            for i, (word, count) in enumerate(sorted_words, 1):
                percentage = (count / total_occurrences) * 100
                f.write(f"{i:3d}. {word:<20} {count:>5} 次 ({percentage:.2f}%)\n")

            # 写入统计摘要
            f.write("\n" + "=" * 60 + "\n")
            f.write("统计摘要:\n")
            f.write(f"- 最常见的单词: '{sorted_words[0][0]}' ({sorted_words[0][1]}次)\n" if sorted_words else "")
            f.write(f"- 平均每个单词出现次数: {total_occurrences/len(word_counts):.2f}\n")
            f.write("=" * 60 + "\n")

    return output_path


def print_word_counts(word_counts: Dict[str, int], top_n: Optional[int] = None):
    """
    打印单词统计结果

    Args:
        word_counts: 单词统计字典
        top_n: 只显示前N个最常见的单词（如果为None则显示全部）
    """
    if not word_counts:
        print("没有找到任何单词")
        return

    # 按词频排序（从高到低）
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    total_occurrences = sum(word_counts.values())

    print(f"\n单词统计结果（共 {len(word_counts)} 个不同单词，总计 {total_occurrences} 次出现）")
    print("=" * 60)

    # 限制显示的数量
    if top_n is not None and top_n > 0:
        sorted_words = sorted_words[:top_n]
        print(f"（显示前 {top_n} 个最常见的单词）")

    # 显示单词统计
    for i, (word, count) in enumerate(sorted_words, 1):
        percentage = (count / total_occurrences) * 100
        print(f"{i:>3}. {word:<20} {count:>5} 次 ({percentage:.2f}%)")

    # 显示统计摘要
    if sorted_words:
        print("\n" + "-" * 60)
        print(f"最常见的单词: '{sorted_words[0][0]}' (出现{sorted_words[0][1]}次)")
        print(f"平均每个单词出现次数: {total_occurrences/len(word_counts):.2f}")


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(
        description='统计文本文件中每个单词的出现次数',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s txt.txt                    # 基本使用
  %(prog)s txt.txt -c                 # 区分大小写
  %(prog)s txt.txt -t 10              # 只显示前10个
  %(prog)s txt.txt -o results.txt     # 保存到指定文件
  %(prog)s txt.txt -f json -o data.json  # 保存为JSON格式
  %(prog)s txt.txt -d ./results       # 保存到指定目录
        """
    )

    parser.add_argument('file', help='要处理的文本文件路径')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                       help='区分大小写（默认不区分）')
    parser.add_argument('-o', '--output', help='输出文件名（可选）')
    parser.add_argument('-d', '--directory', default='.',
                       help='输出目录（默认为当前目录）')
    parser.add_argument('-f', '--format', choices=['txt', 'json'], default='txt',
                       help='输出格式：txt 或 json（默认 txt）')
    parser.add_argument('-t', '--top', type=int,
                       help='只显示前N个最常见的单词')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细信息')

    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"正在处理文件: {args.file}")
            print(f"输出目录: {args.directory}")
            print(f"输出格式: {args.format}")

        # 统计单词
        word_counts = count_words_in_file(args.file, args.case_sensitive)

        if not word_counts:
            print("警告：文件中没有找到任何单词")
            return

        # 显示结果
        print_word_counts(word_counts, args.top)

        # 保存结果
        output_path = save_word_counts(
            word_counts,
            args.output,
            args.directory,
            args.format
        )

        print(f"\n结果已保存到：{output_path}")

    except FileNotFoundError as e:
        print(f"错误：{e}")
    except IOError as e:
        print(f"错误：{e}")
    except ValueError as e:
        print(f"错误：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def example_usage():
    """示例用法"""
    print("=" * 60)
    print("单词统计工具 - 使用示例")
    print("=" * 60)

    print("\n1. 基本使用:")
    print("   from word_count_fixed import count_words_in_file, save_word_counts")
    print("   word_counts = count_words_in_file('txt.txt')")
    print("   save_word_counts(word_counts, 'results.txt')")

    print("\n2. 命令行使用:")
    print("   python word_count_fixed.py txt.txt")
    print("   python word_count_fixed.py txt.txt -c -t 10")
    print("   python word_count_fixed.py txt.txt -f json -o data.json")

    print("\n3. 自定义设置:")
    print("   word_counts = count_words_in_file('txt.txt', case_sensitive=True)")
    print("   save_word_counts(word_counts, 'my_results.txt', './output', 'txt')")
    print("=" * 60)


def run_example():
    """运行示例测试"""
    print("正在运行示例测试...")
    print("-" * 60)

    try:
        # 测试文件路径
        test_file = "txt.txt"

        if not os.path.exists(test_file):
            print(f"测试文件不存在: {test_file}")
            print("请确保 txt.txt 文件存在于当前目录")
            return

        print(f"测试文件: {test_file}")
        print(f"文件大小: {os.path.getsize(test_file)} 字节")

        # 统计单词（不区分大小写）
        print("\n1. 统计单词（不区分大小写）...")
        word_counts = count_words_in_file(test_file, case_sensitive=False)

        if not word_counts:
            print("错误: 文件中没有找到任何单词")
            return

        print(f"  找到 {len(word_counts)} 个不同的单词")
        print(f"  总出现次数: {sum(word_counts.values())}")

        # 显示前10个最常见单词
        print("\n2. 显示前10个最常见单词:")
        print_word_counts(word_counts, top_n=10)

        # 保存结果
        print("\n3. 保存结果:")
        results_dir = "C:\\Users\\1\\Desktop\\11"

        # 保存为文本格式
        txt_path = save_word_counts(
            word_counts,
            output_file="word_count_fixed_results.txt",
            results_dir=results_dir,
            format_type="txt"
        )
        print(f"  文本格式: {txt_path}")

        # 保存为JSON格式
        json_path = save_word_counts(
            word_counts,
            output_file="word_count_fixed_results.json",
            results_dir=results_dir,
            format_type="json"
        )
        print(f"  JSON格式: {json_path}")

        print("\n" + "=" * 60)
        print("示例测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 如果没有命令行参数，运行示例测试
    import sys
    if len(sys.argv) == 1:
        run_example()
    else:
        # 否则运行主函数处理命令行参数
        main()