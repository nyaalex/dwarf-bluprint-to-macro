#!/bin/env python3
import PIL.Image
import sys
import os

START = (0, 255, 0)
ACTIVE = (255, 255, 255)
INACTIVE = (0, 0, 0)

UP = 'KEYBOARD_CURSOR_UP'
DOWN = 'KEYBOARD_CURSOR_DOWN'
LEFT = 'KEYBOARD_CURSOR_LEFT'
RIGHT = 'KEYBOARD_CURSOR_RIGHT'
SELECT = 'SELECT'
FAST = '_FAST'


def steps_to_macro(steps, macro_name):
    macro = macro_name + '\r\n'
    for s in steps:
        macro += f'\t\t{s}\r\n\tEnd of group\r\n'
    macro += 'End of macro\r\n'
    return macro


def get_path(a, b, directions):
    delta = b - a
    f_steps, steps = divmod(delta, 10)
    if steps > 5:
        f_steps += 1
        steps = steps - 10

    path = []
    path += [directions[f_steps < 0] + FAST] * abs(f_steps)
    path += [directions[steps < 0]] * abs(steps)

    return path


def parse_image(image: PIL.Image.Image):
    w, h = image.size
    instr = []

    last = (0, 0)
    for x in range(w):
        for y in range(h):
            tile = image.getpixel((x, y))
            if tile == START:
                last = x, y

    stamp_up = True
    for x in range(w):
        for y in range(h):
            tile = image.getpixel((x, y))

            if (tile == ACTIVE) == stamp_up:
                if tile != ACTIVE:
                    y -= 1
                lx, ly = last
                instr += get_path(lx, x, [RIGHT, LEFT])
                instr += get_path(ly, y, [DOWN, UP])
                instr.append(SELECT)
                stamp_up = not stamp_up
                last = x, y

            # if tile == ACTIVE:
            #     lx, ly = last
            #     instr += get_path(lx, x, [UP, DOWN])
            #     instr += get_path(ly, y, [LEFT, RIGHT])
            #     instr.append(SELECT)
            #     last = x, y
        if not stamp_up:
            lx, ly = last
            instr += get_path(lx, x, [RIGHT, LEFT])
            instr += get_path(ly, y, [DOWN, UP])
            instr.append(SELECT)
            stamp_up = not stamp_up
            last = x, y

    return instr


def main():
    if len(sys.argv) not in (2, 3) or not os.path.exists(sys.argv[1]):
        print(f'Usage:\n{sys.argv[0]} image_file [macro name]')
        exit(1)

    image = PIL.Image.open(sys.argv[1])
    image = image.convert('RGB')
    if len(sys.argv) == 3:
        macro_name = sys.argv[2]
    else:
        macro_name = os.path.basename(sys.argv[1]).split('.')[0]
    instr = parse_image(image)
    macro = steps_to_macro(instr, macro_name)
    open(macro_name + '.mak', 'w').write(macro)


if __name__ == '__main__':
    main()
