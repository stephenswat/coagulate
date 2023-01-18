import argparse
import random
import math
import time
import numpy
import hkb_diamondsquare.DiamondSquare as DS
import matplotlib.pyplot as plt
import colour
import logging
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo


def render(
    of,
    width,
    height,
    supersample=1,
    background="#FAF9F6",
    line_width=1,
    margin=20,
    roughness=0.2,
    banding=10.0,
    distance=10,
    weight=0.8,
    density=20,
    noise=10,
    seed=None,
):
    random.seed(seed)

    img = Image.new(
        "RGBA", (supersample * width, supersample * height), color=background
    )

    nw, nh = 40, 60

    grid = DS.diamond_square(
        shape=(nw, nh), min_height=0, max_height=100, roughness=roughness, random_seed=seed,
    )

    gmin = int(numpy.min(grid))
    gmax = int(numpy.max(grid) + 1.5)

    # c1 = colour.Color("#002b81")
    # c2 = colour.Color("#81000d")

    h1 = random.uniform(0, 1)
    h2 = random.uniform(h1, 1)

    c1 = colour.Color(hue=h1, saturation=1.0, luminance=random.uniform(0.2, 0.5))
    c2 = colour.Color(hue=h2, saturation=1.0, luminance=random.uniform(0.2, 0.5))

    palette = list(c1.range_to(c2, gmax - gmin))

    noise = 10

    points = {
        (i, j): (x + random.uniform(-noise, noise), y + random.uniform(-noise, noise))
        for (i, x) in enumerate(
            (supersample * margin)
            + i * ((width - 2 * (supersample * margin)) / (nw - 1))
            for i in range(nw)
        )
        for (j, y) in enumerate(
            (supersample * margin)
            + i * ((height - 2 * (supersample * margin)) / (nh - 1))
            for i in range(nh)
        )
    }

    # create line image
    img1 = ImageDraw.Draw(img)

    for (p1k, p1) in points.items():
        reachable = set()

        queue = [(p1k, 0)]

        while queue:
            ((i1, j1), d) = queue.pop()

            reachable.add((i1, j1))

            for (i2, j2) in [(i1 - 1, j1), (i1 + 1, j1), (i1, j1 - 1), (i1, j1 + 1)]:
                if (
                    0 <= i2 < nw
                    and 0 <= j2 < nh
                    and (i2, j2) not in reachable
                    and int(grid[i1, j1] / banding) == int(grid[i2, j2] / banding)
                    and d <= distance
                ):
                    queue.append(((i2, j2), d + 1))

        p2c = [k for k in list(reachable) if k != p1k]
        p2w = [
            1.0 / abs(grid[p1k[0], p1k[1]] - grid[c[0], c[1]]) ** weight for c in p2c
        ]

        if len(p2c) == 0:
            continue

        for _ in range(density):
            p2k = random.choices(p2c, weights=p2w, k=1)[0]
            p2 = points[p2k]

            img1.line(
                [
                    (p1[0] * supersample, p1[1] * supersample),
                    (p2[0] * supersample, p2[1] * supersample),
                ],
                fill=palette[int(grid[p1k[0], p1k[1]]) - gmin].hex,
                width=(supersample * line_width) // 4,
            )

    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(of)


if __name__ == "__main__":
    run = time.time()

    for i in range(2000):
        of = "output/%d_%04d.png" % (run, i)
        rn = random.uniform(0.1, 0.7)
        bd = random.uniform(3.0, 20.0)
        ds = random.randint(2, 15)
        wt = random.uniform(0.5, 2.0)
        dt = random.randint(2, 40)
        ns = random.uniform(0, 30)

        print("Rendering %s with roughness %f, banding %f, distance %d, density %d, noise %f, and weight %f" % (of, rn, bd, ds, dt, ns, wt))

        render(
            of,
            800,
            1200,
            supersample=16,
            margin=5,
            roughness=rn,
            banding=bd,
            distance=ds,
            weight=wt,
            density=dt,
            noise=ns,
            background="#FFFFFF"
        )
