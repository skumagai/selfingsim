"""
selfingsim.infinite_alleles
===========================

Simulation related code specific to mutational model (the infinite alleles model).
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import csv
import io
import sys

import simuOpt
simuOpt.setOptions(alleleType='long')
import simuPOP as simu
from . import common as cf
from . import utils

def get_init_genotype_by_prop(prop):
    """
    Sets up initial genotypes of initial individuals by specifying frequencies of
    alleles.
    """
    s = sum(prop)
    return (len(prop), simu.InitGenotype(prop=[p / s for p in prop]))


def get_mutation_operator(m_rate, loci, nrep, burnin, new_idx=0):
    """
    Sets up a mutation scheme under the infinite alleles model.
    """
    class MyMutator(simu.PyOperator):
        """
        A mutation operator class representing the infinite-alleles model.

        A new mutation is distinct from any other mutations already in a population.
        """
        def __init__(self):
            self.idx = list([new_idx] * loci for i in range(nrep))

            super(MyMutator, self).__init__(func=self.mutate)


        def mutate(self, pop):
            """Add mutations to organisms."""
            rng = simu.getRNG()

            dvars = pop.dvars()
            rep = dvars.rep
            gen = dvars.gen - burnin

            for i, ind in enumerate(pop.individuals()):
                for locus in range(loci):
                    for ploidy in range(2):
                        if  rng.randUniform() < m_rate[locus]:
                            ind.setAllele(self.idx[rep][locus], locus, ploidy=ploidy)
                            self.idx[rep][locus] += 1
            return True

    return MyMutator()


def get_output_operator(config, field='self_gen'):
    """
    Sets up an operator to write out simulation results (and progress).
    """
    output = config.outfile
    output_per = config.output_per
    N = config.N
    burnin = config.burnin
    ngen = config.gens

    header = [
        'replicate',
        'generation',
        'individual',
        'number of selfing',
        'chromosome'
    ] + ['locus {}'.format(i) for i in range(config.loci)]

    # For compatibility with python2.
    # csv module does not support unicode.
    delim = str("\t")
    field = str(field)

    class MyWriter(simu.PyOperator):
        """A class handling output of genetic information of the entire population."""

        def __init__(self):
            with io.open(output, utils.getmode("w")) as f:
                writer = csv.DictWriter(f, header, delimiter=delim)
                writer.writeheader()

            if output_per > 0:
                ats = [i + burnin for i in range(0, ngen, output_per)]
                super(MyWriter, self).__init__(func=self.write, at=ats)
            else:
                super(MyWriter, self).__init__(func=self.write)


        def write(self, pop):
            # In order to keep output file structure simple, all
            # information regarding to simulation such as model
            # parameters are included into each row.  This obviously
            # caused repetition of simulation-wide parameters many
            # times and excessive use of storage space.  However, I
            # consider an upside, the simplicity of the output file
            # structure, is well worth the cost.

            with io.open(output, utils.getmode("a")) as f:
                dvars = pop.dvars()
                rep = dvars.rep
                gen = dvars.gen

                writer = csv.DictWriter(f, header, delimiter=delim)

                # write genotype row by row.  Each row contains a list
                # of genes on a single chromosome.  Because simulated
                # organisms are diploid, each individual occupy two
                # (successive) rows.
                for idx, ind in enumerate(pop.individuals()):
                    selfing = ind.info(field)
                    for ploidy in range(2):
                        geno = list(ind.genotype(ploidy=ploidy))
                        writer.writerow({key: value for key, value in
                                         zip(header,
                                             [rep, gen, idx, int(selfing), ploidy] + geno)})

            return True

    return MyWriter()

def execute(config, pop, mating_op):
    """
    Executes simulations with appropriate mutation model and mating scheme.
    """

    init = config.initial_genotype

    if init[0] == 'monomorphic':
        next_idx, init_genotype_op = cf.get_init_genotype_by_count(simu, 1)
    elif init[0] == 'unique':
        next_idx, init_genotype_op = cf.get_init_genotype_by_count(simu, 2 * config.N)
    elif init[0] == 'count':
        next_idx, init_genotype_op = cf.get_init_genotype_by_count(simu, init[1])
    elif init[0] == 'frequency':
        next_idx, init_genotype_op = get_init_genotype_by_prop(init[1])

    init_info_op = cf.get_init_info(simu)

    mutation_op = get_mutation_operator(m_rate=config.m,
                                        loci=config.loci,
                                        nrep=1,
                                        burnin=config.burnin,
                                        new_idx=next_idx)

    output_op = get_output_operator(config)

    simulator = simu.Simulator(pops=pop, rep=1)

    if config.debug > 0:
        post_op = [simu.Stat(alleleFreq=simu.ALL_AVAIL, step=config.debug),
                   simu.PyEval(r"'%s\n' % alleleFreq", step=config.debug)]
    else:
        post_op = []

    if config.output_per > 0:
        post_op.append(output_op)

    simulator.evolve(
        initOps=[init_info_op, init_genotype_op],
        preOps=mutation_op,
        matingScheme=mating_op,
        postOps=post_op,
        finalOps=output_op,
        gen=config.gens + config.burnin)


def run(config):
    """
    Runs simulations under an appropriate mating scheme.
    """
    if config.mating_model == 'androdioecy':
        cf.androdioecy(simu, execute, config)
    elif config.mating_model == 'gynodioecy':
        cf.gynodioecy(simu, execute, config)
    elif config.mating_model == 'pure hermaphroditism':
        cf.pure_hermaphrodite(simu, execute, config)
    else:
        sys.exit('Unrecognized mating model: {}.'.format(config.mating_model))
