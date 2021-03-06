"""
selfingsim.common
=================

Common code used in simulations.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def get_population(simu, size, loci, info_fields='self_gen'):
    """Construct a population object."""
    return simu.Population(size=size,
                           ploidy=2,
                           loci=loci,
                           infoFields=str(info_fields))


def get_init_info(simu, field='self_gen'):
    """Zero initialize info field `field`."""
    return simu.InitInfo(0, infoFields=str(field))


def get_init_genotype_by_count(simu, nalleles):
    """
    Set genotype of inital population by equi-probable n alleles.
    """
    return (nalleles, simu.InitGenotype(prop=[1 / nalleles for _ in range(nalleles)]))


def pick_pure_hermaphrodite_parents(simu, config):
    """
    Sets up a mechanism to pick parent(s) under pure hermaphroditism.
    """
    rng = simu.getRNG()
    runif = rng.randUniform
    rint = rng.randInt
    try:
        sstar = config.sstar
        def compound_generator(pop):
            """
            Generates parents under pure hermaphroditism using a compound parameter.
            """
            npop = pop.popSize()
            while True:
                if runif() < sstar:         # uniparental
                    yield rint(npop)
                else:                   # biparental
                    first, second = rint(npop), rint(npop)
                    while first == second:
                        second = rint(npop)
                    yield [first, second]
        return compound_generator
    except KeyError:
        stilde = config.stilde
        tau = config.tau
        def fundamental_generator(pop):
            """
            Generates parents under pure hermaphroditism using fundamental parameters.
            """
            npop = pop.popSize()
            while True:
                if runif() < stilde: # proportion of self-fertilized eggs
                    if runif() < tau: # survival of a uniparental zygote (rel to a biparental z)
                        yield rint(npop)
                else:
                    first, second = rint(npop), rint(npop)
                    while first == second:
                        second = rint(npop)
                    yield [first, second]
        return fundamental_generator


def pick_androdioecious_parents(simu, config):
    """
    Sets up a mechanism to pick parent(s) under androdioecy.
    """
    rng = simu.getRNG()
    runif = rng.randUniform
    rint = rng.randInt
    try:
        sstar = config.sstar
        def compound_generator(pop):
            """
            Picks up parent(s) under androdioecy using a compound parameter.
            """
            gen = -1
            while True:
                ngen = pop.dvars().gen
                if gen != ngen:
                    # At the beginning of a generation, extract the
                    # sex-specific subpopulations from a parental
                    # population. The sex-specific subpopulations are used
                    # throughout mating events in one generation.
                    gen = ngen
                    males = pop.extractSubPops(subPops=[(0, 0)])
                    herms = pop.extractSubPops(subPops=[(0, 1)])
                    nmale = males.popSize()
                    nherm = herms.popSize()

                if runif() < sstar:         # uniparental
                    yield herms.individual(rint(nherm))
                else:                   # biparental
                    yield [males.individual(rint(nmale)), herms.individual(rint(nherm))]
        return compound_generator
    except KeyError:
        stilde = config.stilde
        tau = config.tau
        def compound_generator(pop):
            """
            Picks up parent(s) under androdioecy using fundamental parameters.
            """
            gen = -1
            while True:
                ngen = pop.dvars().gen
                if gen != ngen:
                    # At the beginning of a generation, extract the
                    # sex-specific subpopulations from a parental
                    # population. The sex-specific subpopulations are used
                    # throughout mating events in one generation.
                    gen = ngen
                    males = pop.extractSubPops(subPops=[(0, 0)])
                    herms = pop.extractSubPops(subPops=[(0, 1)])
                    nmale = males.popSize()
                    nherm = herms.popSize()

                if runif() < stilde: # proportion of self-fertlized egg
                    if runif() < tau: # survival rate of a uniparental zygote rel to a biparental z.
                        yield herms.individual(rint(nherm))
                else:                   # biparental
                    yield [males.individual(rint(nmale)), herms.individual(rint(nherm))]
        return compound_generator


def pick_gynodioecious_parents(simu, config):
    """
    Sets up a mechanism to pick up parent(s) under gynodioecy.
    """
    rng = simu.getRNG()
    runif = rng.randUniform
    rint = rng.randInt
    try:
        sstar = config.sstar
        H = config.H
        def compound_generator(pop):
            """
            Picks up parent(s) under gynodioecy using compound parameters.
            """
            gen = -1
            while True:
                ngen = pop.dvars().gen
                if gen != ngen:
                    # At the beginning of a generation, extract the
                    # sex-specific subpopulations from a parental
                    # population. The sex-specific subpopulations are used
                    # throughout mating events in one generation.
                    gen = ngen
                    h = pop.extractSubPops(subPops=[(0, 0)])
                    f = pop.extractSubPops(subPops=[(0, 1)])
                    Nh = h.popSize()
                    Nf = f.popSize()

                if runif() < sstar: # uniparental
                    yield h.individual(rint(Nh))
                else:               # biparental
                    if runif() < H: # having a hermaphroditic seed parent
                        first, second = rint(Nh), rint(Nh)
                        while first == second:
                            second = rint(Nh)
                        yield [h.individual(first), h.individual(second)]
                    else:           # female seed parent
                        yield [h.individual(rint(Nh)), f.individual(rint(Nf))]
        return compound_generator
    except KeyError:
        a = config.a
        sigma = config.sigma
        tau = config.tau
        def fundamental_generator(pop):
            """
            Picks up parent(s) under gynodioecy using fundamental parameters.
            """
            gen = -1
            while True:
                ngen = pop.dvars().gen
                if gen != ngen:
                    # At the beginning of a generation, extract the
                    # sex-specific subpopulations from a parental
                    # population. The sex-specific subpopulations are used
                    # throughout mating events in one generation.
                    gen = ngen
                    h = pop.extractSubPops(subPops=[(0, 0)])
                    f = pop.extractSubPops(subPops=[(0, 1)])
                    Nh = h.popSize()
                    Nf = f.popSize()
                    hermseed = Nh / (Nh * Nf * sigma)

                if runif() < hermseed: # hermaphroditic seed parent
                    if runif() < a: # self-pollen
                        yield h.individual(rint(Nh))
                    else: # non self-pollen
                        first, second = rint(Nh), rint(Nh)
                        while first == second:
                            second = rint(Nh)
                        yield [h.individual(first), h.individual(second)]
                else: # female seed parent
                    if runif() < tau:
                        yield [h.individual(rint(Nh)), f.individual(rint(Nf))]
        return fundamental_generator


def get_selfing_tagger(simu, field):
    class MySelfingTagger(simu.PyOperator):
        """
        Update information field to reflect selfing.

        When selfing occurred, this operator record the fact by incrementing the value
        of `field` by one.
        """

        def __init__(self, field='self_gen'):
            self.field = field.encode("utf-8")
            super(MySelfingTagger, self).__init__(func=self.record)

        def record(self, pop, off, dad, mom):
            """
            Increment the value of offspring's infofield `field` by one if it is uniparental.
            Otherwise reset the value to 0.
            """
            if mom is not None:
                off.setInfo(0, str(self.field))
            else:
                off.setInfo(dad.info(self.field) + 1, self.field)
            return True
    return MySelfingTagger(field)

def get_pure_hermaphrodite_mating(simu, r_rate, parents_chooser, size, rec_sites, field='self_gen'):
    """
    Constructs mating scheme for pure hermaphrodite with partial selfing under
    the infinite alleles model.

    A fraction, 0 <= weight <= 1, of offspring is generated by selfing, and others are
    generated by outcrossing.  In this model, there is no specific sex so that any
    individual can mate with any other individuals in a population.
    Furthermore, a parent can participate in both selfing and outcrossing.
    """

    selfing_tagger = get_selfing_tagger(simu, field)

    return simu.HomoMating(chooser=parents_chooser,
                           generator=simu.OffspringGenerator(
                               ops=[simu.Recombinator(rates=r_rate, loci=rec_sites),
                                    selfing_tagger]),
                           subPopSize=size)


def get_androdioecious_mating(simu, r_rate, parents_chooser,
                              size, sex_seq, rec_sites, field='self_gen'):
    """
    Constructs a mating operator under androdioecy.
    """

    sex_mode = (simu.GLOBAL_SEQUENCE_OF_SEX,) + sex_seq

    selfing_tagger = get_selfing_tagger(simu, field)
    return simu.HomoMating(chooser=parents_chooser,
                           generator=simu.OffspringGenerator(
                               ops=[simu.Recombinator(rates=r_rate, loci=rec_sites),
                                    selfing_tagger],
                               sexMode=sex_mode),
                           subPopSize=size)


def get_gynodioecious_mating(simu, r_rate, parents_chooser,
                             size, sex_seq, rec_sites, field='self_gen'):
    """
    Constructs a mating operator under gynodioecy.
    """

    sex_mode = (simu.GLOBAL_SEQUENCE_OF_SEX,) + sex_seq

    selfing_tagger = get_selfing_tagger(simu, field)
    return simu.HomoMating(chooser=parents_chooser,
                           generator=simu.OffspringGenerator(
                               ops=[simu.Recombinator(rates=r_rate, loci=rec_sites),
                                    selfing_tagger],
                               sexMode=sex_mode),
                           subPopSize=size)


def pure_hermaphrodite(simu, execute_func, config):
    """
    Sets up pure hermaphroditic simulation.
    """
    pop = get_population(simu=simu,
                         size=config.N,
                         loci=config.loci * config.allele_length)

    # Index of sites, after which recombinations happen.
    rec_loci = [config.allele_length * i - 1 for i in range(1, config.loci)]

    parents_chooser = simu.PyParentsChooser(
        pick_pure_hermaphrodite_parents(simu, config)
    )

    mating_op = get_pure_hermaphrodite_mating(simu,
                                              r_rate=config.r,
                                              parents_chooser=parents_chooser,
                                              size=config.N,
                                              rec_sites=rec_loci)

    execute_func(config, pop, mating_op)


def androdioecy(simu, execute_func, config):
    """
    Sets up androdioecious simulation.
    """
    N = config.N
    Nh = config.N_hermaphrodites
    pop = get_population(simu=simu,
                         size=N,
                         loci=config.loci * config.allele_length)
    sex_seq = tuple(simu.MALE for _ in xrange(N - Nh)) + tuple(simu.FEMALE for _ in xrange(Nh))

    simu.initSex(pop, sex=sex_seq)
    pop.setVirtualSplitter(simu.SexSplitter())

    # Index of sites, after which recombinations happen.
    rec_loci = [config.allele_length * i - 1 for i in range(1, config.loci)]

    parents_chooser = simu.PyParentsChooser(
        pick_androdioecious_parents(simu, config)
    )

    mating_op = get_androdioecious_mating(simu,
                                          r_rate=config.r,
                                          parents_chooser=parents_chooser,
                                          size=config.N,
                                          sex_seq=sex_seq,
                                          rec_sites=rec_loci)

    execute_func(config, pop, mating_op)



def gynodioecy(simu, execute_func, config):
    """
    Sets up gynodioecious mating.
    """
    N = config.N
    Nh = config.N_hermaphrodites
    pop = get_population(simu=simu,
                         size=N,
                         loci=config.loci * config.allele_length)
    sex_seq = tuple(simu.MALE for _ in xrange(Nh)) + tuple(simu.FEMALE for _ in xrange(N - Nh))

    simu.initSex(pop, sex=sex_seq)
    pop.setVirtualSplitter(simu.SexSplitter())

    # Index of sites, after which recombinations happen.
    rec_loci = [config.allele_length * i - 1 for i in range(1, config.loci)]

    parents_chooser = simu.PyParentsChooser(
        pick_gynodioecious_parents(simu, config)
    )

    mating_op = get_gynodioecious_mating(simu,
                                         r_rate=config.r,
                                         parents_chooser=parents_chooser,
                                         size=config.N,
                                         sex_seq=sex_seq,
                                         rec_sites=rec_loci)

    execute_func(config, pop, mating_op)
