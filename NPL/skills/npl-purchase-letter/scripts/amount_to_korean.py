#!/usr/bin/env python3
"""
숫자 금액을 한글 금액으로 변환하는 스크립트.
만원 단위 절사 후 한글 변환.

Usage:
    python amount_to_korean.py <금액(숫자)>
    
Examples:
    python amount_to_korean.py 722074235.74
    → 722070000 → 칠억이천이백칠만원
    
    python amount_to_korean.py 473700000
    → 사억칠천삼백칠십만원
"""

import sys
import math


DIGITS = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']
SMALL_UNITS = ['', '십', '백', '천']
BIG_UNITS = ['', '만', '억', '조', '경']


def truncate_to_man(amount: float) -> int:
    """10만원 단위로 절사 (10만원 미만 버림)"""
    return math.floor(amount / 100000) * 100000


def number_to_korean(amount: int) -> str:
    """정수 금액을 한글로 변환"""
    if amount == 0:
        return '영원'
    if amount < 0:
        return '마이너스 ' + number_to_korean(-amount)
    
    result = ''
    big_unit_index = 0
    
    while amount > 0:
        group = amount % 10000
        amount //= 10000
        
        if group > 0:
            group_str = ''
            for i, unit in enumerate(SMALL_UNITS):
                digit = group % 10
                group //= 10
                if digit > 0:
                    if digit == 1 and i > 0:
                        group_str = unit + group_str
                    else:
                        group_str = DIGITS[digit] + unit + group_str
            
            result = group_str + BIG_UNITS[big_unit_index] + result
        
        big_unit_index += 1
    
    return result + '원'


def korean_to_number(korean: str) -> int:
    """한글 금액을 숫자로 역변환 (검증용)"""
    korean = korean.replace('원', '').replace(',', '').strip()
    if korean == '영':
        return 0
    
    digit_map = {v: i for i, v in enumerate(DIGITS) if v}
    
    total = 0
    current_big = 0
    current_small = 0
    
    i = 0
    while i < len(korean):
        char = korean[i]
        
        if char in digit_map:
            current_small = digit_map[char]
            i += 1
        elif char == '십':
            current_small = current_small if current_small else 1
            current_big += current_small * 10
            current_small = 0
            i += 1
        elif char == '백':
            current_small = current_small if current_small else 1
            current_big += current_small * 100
            current_small = 0
            i += 1
        elif char == '천':
            current_small = current_small if current_small else 1
            current_big += current_small * 1000
            current_small = 0
            i += 1
        elif char == '만':
            current_big += current_small
            total += (current_big if current_big else 1) * 10000
            current_big = 0
            current_small = 0
            i += 1
        elif char == '억':
            current_big += current_small
            total += (current_big if current_big else 1) * 100000000
            current_big = 0
            current_small = 0
            i += 1
        elif char == '조':
            current_big += current_small
            total += (current_big if current_big else 1) * 1000000000000
            current_big = 0
            current_small = 0
            i += 1
        else:
            i += 1
    
    total += current_big + current_small
    return total


def format_number(amount: int) -> str:
    """숫자를 콤마 포맷으로 변환"""
    return f'{amount:,}'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python amount_to_korean.py <금액>")
        sys.exit(1)
    
    raw_amount = float(sys.argv[1])
    truncated = truncate_to_man(raw_amount)
    korean = number_to_korean(truncated)
    
    # 역변환 검증
    verified = korean_to_number(korean)
    is_valid = verified == truncated
    
    import json
    result = {
        "raw_amount": raw_amount,
        "truncated_amount": truncated,
        "formatted_amount": format_number(truncated),
        "korean_amount": korean,
        "deposit_10pct": math.floor(truncated * 0.1 / 100000) * 100000,
        "deposit_formatted": format_number(math.floor(truncated * 0.1 / 100000) * 100000),
        "verification": {
            "reverse_converted": verified,
            "is_valid": is_valid
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
