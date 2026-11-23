"""Versioned-by-Git article ordering, shared by builder and local preview."""
import argparse
import json
import os
import math
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
        if isinstance(ids, dict):
            if any(not isinstance(i, str) or not i or len(i)>200 or isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) for i,n in ids.items()):
                raise ValueError('文章编号必须为有限数字')
            if len(set(ids.values())) != len(ids):
                raise ValueError('文章编号不能重复')
            continue
        if not isinstance(ids, list) or any(not isinstance(i, str) or not i or len(i)>200 for i in ids):
            raise ValueError('文章顺序必须为非空字符串 ID 的数组')
        if len(ids) != len(set(ids)):
            raise ValueError('同一目录内存在重复文章 ID')
    return value

def load_orders(path=ORDER_FILE):
    if not path.exists():
        return {}
    return validate_orders(json.loads(path.read_text(encoding='utf-8')))

def rank_order(ids, saved):
    # Legacy arrays migrate without changing their displayed order.
    if isinstance(saved, list):
        saved = {ident: (len(saved)-i)*1024 for i, ident in enumerate(saved)}
    ranks = dict(saved)
    missing = [ident for ident in ids if ident not in ranks]
    top = max(ranks.values(), default=0)
    for ident in reversed(missing):
        top += 1024
        ranks[ident] = top
    current = sorted(ids, key=lambda ident: ranks[ident], reverse=True)
    if current == ids:
        return ranks
    # A drag moves one article; keep all other numbers unchanged.
    for moved in ids:
        if [i for i in current if i != moved] != [i for i in ids if i != moved]:
            continue
        at = ids.index(moved)
        high = ranks[ids[at-1]] if at else None
        low = ranks[ids[at+1]] if at+1 < len(ids) else None
        number = low+1024 if high is None else high-1024 if low is None else (high+low)/2
        if (high is None or number < high) and (low is None or number > low):
            ranks[moved] = number
            return ranks
    # Only bulk reorder or exhausted floating-point gaps need renumbering.
    ranks.update({ident: (len(ids)-i)*1024 for i,ident in enumerate(ids)})
    return ranks


def apply_order(ids, saved):
    if isinstance(saved, dict):
        # Building must honor stored ranks, not reinterpret source order as a drag.
        saved = sorted(saved, key=saved.get, reverse=True)

    present=set(ids)
    chosen=[i for i in dict.fromkeys(saved) if i in present]
    used=set(chosen)
    return [i for i in ids if i not in used]+chosen

def save_orders(path, patch):
    validate_orders(patch)
    combined=load_orders(path)
    for key, value in patch.items():
        combined[key] = rank_order(value, combined.get(key, {})) if isinstance(value, list) else value
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
