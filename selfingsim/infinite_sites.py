# standard imports
import csv
import sys

import simuOpt
simuOpt.setOptions(alleleType='binary')
import simuPOP as simu
import partial_selfing.common as cf


def get_pure_hermaphrodite_mating(r_rate, weight, size, loci, allele_length, field='self_gen'):
    """
    Construct mating scheme for pure hermaphrodite with partial selfing under the
    infinite sites model.

    A fraction, 0 <= weight <= 1, of offspring is generated by selfing, and others are
    generated by outcrossing.  In this model, there is no specific sex so that any
    individual can mate with any other individuals in a population.
    Furthermore, a parent can participate in both selfing and outcrossing.
    """
    # Index of sites, after which recombinations happen.
    rec_loci = [allele_length * i - 1 for i in range(1, loci + 1)]
    selfing = simu.SelfMating(ops = [simu.Recombinator(rates = r_rate,
                                                       loci = rec_loci),
                                     cf.MySelfingTagger(field)],
                              weight = weight)

    outcross = simu.HomoMating(chooser = simu.PyParentsChooser(generator = cf.pickTwoParents),
                               generator = simu.OffspringGenerator(
                                   ops = [simu.Recombinator(rates = r_rate,
                                                            loci = rec_loci),
                                          cf.MyOutcrossingTagger(field)]),
                               weight = 1.0 - weight)

    return simu.HeteroMating(matingSchemes = [selfing, outcross],
                               subPopSize = size)


def get_androdioecious_mating(r_rate, weight, size, sex_ratio, loci, allele_length, field='self_gen'):

    sexMode = (simu.PROB_OF_MALES, sex_ratio)

    rec_loci = [allele_length * i - 1 for i in range(1, loci + 1)]

    selfing = simu.SelfMating(ops = [simu.Recombinator(rates = r_rate,
                                                       loci = rec_loci),
                                     cf.MySelfingTagger(field)],
                              sexMode = sexMode,
                              subPops = [(0, 1)],
                              weight = weight)

    outcross = simu.RandomMating(ops = [simu.Recombinator(rates = r_rate,
                                                          loci = rec_loci)],
                                 sexMode = sexMode,
                                 weight = weight)

    return simu.HeteroMating(matingSchemes = [selfing, outcross],
                             subPopSize = size)


def get_gynodioecious_mating(r_rate, weight, size, sex_ratio, loci, allele_length, field='self_gen'):

    sexMode = (simu.PROB_OF_MALES, sex_ratio)

    rec_loci = [allele_length * i - 1 for i in range(1, loci + 1)]

    selfing = simu.SelfMating(ops = [simu.Recombinator(rates = r_rate,
                                                       loci = rec_loci)],
                              sexMode = sexMode,
                              subPops = [(0, 0)],
                              weight = weight)

    outcross = simu.RandomMating(ops = [simu.Recombinator(rates = r_rate,
                                                          loci = rec_loci)],
                                 sexMode = sexMode,
                                 weight = weight)

    return simu.HeteroMating(matingSchemes = [selfing, outcross],
                             subPopSize = size)


def get_mutation_operator(m_rate, loci, allele_length, nrep, burnin):
    class MyMutator(simu.PyOperator):
        """
        A mutation operator representing the infinite sites model.

        A new mutation occurs at a distinct site from any previous mutated sites.
        """
        def __init__(self):
            self.available = list(list(range(i * allele_length, (i + 1) * allele_length)
                                       for i in range(loci))
                                  for r in range(nrep))
            super(MyMutator, self).__init__(func = self.mutate)


        def mutate(self, pop):
            """Add mutations to organisms."""
            rng = simu.getRNG()

            dvars = pop.dvars()
            rep = dvars.rep
            gen = dvars.gen - burnin

            for i, ind in enumerate(pop.individuals()):
                for locus in range(loci):
                    for ploidy in range(2):
                        if rng.randUniform() < m_rate[locus]:
                            try:
                                idx = self.available[rep][locus].pop()
                            except IndexError:
                                if self.reclaim(pop, rep, locus):
                                    idx = self.available[rep][locus].pop()
                                else:
                                    sys.stderr.write(
                                        '[ERROR] rep={}, gen={}: available sites exhausted.\n'.
                                        format(rep, gen - burnin))
                                    return False

                            # A site is represented by 1 bit.  An
                            # ancestral state is always represented by
                            # 0, and mutated state is therefore always
                            # 1.
                            ind.setAllele(1, idx, ploidy = ploidy)
            return True


        def reclaim(self, pop, rep, locus):
            """
            Scan and reuse monomorphic sites.

            A new mutation uses up one available site/locus.  After enough mutations
            appear in a population, a simulation exhausts all sites/loci.  However,
            some of such mutations may be either extinct from or fixed in a current
            population.  Extinct mutations will never come back to the population, and
            fixed mutations likewise never returns to ancestral states.  Therefore,
            those sites occupied by such mutations can be freed and reused.  This method
            scans all sites to find monomorphic sites.  Once the monomorphic sites are
            identified, those sites are re-initialized and registered to a list of all
            available sites.
            """
            start = locus * allele_length
            raw_geno = list(pop.genotype())
            stride = loci * allele_length
            available = [loc for loc in range(start, start + allele_length)
                         if len(set(raw_geno[loc::stride])) == 1]

            if len(available) == 0:
                # Even after scanning all sites, there is no unused site.
                return False

            # Re-initialize newly freed sites by setting their values 0.
            for ind in pop.individuals():
                for site in available:
                    ind.setAllele(0, site, ploidy = 0)
                    ind.setAllele(0, site, ploidy = 1)
            self.available[rep][locus] = available


    return MyMutator()


def get_output_operator(config, field = 'self_gen'):
    output = config.outfile
    output_per = config.output_per
    N = config.N
    burnin = config.burnin
    ngen = config.gens
    loci = config.loci
    allele_length = config.allele_length

    data = ['infinite sites',
            N,
            ngen,
            config.reps,
            loci,
            config.m,
            config.s,
            config.r,
            burnin,
            config.a,
            config.tau]

    header = ['mutation model',
              'number of individuals',
              'number of generations',
              'number of replicates',
              'number of loci',
              'mutation rate',
              'selfing rate',
              'recombination rate',
              'number of burnin generations',
              'a',
              'tau']

    try:
        data.append(config.sigma)
        header.append('sigma')
    except:
        pass

    if config.model != 'pure hermaphrodite':
        data.append(config.sex_ratio)
        header.append('sex ratio')

    if config.model == 'gynodioecy':
        data.append(config.h)
        header.append('H')

    header.extend(['replicate',
                   'generation',
                   'individual',
                   'number of selfing',
                   'chromosome'] + ['locus {}'.format(i) for i in range(loci)])

    """Output genetic information of a population."""

    class MyWriter(simu.PyOperator):
        """A class handling output of genetic information of the entire population."""

        def __init__(self):

            # Allele length is the only parameter that will not be
            # printed.  This variable controls the assignment of
            # sites, which can hold polymorphic sites, and it is
            # there for strictly an implementation reason (albeit user
            # configurable).

            with open(output, 'w') as f:
                writer = csv.DictWriter(f, header)
                writer.writeheader()

            if output_per > 0:
                ats = [i + burnin for i in range(0, ngen, output_per)]
                super(MyWriter, self).__init__(func = self.write, at = ats)
            else:
                super(MyWriter, self).__init__(func = self.write)

        def write(self, pop):
            # In order to keep output file structure simple, all
            # information regarding to simulation such as model
            # parameters are included into each row.  This obviously
            # caused repetition of simulation-wide parameters many
            # times and excessive use of storage space.  However, I
            # consider an upside, the simplicity of the output file
            # structure, is well worth the cost.

            with open(output, 'a') as f:
                dvars = pop.dvars()
                rep = dvars.rep
                gen = dvars.gen - burnin

                writer = csv.DictWriter(f, header)

                # scan genotype of all individuals to identify
                # polymorphic sites.

                # convert to carray to list because I want to use
                # slice
                raw_geno = list(pop.genotype())
                stride = loci * allele_length
                poly_sites = [locus for locus in range(stride)
                              if len(set(raw_geno[locus::stride])) > 1]
                poly_sites = [[i for i in poly_sites
                               if j * allele_length <= i < (j + 1) * allele_length]
                              for j in range(loci)]
                for idx, ind in enumerate(pop.individuals()):
                    selfing = ind.info(field)
                    for ploidy in range(2):
                        geno = ind.genotype(ploidy = ploidy)
                        geno = [''.join(str(geno[site]) for site in locus)
                                for locus in poly_sites]
                        geno = [hex(int(i, 2)) for i in geno if len(i) > 0]
                        writer.writerow({key: value for key, value in
                                         zip(header,
                                             data + [rep, gen, idx, selfing, ploidy] + geno)})

            return True

    return MyWriter()


def execute(config, pop, mating_op):
    """Configure and run simulations."""

    next_idx, init_genotype_op = cf.get_init_genotype_by_count(simu, 1)
    init_info_op = cf.get_init_info(simu)

    mutation_op = get_mutation_operator(m_rate = config.m,
                                        loci = config.loci,
                                        allele_length = config.allele_length,
                                        nrep = config.reps,
                                        burnin = config.burnin)

    output_op = get_output_operator(config)

    simulator = simu.Simulator(pops = pop, rep = config.reps)

    if config.debug > 0:
        post_op = [simu.Stat(alleleFreq=simu.ALL_AVAIL, step=config.debug),
                   simu.PyEval(r"'%s\n' % alleleFreq", step=config.debug)]
    else:
        post_op = []

    if config.output_per > 0:
        post_op.append(output_op)

    simulator.evolve(
        initOps = [init_info_op, init_genotype_op],
        preOps = mutation_op,
        matingScheme = mating_op,
        postOps = post_op,
        finalOps = output_op,
        gen = config.gens + config.burnin)


def run(config):
    if config.model == 'androdioecy':
        cf.androdioecy(simu, execute, config)
    elif config.model == 'gynodioecy':
        cf.gynodioecy(simu, execute, config)
    else:
        cf.pure_hermaphrodite(simu, execute, config)
