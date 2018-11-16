# Modified from pop-plot.py in Golly 3.2. 2018.

import golly as g
from glife import getminbox, rect, rccw
from glife.text import make_text

import numpy
import os
import random
import re
import sys
import time
import uuid
from scipy.io import wavfile

def write_wave(filename, data):
    # Normalize to range [-1, 1].
    # +0.5 DC isn't eliminated for non-oscillatory pattern.
    data = numpy.array(data).astype(numpy.float32)
    min_data = numpy.min(data)
    max_data = numpy.max(data)
    data = (data - min_data) / (max_data - min_data)
    wavfile.write(filename, 44100, data)

def create_name(directory=""):
    # uuid to avoid filename conflicts.
    return "{}/{}_{}_{}.wav".format(
        directory,
        re.sub("[/:,]", "-", g.getrule()),
        time.strftime("%F-%H-%M-%S"),
        uuid.uuid4().hex)

def generate_rule_sequence():
    values = [i for i in xrange(1, 9)]
    indices = random.sample(range(len(values)), random.randint(1, 4))
    return "".join([str(values[i]) for i in sorted(indices)])
    

def generate_rule(x, y, generation):
    return "{}/{}/{}:P{},{}".format(
        generate_rule_sequence(),
        generate_rule_sequence(),
        generation,
        x,
        y,
    )

def randfill(x, y):
    g.select([-int(x/2), -int(y/2), x, y])
    g.clear(0)
    g.randfill(50)
    g.select([])

def get_pop(numsteps=44100, x=256, y=256):
    if numsteps < 1:
        g.exit("numsteps must be greater than 0.")

    randfill(x, y)

    poplist = [ int(g.getpop()) ]
    extinction = sys.maxint

    rule = g.getrule()
    oldsecs = time.time()
    for i in xrange(numsteps - 1):
        if g.empty():
            extinction = int(g.getgen())
            break
        g.step()
        poplist.append( int(g.getpop()) )
        newsecs = time.time()
        if newsecs - oldsecs >= 1.0:
            oldsecs = newsecs
            g.show("Rule {}, Step {} of {}".format(rule, i+1, numsteps))

    return (poplist, extinction)

def render(length, x, y, generation):
    g.setgen("0")
    g.setalgo("Generations")
    g.setrule(generate_rule(x, y, generation))
    
    pop, extinction = get_pop(length, x, y)
    if extinction < 4410:
        g.show("Rule {} extinct at generation {}.".format(
            g.getrule(), extinction))
        with open("snd/short_lived_rules", "a") as short_lived:
            short_lived.write(g.getrule() + "\n")
        return
    with open("snd/long_lived_rules", "a") as long_lived:
        long_lived.write(g.getrule() + "\n")
    
    filename = create_name("snd")
    write_wave(filename, pop)
    
    g.show("Wave saved to " + filename)

if not os.path.exists("snd"):
    os.makedirs("snd")

for gen in xrange(2, 32):
    for _ in xrange(128):
        render(8820, 128, 128, gen)
g.show("Rendering finished.")
