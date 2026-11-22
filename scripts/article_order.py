"""Versioned-by-Git article ordering, shared by builder and local preview."""
import argparse
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ORDER_FILE = ROOT / 'site/article-order.json'

def validate_orders(value):
    if not isinstance(value, dict):
        raise ValueError('排序文件必须是“目录键: 文章 ID 数组”的 JSON 对象')
    for key, ids in value.items():
        if not isinstance(key, str) or not key or len(key) > 200:
            raise ValueError('无效目录键')
        if not isinstance(ids, list) or any(not isinstance(i, str) or not i or len(i)>200 for i in ids):
            raise ValueError('文章顺序必须为非空字符串 ID 的数组')
        if len(ids) != len(set(ids)):
            raise ValueError('同一目录内存在重复文章 ID')
    return value

def load_orders(path=ORDER_FILE):
    if not path.exists():
        return {}
    return validate_orders(json.loads(path.read_text(encoding='utf-8')))

def apply_order(ids, saved):
    present=set(ids)
    chosen=[i for i in dict.fromkeys(saved) if i in present]
    used=set(chosen)
    return chosen+[i for i in ids if i not in used]

def save_orders(path, patch):
    validate_orders(patch)
    combined=load_orders(path)
    combined.update(patch)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as f:
        temp=Path(f.name)
        json.dump(combined, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return combined

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='把浏览器导出的排序合并到仓库')
    parser.add_argument('file', type=Path)
    args=parser.parse_args()
    try:
        if not args.file.is_file():
            raise ValueError(f"文件不存在：{args.file}")
        result=save_orders(ORDER_FILE, load_orders(args.file))
    except (ValueError,OSError) as error:
        parser.exit(1, f'导入失败：{error}\n')
    print(f'已保存 {len(result)} 组目录顺序到 {ORDER_FILE}，请重新生成网页。')
