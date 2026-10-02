"""Build a dependency-ordered learning plan from a local JSON curriculum."""
import argparse
import json
from pathlib import Path


def plan(curriculum: dict, target: str, completed=()) -> list[dict]:
    if target not in curriculum:
        raise ValueError(f'Unknown target: {target}')
    completed = set(completed)
    if completed - curriculum.keys():
        raise ValueError('Completed skills must exist in the curriculum.')
    visiting, visited, ordered = set(), set(), []
    def visit(skill):
        if skill not in curriculum:
            raise ValueError(f'Unknown prerequisite: {skill}')
        if skill in visiting:
            raise ValueError(f'Prerequisite cycle at {skill}')
        if skill in visited:
            return
        entry = curriculum[skill]
        hours = entry.get('hours')
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or not 0 < hours < 10000:
            raise ValueError(f'Invalid effort estimate: {skill}')
        visiting.add(skill)
        for dependency in sorted(entry.get('requires', [])):
            visit(dependency)
        visiting.remove(skill)
        visited.add(skill)
        if skill not in completed:
            ordered.append({'skill': skill, 'hours': hours})
    visit(target)
    return ordered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('curriculum', type=Path)
    parser.add_argument('target')
    parser.add_argument('--completed', nargs='*', default=[])
    args = parser.parse_args()
    try:
        steps = plan(json.loads(args.curriculum.read_text()), args.target, args.completed)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    for i, step in enumerate(steps, 1):
        print(f'{i:2}. {step["skill"]:24} {step["hours"]:g} hours')
    print(f'\n{len(steps)} steps; {sum(s["hours"] for s in steps):g} estimated hours remaining.')
    print('Effort estimates come from the curriculum; they are not measured learning times.')

if __name__ == '__main__':
    main()
