#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共用应力核对：降额规则在某一级给的限值、一条应力对额定与降额值的判法、按器件类别与量纲挑降额规则。

共用层文件（references/shared/shared-layer.md），ASG 与 SR 两个技能里同一份字节；只用标准库，不导入任一技能的模块。
判法来自 references/shared/stress-spec.md：超过额定值不成立，在额定内但超过本级降额值是合格但有风险（应力），不超过降额值合格。
SR `derating.py` 和 ASG `audit_design_closure.py` 各自读记录、各自措辞，算数和挑规则都在这里。
"""
import math
import re

LEVELS = ('I', 'II', 'III')
RECOMPUTED = ('ratio', 'pulse_ratio')   # 应力 / 额定 ≤ 取值：门禁与审计从余量和限值重算的两种量度
OVER_RATING, STRESS_RISK, OK = 'OVER_RATING', 'STRESS_RISK', 'OK'
# 量纲 → 降额规则 parameter 里的词：挑“没点名规则的应力比较”该套哪条规则时用
DIMENSION_WORDS = {'current': ('电流',), 'voltage': ('电压',), 'power': ('功率', '功耗')}
# 同一类别有多条同量纲规则时，按器件身份（料号、值、库名）里的词区分；都不命中的归“其他…”那条
TYPE_WORDS = {'USB 母座': re.compile(r'USB', re.I),
              '器具耦合器': re.compile(r'耦合器|IEC ?60320|appliance coupler|\bC(?:5|6|7|8|13|14|15|16)\b', re.I)}


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def derated_limit(rule, level, rating):
    """The limit a rule sets at this level, or None when the measure has no single number to compare.
    A ratio of a negative rating is the allowed magnitude (R8: turn-off gate voltage)."""
    v, m = rule['values'][level], rule['measure']
    if m in ('ratio', 'pulse_ratio', 'min_ratio', 'margin_c', 'tj_percent') and not _finite(rating):
        return None
    if m in ('ratio', 'pulse_ratio', 'min_ratio'):
        rating = abs(rating)
    return {'ratio': lambda: rating * v, 'pulse_ratio': lambda: rating * v, 'min_ratio': lambda: rating * v,
            'margin_c': lambda: rating - v, 'tj_percent': lambda: (rating - 25) * v + 25,
            'max_c': lambda: v, 'max_rise_k': lambda: v, 'max_v': lambda: v, 'min_hours': lambda: v,
            'min_years': lambda: v, 'max_dvdt': lambda: v}.get(m, lambda: None)()


def verdict(stress, rating, rule, level):
    """(verdict, derated) for a stress against a guaranteed rating under a ratio rule at this level: OVER_RATING when the
    stress exceeds the rating, STRESS_RISK when it is within the rating but over the derated value, OK otherwise; None
    when the rule's measure is not a ratio or the numbers are not finite."""
    if rule['measure'] not in RECOMPUTED or level not in LEVELS or not (_finite(stress) and _finite(rating)):
        return None
    derated = derated_limit(rule, level, rating)
    if derated is None:
        return None
    rating = abs(rating)
    if stress > rating:
        return OVER_RATING, derated
    return (STRESS_RISK if stress > derated else OK), derated


def fit_rules(rules, kinds, dimension, identity=''):
    """The steady or worst-case ratio rules that fit the parts' kinds and the stress's dimension; several of one kind
    are told apart by the part's identity (TYPE_WORDS), the “其他…” rule taking a part none names. `rules` is an
    iterable of rule dicts; the result is a list, exactly one entry when the rule is settled."""
    words = DIMENSION_WORDS.get(dimension, ())
    kinds = set(kinds)
    fits = [r for r in rules if r['measure'] == 'ratio' and r['condition'] in ('worst', 'steady')
            and kinds & set(r['kinds']) and any(w in r['parameter'] for w in words)]
    if len(fits) > 1:
        named = [r for r in fits if TYPE_WORDS.get(r['type']) and TYPE_WORDS[r['type']].search(identity or '')]
        fits = named or [r for r in fits if r['type'].startswith('其他') and not any(
            TYPE_WORDS.get(o['type']) and TYPE_WORDS[o['type']].search(identity or '') for o in fits)]
    return fits
